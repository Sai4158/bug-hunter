"""Start/stop local services, remembering only processes started by this project."""
import argparse
from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import webbrowser

import psutil
import requests

from bug_hunter.ai.ollama_provider import FAST_MODEL, OllamaProvider

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / ".bug-hunter-runtime"


@contextmanager
def control_lock():
    RUNTIME.mkdir(exist_ok=True)
    with (RUNTIME / "control.lock").open("a+b") as handle:
        if handle.tell() == 0:
            handle.write(b"0")
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt  # pylint: disable=import-error  # Windows-only branch.
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl  # pylint: disable=import-error  # Unix-only branch.
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise RuntimeError("Another start/stop is in progress. Let it finish, or cancel its terminal with Ctrl+C.") from exc
        try:
            yield
        finally:
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def read_state():
    path = RUNTIME / "state.json"
    if not path.exists():
        return {"project": str(ROOT), "processes": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("project") != str(ROOT) or not isinstance(data.get("processes"), dict):
            raise ValueError("wrong project or process list")
        return data
    except (ValueError, AttributeError) as exc:
        raise RuntimeError("Runtime state is invalid. No process will be stopped; see .bug-hunter-runtime/state.json.") from exc


def save_state(state):
    temporary = RUNTIME / "state.tmp"
    temporary.write_text(json.dumps(state, indent=2), encoding="utf-8")
    temporary.replace(RUNTIME / "state.json")


def owned_process(role, record):
    """PID alone is unsafe: also verify creation time, command, and project directory."""
    if not isinstance(record, dict) or type(record.get("pid")) is not int or record["pid"] <= 0:
        return None
    command = record.get("command")
    if not isinstance(command, list) or not all(isinstance(arg, str) for arg in command):
        return None
    if role == "app":
        if len(command) < 5 or command[1:4] != ["-m", "streamlit", "run"] or command[4] != str(ROOT / "app.py"):
            return None
    elif role == "ollama":
        if len(command) != 2 or Path(command[0]).name.lower() not in {"ollama", "ollama.exe"} or command[1] != "serve":
            return None
    else:
        return None
    try:
        process = psutil.Process(record["pid"])
        if (not process.is_running() or process.status() == psutil.STATUS_ZOMBIE
                or not math.isclose(process.create_time(), float(record["created"]), rel_tol=0, abs_tol=0.01)
                or process.cmdline() != command or Path(process.cwd()).resolve() != ROOT):
            return None
        return process
    except (psutil.Error, KeyError, TypeError, ValueError, OSError):
        return None


def stop_record(role, record):
    process = owned_process(role, record)
    if process is None:
        return
    # No taskkill-by-name or port-based kills: only this verified process tree.
    try:
        children = process.children(recursive=True)
    except psutil.NoSuchProcess:
        return
    targets = list(reversed(children)) + [process]
    for target in targets:
        try:
            target.terminate()
        except psutil.NoSuchProcess:
            pass
    _, alive = psutil.wait_procs(targets, timeout=5)
    for target in alive:
        try:
            target.kill()
            target.wait(timeout=5)
        except psutil.NoSuchProcess:
            pass


def spawn(role, command, state, env=None):
    with (RUNTIME / f"{role}.log").open("ab") as log:
        process = subprocess.Popen(command, cwd=ROOT, shell=False, stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=subprocess.STDOUT, env=env,
                                   creationflags=(subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP)
                                   if os.name == "nt" else 0,
                                   start_new_session=os.name != "nt")
    identity = psutil.Process(process.pid)
    state["processes"][role] = {"pid": process.pid, "created": identity.create_time(), "command": command}
    save_state(state)
    return process


def healthy(session, url):
    try:
        return session.get(url, timeout=2, allow_redirects=False).status_code == 200
    except requests.RequestException:
        return False


def wait_ready(process, ready, name, timeout=40):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"{name} exited during startup. Check .bug-hunter-runtime/{name.lower()}.log.")
        if ready():
            return
        time.sleep(0.25)
    raise RuntimeError(f"{name} did not become ready. Check .bug-hunter-runtime/ logs.")


def confirm(message, yes):
    if yes:
        return True
    try:
        print(message + " [y/N]", flush=True)
        return input().strip().lower() in {"y", "yes"}
    except EOFError:
        return False


def ensure_model(provider, yes):
    models, error = provider.list_models()
    if error and not models and "no local model" not in error.lower():
        raise RuntimeError(error)
    if FAST_MODEL in models:
        print(f"Local model ready: {FAST_MODEL}")
        return
    if not confirm(f"Download {FAST_MODEL} once (about 2 GB; internet and disk space required)?", yes):
        raise RuntimeError("Model download declined. Use run.bat / bash run.sh for the interface without this setup step.")
    print("Downloading local model; actual transfer progress follows...", flush=True)
    with provider.session.post(provider.base_url + "/api/pull", json={"model": FAST_MODEL, "stream": True},
                               stream=True, timeout=(5, 1800), allow_redirects=False) as response:
        response.raise_for_status()
        previous = None
        success = False
        for line in response.iter_lines():
            if not line:
                continue
            item = json.loads(line)
            if item.get("error"):
                raise RuntimeError(str(item["error"]))
            status = str(item.get("status", ""))
            total, completed = item.get("total"), item.get("completed")
            if type(total) is int and total > 0 and type(completed) is int:
                progress = min(100, max(0, completed * 100 // total))
                status += f" {progress}%"
            if status != previous:
                print(status, flush=True)
                previous = status
            success = success or item.get("status") == "success"
    if not success or FAST_MODEL not in provider.list_models()[0]:
        raise RuntimeError("The model download did not complete. Retry start to resume it.")


def start(args, state):
    provider = OllamaProvider()
    current = state["processes"].get("app")
    already_running = owned_process("app", current)
    if already_running:
        url = f"http://127.0.0.1:{state['port']}"
        if not healthy(provider.session, url + "/_stcore/health"):
            raise RuntimeError("Managed Bug Hunter is not healthy. Run stop, check its log, then retry start.")
    else:
        with socket.socket() as check:
            try:
                check.bind(("127.0.0.1", args.port))
            except OSError as exc:
                raise RuntimeError(f"Port {args.port} is occupied. Nothing was stopped. Close the old instance or choose another port.") from exc
        state["processes"].pop("app", None)
    created = []
    try:
        if not healthy(provider.session, provider.base_url + "/api/tags"):
            executable = args.ollama or shutil.which("ollama")
            if not executable:
                raise RuntimeError("Ollama is not available. Install it from https://ollama.com/download, then retry start.")
            environment = os.environ.copy()
            environment["OLLAMA_HOST"] = provider.base_url.removeprefix("http://")
            process = spawn("ollama", [executable, "serve"], state, environment)
            created.append("ollama")
            print("Starting local Ollama...", flush=True)
            wait_ready(process, lambda: healthy(provider.session, provider.base_url + "/api/tags"), "Ollama")
        else:
            print("Reusing running Ollama (native or Docker).")
            if not owned_process("ollama", state["processes"].get("ollama")):
                print("This pre-existing Ollama service will be left running by stop.")
        ensure_model(provider, args.yes)
        if already_running:
            print("Bug Hunter is already running: " + url)
            if not args.no_browser:
                webbrowser.open(url)
            return
        state["port"] = args.port
        command = [sys.executable, "-m", "streamlit", "run", str(ROOT / "app.py"),
                   "--server.address", "127.0.0.1", "--server.port", str(args.port), "--server.headless", "true"]
        process = spawn("app", command, state)
        created.append("app")
        url = f"http://127.0.0.1:{args.port}"
        wait_ready(process, lambda: healthy(provider.session, url + "/_stcore/health"), "App")
        print("Bug Hunter is running: " + url)
        print("Stop with stop.bat (Windows) or bash stop.sh (macOS/Linux).")
        if not args.no_browser:
            webbrowser.open(url)
    except BaseException:
        for role in reversed(created):
            stop_record(role, state["processes"].get(role))
            state["processes"].pop(role, None)
        save_state(state)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["start", "stop", "status"])
    parser.add_argument("--port", type=int, default=8501)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--yes", action="store_true", help="Explicitly approve the missing 3B model download.")
    parser.add_argument("--ollama", help="Path to the installed local Ollama executable.")
    args = parser.parse_args(argv)
    if not 1024 <= args.port <= 65535:
        parser.error("Port must be between 1024 and 65535.")
    try:
        with control_lock():
            state = read_state()
            if args.action == "start":
                start(args, state)
            elif args.action == "stop":
                for role in ("app", "ollama"):
                    stop_record(role, state["processes"].get(role))
                state["processes"] = {}
                save_state(state)
                print("Managed Bug Hunter processes stopped. Pre-existing Ollama/Docker services were not stopped.")
            else:
                print("Managed Bug Hunter: " + ("running" if owned_process("app", state["processes"].get("app")) else "stopped"))
        return 0
    except (RuntimeError, OSError, ValueError, requests.RequestException, psutil.Error) as exc:
        print("Bug Hunter: " + str(exc), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Start cancelled. Only newly started managed processes were cleaned up.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
