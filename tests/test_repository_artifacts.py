"""Keep documented behavior, prompt, and references tied to real source/tests."""

import ast
import re
from pathlib import Path

import pytest

from bug_hunter.services import analyze_code

ROOT = Path(__file__).resolve().parents[1]


def test_requirements_map_every_criterion_to_existing_tests():
    text = (ROOT / "docs/REQUIREMENTS.md").read_text(encoding="utf-8")
    assert re.findall(r"^### AC(\d+) —", text, re.MULTILINE) == [str(i) for i in range(1, 19)]
    names = {
        node.name
        for path in (ROOT / "tests").glob("test_*.py")
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if isinstance(node, ast.FunctionDef)
    }
    rows = re.findall(r"^\| AC(\d+) \| (.+) \|$", text, re.MULTILINE)
    assert [number for number, _ in rows] == [str(i) for i in range(1, 19)]
    for number, row in rows:
        references = re.findall(r"`(test_\w+)`", row)
        assert references, f"AC{number} needs an executable check"
        assert set(references) <= names, f"AC{number} refers to a missing test"


def test_documented_prompt_matches_runtime():
    tree = ast.parse((ROOT / "bug_hunter/ai/ollama_provider.py").read_text(encoding="utf-8"))
    prompt = next(
        node.value.value for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "system" for target in node.targets)
    )
    text = (ROOT / "docs/LLM-PROMPT.md").read_text(encoding="utf-8")
    documented = re.search(r"```text\n(.*?)\n```", text, re.DOTALL).group(1)
    assert " ".join(documented.split()) == " ".join(prompt.split())


def test_local_documentation_links_resolve():
    documents = [ROOT / "README.md", ROOT / "AGENTS.md", *sorted((ROOT / "docs").glob("*.md"))]
    for path in documents:
        for link in re.findall(r"\[[^\]]+\]\(([^\s)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in link or link.startswith("#"):
                continue
            target = link.split("#", 1)[0]
            assert (path.parent / target).exists(), f"Broken link in {path.name}: {link}"


@pytest.mark.parametrize("source,error,tests,expected", [
    ("#" * 50_001, "", "", "50,000 source"),
    ("x = 1", "", "#" * 50_001, "Tests must be"),
    ("x = 1", "x" * 20_001, "", "error context"),
], ids=["source-too-long", "tests-too-long", "context-too-long"])
def test_input_limits_reject_before_tool_execution(monkeypatch, source, error, tests, expected):
    monkeypatch.setattr("bug_hunter.services.run_pylint", lambda *args: pytest.fail("must validate first"))
    with pytest.raises(ValueError, match=expected):
        analyze_code(source, error=error, tests=tests)
