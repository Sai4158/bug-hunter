from contextlib import nullcontext
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace

import psutil
import pytest

import control
import setup_env


@pytest.fixture
def runtime(monkeypatch, tmp_path):
    root = tmp_path / "project with spaces"
    root.mkdir()
    folder = root / ".bug-hunter-runtime"
    folder.mkdir()
    monkeypatch.setattr(control, "ROOT", root)
    monkeypatch.setattr(control, "RUNTIME", folder)
    return folder


def identity(role="app"):
    command = ["python", "-m", "streamlit", "run", str(control.ROOT / "app.py")]
    if role == "ollama":
        command = ["ollama", "serve"]
    return {"pid": 123, "created": 100.0, "command": command}


def process_for(record, **changes):
    values = {"is_running": lambda: True, "status": lambda: psutil.STATUS_RUNNING,
              "create_time": lambda: record["created"], "cmdline": lambda: record["command"],
              "cwd": lambda: str(control.ROOT)}
    values.update(changes)
    return SimpleNamespace(**values)


def test_state_round_trip_and_wrong_project_is_rejected(runtime):
    state = control.read_state()
    state["processes"]["app"] = identity()
    control.save_state(state)
    assert control.read_state() == state
    state["project"] = "another project"
    control.save_state(state)
    with pytest.raises(RuntimeError, match="invalid"):
        control.read_state()


def test_corrupt_state_does_not_stop_any_process(runtime, monkeypatch):
    (runtime / "state.json").write_text("not JSON")
    monkeypatch.setattr(control, "stop_record", lambda *args: pytest.fail("must not stop"))
    assert control.main(["stop"]) == 1


def test_verified_process_matches_all_identity_fields(runtime, monkeypatch):
    record = identity()
    process = process_for(record)
    monkeypatch.setattr(control.psutil, "Process", lambda pid: process)
    assert control.owned_process("app", record) is process


@pytest.mark.parametrize("change", ["pid_reused", "command_changed", "different_directory", "zombie", "nan_timestamp"])
def test_stale_or_unrelated_process_is_never_owned(runtime, monkeypatch, change):
    record = identity()
    actual = identity()
    overrides = {}
    if change == "pid_reused":
        overrides["create_time"] = lambda: 101.0
    elif change == "command_changed":
        overrides["cmdline"] = lambda: ["python", "unrelated.py"]
    elif change == "different_directory":
        overrides["cwd"] = lambda: str(control.ROOT.parent)
    elif change == "zombie":
        overrides["status"] = lambda: psutil.STATUS_ZOMBIE
    else:
        record["created"] = float("nan")
    monkeypatch.setattr(control.psutil, "Process", lambda pid: process_for(actual, **overrides))
    assert control.owned_process("app", record) is None


def test_forged_command_and_unknown_role_are_not_stopped(runtime, monkeypatch):
    monkeypatch.setattr(control.psutil, "Process", lambda pid: pytest.fail("must not inspect unrelated PID"))
    record = identity()
    record["command"] = ["python", "unrelated.py"]
    control.stop_record("app", record)
    control.stop_record("unknown", identity())


def test_stop_only_terminates_verified_tree(runtime, monkeypatch):
    events = []
    child = SimpleNamespace(terminate=lambda: events.append("child"))
    parent = SimpleNamespace(children=lambda recursive: [child], terminate=lambda: events.append("parent"))
    monkeypatch.setattr(control, "owned_process", lambda *args: parent)
    monkeypatch.setattr(control.psutil, "wait_procs", lambda targets, timeout: (targets, []))
    control.stop_record("app", identity())
    assert events == ["child", "parent"]


def test_stop_with_no_owned_services_is_idempotent(runtime, monkeypatch):
    calls = []
    monkeypatch.setattr(control, "stop_record", lambda role, record: calls.append((role, record)))
    assert control.main(["stop"]) == 0
    assert control.main(["stop"]) == 0
    assert calls == [("app", None), ("ollama", None)] * 2
    assert control.read_state()["processes"] == {}


def test_missing_model_requires_consent_and_never_posts(monkeypatch):
    provider = SimpleNamespace(list_models=lambda: ([], "Ollama is running, but no local model is installed."))
    monkeypatch.setattr("builtins.input", lambda: "no")
    with pytest.raises(RuntimeError, match="declined"):
        control.ensure_model(provider, False)


def test_existing_fast_model_needs_no_prompt_or_download(monkeypatch):
    provider = SimpleNamespace(list_models=lambda: ([control.FAST_MODEL], None))
    monkeypatch.setattr("builtins.input", lambda: pytest.fail("must not prompt"))
    control.ensure_model(provider, False)


def test_streamed_pull_requires_success_and_model_verification(monkeypatch):
    posts = []
    class Response:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def raise_for_status(self):
            pass
        def iter_lines(self):
            return iter([b'{"status":"pulling layer","total":100,"completed":50}', b'{"status":"success"}'])
    def post(url, **kwargs):
        posts.append((url, kwargs))
        return Response()
    lists = iter([([], "Ollama is running, but no local model is installed."), ([control.FAST_MODEL], None)])
    provider = SimpleNamespace(base_url="http://localhost:11434", list_models=lambda: next(lists),
                               session=SimpleNamespace(post=post))
    control.ensure_model(provider, True)
    assert posts[0][0] == "http://localhost:11434/api/pull"
    assert posts[0][1]["json"]["model"] == control.FAST_MODEL
    assert posts[0][1]["allow_redirects"] is False


def test_failed_pull_is_not_claimed_as_complete(monkeypatch):
    class Response:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def raise_for_status(self):
            pass
        def iter_lines(self):
            return iter([b'{"error":"disk full"}'])
    provider = SimpleNamespace(base_url="http://localhost:11434", list_models=lambda: ([], None),
                               session=SimpleNamespace(post=lambda *a, **kw: Response()))
    with pytest.raises(RuntimeError, match="disk full"):
        control.ensure_model(provider, True)


def fake_start(monkeypatch, runtime, owned=False):
    provider = SimpleNamespace(base_url="http://localhost:11434", session=object())
    monkeypatch.setattr(control, "OllamaProvider", lambda: provider)
    monkeypatch.setattr(control, "owned_process", lambda role, record: object() if role == "app" and owned else None)
    monkeypatch.setattr(control, "healthy", lambda *args: True)
    monkeypatch.setattr(control, "ensure_model", lambda *args: None)
    monkeypatch.setattr(control, "wait_ready", lambda *args: None)
    monkeypatch.setattr(control.socket, "socket", lambda:
                        nullcontext(SimpleNamespace(bind=lambda address: None)))
    monkeypatch.setattr(control.webbrowser, "open", lambda *args: pytest.fail("browser disabled"))
    return SimpleNamespace(port=8501, ollama=None, yes=False, no_browser=True)


def test_reused_ollama_is_not_recorded_as_owned(runtime, monkeypatch):
    args = fake_start(monkeypatch, runtime)
    roles = []
    monkeypatch.setattr(control, "spawn", lambda role, *args: roles.append(role) or object())
    control.start(args, {"project": str(control.ROOT), "processes": {}})
    assert roles == ["app"]


def test_repeated_start_does_not_launch_duplicate(runtime, monkeypatch):
    args = fake_start(monkeypatch, runtime, owned=True)
    monkeypatch.setattr(control, "spawn", lambda *args: pytest.fail("must not spawn duplicate"))
    control.start(args, {"port": 8501, "processes": {"app": identity()}})


def test_start_failure_rolls_back_only_new_processes(runtime, monkeypatch):
    args = fake_start(monkeypatch, runtime)
    roles = []
    monkeypatch.setattr(control, "spawn", lambda *args: object())
    monkeypatch.setattr(control, "stop_record", lambda role, record: roles.append(role))
    monkeypatch.setattr(control, "wait_ready", lambda *args: (_ for _ in ()).throw(RuntimeError("failed startup")))
    with pytest.raises(RuntimeError, match="failed startup"):
        control.start(args, {"project": str(control.ROOT), "processes": {}})
    assert roles == ["app"]


def test_occupied_port_is_not_taken_over(runtime, monkeypatch):
    args = fake_start(monkeypatch, runtime)
    class Socket:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def bind(self, address):
            raise OSError("occupied")
    monkeypatch.setattr(control.socket, "socket", Socket)
    monkeypatch.setattr(control, "spawn", lambda *args: pytest.fail("must not spawn"))
    with pytest.raises(RuntimeError, match="occupied"):
        control.start(args, {"processes": {}})


def test_dependency_check_does_not_install_or_create_environment(monkeypatch, tmp_path):
    monkeypatch.setattr(setup_env, "ROOT", tmp_path)
    (tmp_path / "requirements.txt").write_text("example==1.0\n")
    monkeypatch.setattr(setup_env, "version", lambda name: "1.0")
    monkeypatch.setattr(setup_env.subprocess, "run", lambda *a, **kw: pytest.fail("must not run installer"))
    assert setup_env.main(["--check"]) == 0
    assert not (tmp_path / ".venv").exists()
    monkeypatch.setattr(setup_env, "version", lambda name: "0.9")
    assert setup_env.main(["--check"]) == 1


@pytest.mark.skipif(not shutil.which("powershell"), reason="Windows PowerShell is not installed")
@pytest.mark.parametrize("approved", [False, True])
def test_windows_installer_consent_and_exact_user_scope(approved):
    script = str(Path(control.__file__).with_suffix(".ps1")).replace("'", "''")
    approval = "$true" if approved else "$false"
    command = f"""
. '{script}'
$Yes = {approval}
function winget {{
    $actual = $args -join ' '
    if ($actual -ne 'install --id Ollama.Ollama --exact --source winget --scope user --silent --no-upgrade --accept-package-agreements --accept-source-agreements') {{ throw 'Incorrect install options' }}
    $global:LASTEXITCODE = 0
    Write-Output 'Mock installer called; no software installed.'
}}
function Read-Host {{ return 'no' }}
try {{
    Install-Prerequisite 'Ollama.Ollama' 'Ollama'
    if (-not $Yes) {{ throw 'Installer must be declined' }}
}} catch {{
    if ($Yes -or $_.Exception.Message -notmatch 'declined') {{ Write-Error $_; exit 1 }}
}}
exit 0
"""
    completed = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                               capture_output=True, text=True, shell=False, timeout=30)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert ("Mock installer called" in completed.stdout) is approved
