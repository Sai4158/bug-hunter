# Bug Hunter contributor guidance

## Project scope

This repository is the standalone SWENG 889 Python bug-detection proof of concept.
Keep changes focused on the user's request and preserve working features. Do not
modify unrelated coursework or neighboring projects. Do not commit, push, publish,
or download models unless the user requests or approves that action.

Read `README.md` before changing setup, launch, or evaluation behavior. Update it
when commands or requirements change. Keep this guide aligned with the actual code.

## Responsibilities

- `app.py`: Streamlit inputs, trusted-code acknowledgement, and progress display.
- `bug_hunter/services.py`: coordinates Pylint, original tests, one normal AI
  analysis call, and corrected-code validation.
- `bug_hunter/ai/ollama_provider.py`: local Ollama requests and response validation.
- `bug_hunter/analysis/`: subprocess execution, Pylint, pytest, and comparisons.
- `bug_hunter/presentation.py` and `assets/`: results display and product styling.
- `evaluation/`: controlled cases, actual measurements, and separate human review.
- `setup_env.py` and `setup.*`: project-local Python dependency installation.
- `launch.py` and `run.*`: foreground launch/checks; offline Ollama is a warning.
- `control.py`, `control.ps1`, `start.*`, and `stop.*`: managed service lifecycle.
- `docs/REQUIREMENTS.md`: AC1–AC18 and test traceability; keep expected behavior explicit.
- `docs/ARCHITECTURE.md`, `docs/LLM-PROMPT.md`: actual components and runtime prompt/settings.
- `docs/REFERENCES.md`, `docs/PROJECT-TRACKING.md`: attribution and genuine GitHub planning links.
- `.github/workflows/ci.yml`: mocked-AI regression CI across Windows/macOS/Linux.
- `compose.ollama.yml`: optional loopback-only Ollama; the app still uses native Python.

## Setup and service lifecycle

Use Python 3.11+ and install packages only in the project's `.venv` from the pinned
`requirements.txt`. Do not copy virtual environments between machines. Use
`pathlib`, `sys.executable`, and subprocess argument lists; avoid machine-specific
paths and shell-built commands.

Windows: `start.bat` checks prerequisites, offers missing Python/Ollama installation
through WinGet with consent, and offers the missing `qwen2.5-coder:3b` download.
`stop.bat` stops only processes this helper started and verified. macOS/Linux:
`bash start.sh` and `bash stop.sh`; OS-level Python/Ollama installation is manual.
`run.bat` / `bash run.sh` remain foreground alternatives, stopped with Ctrl+C.

Reuse an existing native or Docker Ollama service. Never kill processes by name or
occupied port, stop shared Docker services, or weaken PID/creation-time/command/CWD
ownership checks. Never silently install software, download the 7B model, or change
the machine's permanent PowerShell execution policy. Runtime ownership/log files
belong only in the ignored `.bug-hunter-runtime/` directory.

## Safety and research integrity

- AI inference must remain local through Ollama, with `OLLAMA_BASE_URL` defaulting
  to `http://localhost:11434` and the provider's HTTP-loopback validation retained.
  Do not introduce cloud AI APIs, credentials, paid services, or public exposure.
- Keep the trusted-code acknowledgement. Temporary directories and timeouts are
  not a production security sandbox; execute only code approved for this purpose.
- Run the identical supplied tests against original and corrected code. Never
  change tests, inject reference fixes, or relax verification to manufacture success.
- Preserve raw successes, failures, timings, and explanations. A pytest-verified
  fix is not proof of explanation accuracy or intended-bug detection.
- Do not overwrite `evaluation/recorded/` or its `SHA256.json` evidence manifest.
  Write new runs to `evaluation/results/` and human judgments to
  `evaluation/reviews/`, separately and linked to their actual evidence.
- Keep generated results/reviews, runtime state, caches, `.venv`, and secrets
  ignored. Never force-add them. Report limitations and unexecuted checks honestly.

## Verification

Run from the project root with the project interpreter. Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q app.py launch.py setup_env.py control.py bug_hunter evaluation tests
.\.venv\Scripts\python.exe -m pip check
git diff --check
```

On macOS/Linux, use `.venv/bin/python`. Regression tests must not require a live
model or depend on port 8501 being free; isolate unit-test network/process effects.
Check PowerShell/shell syntax when editing launch helpers. For lifecycle changes,
also test Start, repeated Start, health, Stop, and restart without disturbing shared
services. Run live inference only when appropriate and retain its real evidence.

Report exact test results and which operating systems were actually exercised.
Keep historical validation counts intact and add dated new results separately.
Before an authorized commit, inspect staged files and check for secrets/artifacts.
Push only to the user's intended repository and never force-push without approval.
Keep docs, acceptance-criterion mappings, runtime prompt, and README commands aligned.
CI is not a live-model evaluation. Do not backdate planning records or fabricate
incremental history. Preserve prior counts and all recorded evidence. CI test
reports belong in ignored `test-results/`, not in commits.
