"""Regression checks for boundary cases found during the final code review."""

import json
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from bug_hunter.ai.ollama_provider import OllamaProvider
from bug_hunter.analysis.diff_utils import source_diff
from bug_hunter.analysis.execution import run_process
from bug_hunter.analysis.test_runner import run_tests
from bug_hunter.demos import load_cases
from evaluation.storage import load_reviews, read_run

ROOT = Path(__file__).resolve().parents[1]


def test_diff_without_final_newline_keeps_changes_on_separate_lines():
    lines = source_diff("x = 1", "x = 2").splitlines()
    assert "-x = 1" in lines
    assert "+x = 2" in lines
    assert "\\ No newline at end of file" in lines


@pytest.mark.parametrize("data", [None, [], {"results": [], "evidence": [None]},
                                     {"results": [{"case_id": "one"}], "evidence": []}])
def test_invalid_saved_evidence_is_a_validation_error(tmp_path, data):
    path = tmp_path / "results-broken.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        read_run(path)


def test_non_object_review_does_not_hide_a_valid_saved_run(tmp_path):
    run = tmp_path / "results-empty.json"
    run.write_text('{"results": [], "evidence": []}', encoding="utf-8")
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    (reviews / "review-broken.json").write_text("[]", encoding="utf-8")
    accepted, issues = load_reviews(run, reviews)
    assert accepted == {}
    assert len(issues) == 1 and "review-broken.json" in issues[0]


def test_dashboard_rejects_invalid_csv_boolean_without_crashing(monkeypatch, tmp_path):
    from bug_hunter import evaluation_dashboard
    path = tmp_path / "results-broken.csv"
    path.write_text("case_id,ai_status,ai_produced_fix,ai_fix_successful,analysis_seconds\n"
                    "one,ok,maybe,False,1\n", encoding="utf-8")
    monkeypatch.setattr(evaluation_dashboard, "list_runs", lambda: [path])
    monkeypatch.setattr(OllamaProvider, "list_models", lambda self: ([], "Offline"))
    app = AppTest.from_file(str(ROOT / "app.py")).run()
    app.radio(key="workspace").set_value("Evaluation").run()
    assert not app.exception
    assert any("integrity check" in item.value for item in app.error)


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf")])
def test_nonfinite_or_nonpositive_execution_timeout_is_rejected(tmp_path, timeout):
    with pytest.raises(ValueError, match="finite.*positive"):
        run_process([sys.executable, "-c", "pass"], tmp_path, timeout)


@pytest.mark.parametrize("descriptor", [1, 2], ids=["stdout", "stderr"])
def test_process_output_limit_stops_a_noisy_child(tmp_path, descriptor):
    result = run_process([sys.executable, "-c",
                          f"import os; os.write({descriptor}, b'x' * 250000)"], tmp_path, 10)
    assert result.output_limited
    assert not result.timed_out
    assert len(result.stdout) <= 100_100
    assert len(result.stderr) <= 100_100
    assert "output truncated" in result.stdout + result.stderr


def test_process_preserves_unicode_and_drains_both_streams(tmp_path):
    result = run_process([sys.executable, "-c",
                          "import sys; print('caf\u00e9'); print('problem', file=sys.stderr)"], tmp_path, 10)
    assert result.returncode == 0
    assert result.stdout.strip() == "caf\u00e9"
    assert result.stderr.strip() == "problem"
    assert not result.timed_out and not result.output_limited


def test_invalid_output_encoding_is_displayed_without_a_crash(tmp_path):
    result = run_process([sys.executable, "-c", "import os; os.write(1, b'\\xff')"], tmp_path, 10)
    assert result.returncode == 0 and result.stdout == "\ufffd"
    assert not result.timed_out and not result.output_limited


def test_noisy_tests_cannot_verify_a_fix():
    result = run_tests("x = 1", "import os\ndef test_noisy():\n"
                       "    os.write(1, b'x' * 250000)\n    assert False\n")
    assert result.status == "error" and not result.all_passed
    assert "output" in result.message


@pytest.mark.parametrize("ai", [None, {"raw_response": []}, {"analysis": []},
                                   {"analysis": {"summary": "x", "corrected_code": None, "findings": []}}])
def test_invalid_nested_ai_evidence_is_rejected(tmp_path, ai):
    case = load_cases()[0]
    path = tmp_path / "results-broken.json"
    path.write_text(json.dumps({"results": [{"case_id": case["id"]}],
                               "evidence": [{"case": case, "report": {"ai": ai}}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="AI|response"):
        read_run(path)
