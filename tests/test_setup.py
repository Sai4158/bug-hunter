import hashlib
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

import setup_env
from evaluation import storage


def fake_environment(monkeypatch, tmp_path):
    root = tmp_path / "downloaded project"
    root.mkdir()
    monkeypatch.setattr(setup_env, "ROOT", root)
    python = root / ".venv" / ("Scripts/python.exe" if setup_env.sys.platform == "win32" else "bin/python")
    def create(self, destination):
        assert destination == root / ".venv"
        python.parent.mkdir(parents=True)
        python.touch()
    monkeypatch.setattr(setup_env.venv.EnvBuilder, "create", create)
    return root, python


def test_setup_installs_only_in_project_environment(monkeypatch, tmp_path):
    root, python = fake_environment(monkeypatch, tmp_path)
    calls = []
    monkeypatch.setattr(setup_env.subprocess, "run", lambda args, **kwargs:
                        calls.append((args, kwargs)) or SimpleNamespace(returncode=0))
    assert setup_env.main([]) == 0
    assert [call[0][0] for call in calls] == [str(python)] * 3
    assert calls[1][0][-2:] == ["-r", str(root / "requirements.txt")]
    assert calls[2][0][1:] == ["-m", "pip", "check"]
    assert all(call[1]["cwd"] == root and call[1]["shell"] is False for call in calls)
    assert not any("ollama" in str(call[0]) for call in calls)


def test_setup_run_launches_with_project_python(monkeypatch, tmp_path):
    root, python = fake_environment(monkeypatch, tmp_path)
    calls = []
    monkeypatch.setattr(setup_env.subprocess, "run", lambda args, **kwargs:
                        calls.append((args, kwargs)) or SimpleNamespace(returncode=0))
    assert setup_env.main(["--run"]) == 0
    assert calls[-1][0] == [str(python), str(root / "launch.py")]
    assert calls[-1][1]["shell"] is False


def test_setup_failure_does_not_claim_success_or_launch(monkeypatch, tmp_path, capsys):
    _, python = fake_environment(monkeypatch, tmp_path)
    calls = []
    def run(args, **kwargs):
        calls.append(args)
        if "install" in args:
            raise subprocess.CalledProcessError(1, args)
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(setup_env.subprocess, "run", run)
    assert setup_env.main(["--run"]) == 1
    assert len(calls) == 2 and calls[0][0] == str(python)
    assert "Setup complete." not in capsys.readouterr().out


def test_setup_rejects_old_python_without_changing_environment(monkeypatch):
    monkeypatch.setattr(setup_env.sys, "version_info", (3, 10, 0))
    monkeypatch.setattr(setup_env.venv.EnvBuilder, "create", lambda *args: pytest.fail("must not create environment"))
    assert setup_env.main([]) == 1


def test_saved_samples_and_local_runs_are_both_discovered(monkeypatch, tmp_path):
    local, recorded = tmp_path / "results", tmp_path / "recorded"
    local.mkdir()
    recorded.mkdir()
    local_run = local / "results-20261006.json"
    saved_run = recorded / "results-20261005.json"
    local_run.touch()
    saved_run.touch()
    saved_run.with_suffix(".csv").touch()
    monkeypatch.setattr(storage, "RESULTS", local)
    monkeypatch.setattr(storage, "RECORDED", recorded)
    assert storage.list_runs(local) == [local_run, saved_run]
    assert storage.list_runs(recorded) == [saved_run]


def test_shipped_evidence_matches_original_hashes_and_validates():
    recorded = Path(__file__).resolve().parents[1] / "evaluation" / "recorded"
    hashes = json.loads((recorded / "SHA256.json").read_text(encoding="utf-8"))
    assert len(hashes) == 21
    for name, expected in hashes.items():
        path = recorded / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
        if path.name.startswith("results-"):
            storage.read_run(path)
