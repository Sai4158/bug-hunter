"""Replaceable subprocess boundary; a timeout is not a security sandbox."""

import math
import os
import signal
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExecutionResult:
    returncode: int | None
    stdout: str
    stderr: str
    duration: float
    timed_out: bool = False
    output_limited: bool = False


def run_process(args: list[str], cwd: Path, timeout: float) -> ExecutionResult:
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Execution timeout must be finite and positive.")
    # Do not forward project Python paths, pytest plugins, or credential variables.
    allowed = {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "HOME",
               "USERPROFILE", "LANG", "LC_ALL"}
    env = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    env.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONIOENCODING="utf-8",
               PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1")
    options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    started = time.perf_counter()
    process = subprocess.Popen(
        args, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        bufsize=0, shell=False, **options,
    )
    limit = 100_000
    buffers = [bytearray(), bytearray()]
    limited = [False, False]
    stop_reading = threading.Event()
    exceeded = threading.Event()
    read_errors = []

    def collect(stream, index):
        try:
            while not stop_reading.is_set():
                chunk = stream.read(8192)
                if not chunk:
                    break
                remaining = limit - len(buffers[index])
                buffers[index].extend(chunk[:remaining])
                if len(chunk) > remaining:
                    limited[index] = True
                    exceeded.set()
                    break
        except (OSError, ValueError) as exc:
            if not stop_reading.is_set():
                read_errors.append(exc)
        finally:
            stream.close()

    readers = [threading.Thread(target=collect, args=(stream, index), daemon=True)
               for index, stream in enumerate((process.stdout, process.stderr))]
    for reader in readers:
        reader.start()
    timed_out = False
    deadline = time.monotonic() + timeout
    while process.poll() is None or any(reader.is_alive() for reader in readers):
        if exceeded.is_set():
            break
        if time.monotonic() >= deadline:
            timed_out = True
            break
        exceeded.wait(0.01)
    output_limited = exceeded.is_set()
    if timed_out or output_limited:
        if os.name == "nt":
            try:
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                               capture_output=True, timeout=5, check=False, shell=False)
            except (OSError, subprocess.TimeoutExpired):
                process.kill()
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if process.poll() is None:
            process.kill()
    process.wait(timeout=5)
    for reader in readers:
        reader.join(timeout=1)
    stop_reading.set()
    for stream in (process.stdout, process.stderr):
        if not stream.closed:
            stream.close()
    if read_errors:
        raise OSError(f"Could not capture subprocess output: {read_errors[0]}")
    output = [bytes(buffer).decode("utf-8", errors="replace")
              + ("\n[output truncated]" if limited[index] else "")
              for index, buffer in enumerate(buffers)]
    return ExecutionResult(process.returncode, *output, time.perf_counter() - started,
                           timed_out, output_limited)
