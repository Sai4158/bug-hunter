# Bug Hunter

## AI-Assisted Python Bug Detection & Fix Validation

A SWENG 889 group-project proof of concept for finding functional Python bugs,
comparing local AI findings with Pylint, and checking proposed fixes with pytest.
It is not an automatic code-approval tool.

AI inference runs on your computer through Ollama. No API key or paid AI API is
used. Streamlit, Pylint, and pytest also run locally. Hardware and electricity
usage are not free, and model quality and speed depend on your machine.

## Get the project

Clone the standalone repository:

```bash
git clone https://github.com/Sai4158/bug-hunter.git
cd bug-hunter
```

Or open [the repository](https://github.com/Sai4158/bug-hunter), choose **Code →
Download ZIP**, and extract the entire ZIP before running anything. Open the
extracted folder containing `app.py`, `setup_env.py`, and `requirements.txt` in
VS Code. You do not need the SWENG coursework repository.

## Quick start

### Simplest Windows start / stop

Double-click **start.bat**, or run this from the project folder:

```powershell
.\start.bat
```

The helper checks Python, project packages, local Ollama, and the smaller
`qwen2.5-coder:3b` model. It then starts Streamlit in the background and opens
**http://127.0.0.1:8501**. Run Start again to reopen the existing app, not launch
a duplicate.

On the first run:

- Missing Python/Ollama can be installed for your Windows account through
  [WinGet](https://learn.microsoft.com/en-us/windows/package-manager/winget/install).
  You are asked before installation; package/source terms apply. Python 3.12 is
  selected when no suitable Python is found.
- Python packages are installed only into this project's `.venv`, and subsequent
  launches skip installation when the pinned versions already match.
- If the 3B model is missing, you are asked before its roughly **2 GB** download.
  The helper never silently downloads the larger 7B model.
- An existing native or Docker Ollama service is reused. Docker is not installed
  or required. If native Ollama is installed but stopped, the helper starts it.

Internet, disk space, and any Windows installation permissions are needed for
initial setup. If WinGet is unavailable or company policy blocks installation,
use the manual prerequisites below; the helper will report the problem honestly.

Double-click **stop.bat**, or run:

```powershell
.\stop.bat
```

Stop shuts down only processes recorded and verified as started by this helper.
It does **not** kill all Python processes, stop Docker, or shut down an Ollama
service that was already running. An Ollama server started by this helper is
stopped with the app. Browser tabs are not forcibly closed. An app launched with
the older `run.bat` is not managed by Stop; stop that terminal with **Ctrl+C**.

Optional commands:

```powershell
.\start.bat -NoBrowser
.\start.bat -Port 8502
powershell -NoProfile -ExecutionPolicy Bypass -File .\control.ps1 -Action status
```

Start refuses to take over an occupied port. `-Yes` explicitly approves the
missing-software installations and model download without asking again; leave
it off for normal interactive setup. The batch helpers permit only the bundled
PowerShell script for that invocation; they do not change your permanent
execution policy. Logs and ownership state live in the ignored
`.bug-hunter-runtime/` directory. Do not copy that state to another computer.
To change the port of an already running managed app, run Stop first, then Start
with `-Port 8502`. Otherwise Start reopens the existing instance on its current port.

### Simple macOS / Linux start / stop

After installing Python 3.11+ and native Ollama (or using your existing Docker
Ollama), run:

```bash
bash start.sh
bash stop.sh
```

These helpers prepare/check the project environment, offer the missing 3B model
download, and manage the app like their Windows counterparts. They do **not**
install operating-system packages, invoke `sudo`, or run a remote install script.
If Python or Ollama is missing, use the manual instructions below. You can use
`bash start.sh --no-browser --port 8502` or `.venv/bin/python control.py status`.

### Manual setup alternative

#### Prerequisites

- Python **3.11 or newer**, 64-bit. Python 3.12 was tested on Windows.
  Install from [python.org](https://www.python.org/downloads/). On Windows,
  enable the Python PATH option and reopen your terminal after installation.
- [Ollama](https://ollama.com/download), either its native application or the
  optional Docker setup below. Docker is not required for native Ollama.
- Internet for the first dependency/model downloads and enough memory and disk
  space for your chosen model. Once installed, analysis runs locally.

Every teammate needs their own Python environment and local model. The repository
does not include Python, virtual environments, or model weights.

#### Windows — PowerShell or Command Prompt

Run these from the downloaded project folder:

```powershell
.\setup.bat
```

This creates `.venv` and installs the pinned Python packages in
`requirements.txt`, without installing packages globally.

Start the Ollama desktop application. Download the recommended smaller model once:

```powershell
ollama pull qwen2.5-coder:3b
ollama list
```

Then start Bug Hunter:

```powershell
.\run.bat
```

Open **http://localhost:8501**. Use **Ctrl+C** in the terminal to stop Streamlit.
If the desktop application is not serving Ollama, run `ollama serve` in a
separate terminal. Do not start another server if port 11434 is already in use.

The setup helper can also install dependencies and launch in one command, once
Ollama and a model are available:

```powershell
py -3 setup_env.py --run
```

PowerShell users may alternatively use `.\run.ps1` if their script policy permits
it. No activation command or execution-policy change is required for `run.bat`.

#### macOS / Linux

From the project folder:

```bash
bash setup.sh
ollama pull qwen2.5-coder:3b
ollama list
bash run.sh
```

Start the installed Ollama application/service first, or use `ollama serve` in
another terminal. Open **http://localhost:8501** and stop Streamlit with **Ctrl+C**.

Alternatively, after installing Ollama and a model:

```bash
python3 setup_env.py --run
```

Some Linux Python installations require their distribution's `python3-venv`
package before environment creation. If setup fails, read its actual installer
error; it will not launch or claim success.

#### Check setup / manual launch

Windows:

```powershell
.\run.bat --check
.\.venv\Scripts\python.exe -m streamlit run app.py
```

macOS / Linux:

```bash
bash run.sh --check
.venv/bin/python -m streamlit run app.py
```

The launch helpers work from other directories too, because they locate their own
project folder. They warn if Ollama is offline but still allow the interface,
Pylint, and original-code tests to run. Re-run setup after dependency changes.
Do not copy a virtual environment between computers or operating systems.

## Models and local configuration

**Fast Demo** prefers the installed `qwen2.5-coder:3b` model.
**Higher Quality** prefers `qwen2.5-coder:7b`, if installed:

```bash
ollama pull qwen2.5-coder:7b
```

The Start helper downloads the 3B model only after your confirmation (or an
explicit `-Yes` / `--yes` option). The Streamlit application itself never pulls
models, and installing the optional 7B model remains a separate manual command.
Choose an installed model in the sidebar and use **Refresh Models** after a
download. CPU inference can take a minute or more. The smaller model is not as
reliable on every case; the larger model is not guaranteed to produce a correct
explanation either. Rehearse before a live demo.

The local service URL defaults to `http://localhost:11434`. If your local Ollama
uses a different port, configure `OLLAMA_BASE_URL` before launch.

Windows PowerShell:

```powershell
$env:OLLAMA_BASE_URL = "http://localhost:11434"
.\run.bat
```

macOS / Linux:

```bash
export OLLAMA_BASE_URL=http://localhost:11434
bash run.sh
```

An optional `BUG_HUNTER_MODEL` environment variable sets the initial model.
The runtime is local-only; do not point it at a hosted commercial AI service.
Streamlit binds to loopback by default. This POC does not need Streamlit Community
Cloud, user accounts, or an API key.

### Optional Docker-based Ollama

Instead of native Ollama:

```bash
docker run -d --name bug-hunter-ollama -p 127.0.0.1:11434:11434 -v bug-hunter-ollama-data:/root/.ollama ollama/ollama:latest
docker exec bug-hunter-ollama ollama pull qwen2.5-coder:3b
```

For an existing stopped container, use `docker start bug-hunter-ollama`.
Do not run native Ollama and the container on the same port. The named volume
preserves model downloads. Python/Streamlit still run through the project helpers.

## Classroom workflow

1. Load a built-in example, or paste Python code and optional tests/error context.
2. Write supplied pytest tests against the temporary `candidate` module, for
   example `from candidate import average`.
3. Acknowledge that you trust the code before enabling execution.
4. Click **Analyze Code**. Actual stages show validation, Pylint, original tests,
   one local AI analysis call, parsing, and suggested-fix validation.
5. Review the overview, AI findings, Pylint baseline, corrected code/diff, and
   before/after tests. Technical diagnostics remain separate.
6. Enable **Presentation Mode** for a larger, concise display. It does not change
   model settings or analysis behavior.

Pylint is a static-analysis baseline, not a substitute for functional tests.
AI findings are suggestions, not confirmed defects. **Fix Verified** requires
original test failures, a changed valid-Python proposal, and all unchanged supplied
tests passing on the proposal, with no errors or skipped tests. No tests means no
verified-fix claim. Passing those tests still does not prove every behavior correct.

## Evaluation and saved evidence

The controlled dataset contains **12 cases**, each with buggy source, tests,
reference source, and an intended bug category. Reference source is only a test
control; it is not sent to the model or substituted for a generated fix.

Open **Evaluation** in the sidebar to inspect real saved runs. The repository ships
unchanged October 5 development-machine results in `evaluation/recorded/`,
including unsuccessful runs. These appear as **Saved sample**, not a new benchmark
on your computer. See [recorded validation history](docs/VALIDATION.md) for measured
timings, known explanation errors, and the completed 12-case run.

JSON exports retain raw model output, test output, durations, and evidence hashes.
`evaluation/recorded/SHA256.json` protects the shipped file bytes. CSV-only legacy
runs are explicitly limited evidence. New runs go to the ignored
`evaluation/results/` folder with timestamped names; they do not overwrite shipped
evidence.

Human reviewers can mark intended-bug detection, explanation accuracy, fix
correctness, false positives, and notes. Judgments are stored separately in
`evaluation/reviews/` and tied to evidence hashes. **Unreviewed is not No or Yes**.
The dashboard does not infer AI accuracy from a passing fix.

To reproduce evaluation, use the project Python:

Windows:

```powershell
.\.venv\Scripts\python.exe -m evaluation.run_evaluation --baseline-only
.\.venv\Scripts\python.exe -m evaluation.run_evaluation --model qwen2.5-coder:3b --ai-timeout 240
```

macOS / Linux:

```bash
.venv/bin/python -m evaluation.run_evaluation --baseline-only
.venv/bin/python -m evaluation.run_evaluation --model qwen2.5-coder:3b --ai-timeout 240
```

Use `--case 02-comparison` for one case, `--model qwen2.5-coder:7b` for a
quality-model run, or `--help` for options. A full local run may take several
minutes. Preserve unsuccessful outputs too. Export results from the dashboard or
share the saved files explicitly; generated runs/reviews are not committed by
default.

## Project layout

```text
app.py                     Streamlit interface
bug_hunter/                Analysis, local AI, Pylint, pytest, and results UI
assets/                    Product styling and icon
evaluation/cases/          Controlled Python cases and tests
evaluation/recorded/       Unchanged sample evidence shipped with the repo
evaluation/results/        Your generated runs (ignored)
evaluation/reviews/        Separate human judgments (ignored)
tests/                     Project regression tests
docs/VALIDATION.md         Historical evaluation notes
AGENTS.md                  Coding-agent scope, safety, and verification guidance
setup_env.py, setup.*       Project-local dependency setup
launch.py, run.*            Portable startup and checks
control.py, control.ps1     Managed startup, ownership checks, and shutdown
start.*, stop.*             One-command start / stop helpers
requirements.txt           Pinned direct Python dependencies
```

The application remains a single local Python project. It adds no database, cloud
AI, GitHub integration, or automatic commits.

## Safety and limitations

Only run code you trust. Temporary execution directories and timeouts provide
isolation from project files, but **not a production security sandbox**. Executed
Python can access resources available to your account. Do not paste secrets or
run untrusted submissions.

Local models can invent explanations or miss bugs. Fix verification is limited to
the supplied tests. The curated dataset is small and does not establish general
AI or Pylint accuracy. Hardware, model warm-up, and background load affect timings.

## Troubleshooting

| Problem | What to do |
| --- | --- |
| Python is not found | Install Python 3.11+, then reopen the terminal. On Windows try `py -3 --version`. |
| Dependencies are missing | Run `setup.bat` or `bash setup.sh`; read any installation errors. |
| Ollama is offline | Start its application/service, confirm its local URL, then refresh models. |
| No models are listed | Explicitly pull a model using the commands above. |
| Analysis is slow | Try Fast Demo, use smaller inputs, and allow model warm-up time. |
| Port 8501 is occupied | Stop the other instance yourself, or use `start.bat -Port 8502` / `bash start.sh --port 8502`. Start will not kill an unrelated process. |
| Stop did not close my app | Stop manages only instances started with Start. For `run.bat`, `run.sh`, or a manual Streamlit launch, use Ctrl+C in that terminal. |
| Model download was declined or interrupted | Retry Start when ready. It does not claim a missing model is installed; `run.bat` / `bash run.sh` can open the interface without guided model setup. |
| WinGet is unavailable or installation is blocked | Install Python and Ollama manually using the official links above, then retry Start. First-run installation is not guaranteed on locked-down computers. |
| Tests cannot import your code | Import functions from `candidate`, not the project `app` module. |
| Existing `.venv` is incomplete | Rename it as a backup, then rerun setup. |
| Running from a downloaded ZIP fails | Extract the whole ZIP and run from the extracted project folder. |

## Development verification

Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q app.py launch.py setup_env.py control.py bug_hunter evaluation tests
.\.venv\Scripts\python.exe -m pip check
```

macOS / Linux: replace the Python path with `.venv/bin/python`.

Tests cover parsing, strict validation, subprocess execution, offline/error
handling, UI behavior, evaluation integrity, and the setup helpers. These regression
tests do not constitute a new model evaluation. See the historical validation
notes for earlier platform checks; do not assume that every platform has been
executed on every revision.

### Start / Stop helper checks (October 6, 2026)

- Windows Python 3.12: **117 passed, 0 failed**. A fresh Linux Python 3.11
  environment: **115 passed, 0 failed, 2 skipped** (Windows-only PowerShell tests).
  macOS was not executed.
- Real Windows Start → HTTP 200 health check → repeated Start (same process) →
  Stop → repeated Stop → restart passed. The pre-existing Docker Ollama service
  remained available after Stop. Start opened the browser on restart.
- Dependency checks, Python compilation, PowerShell syntax, shell syntax,
  whitespace checks, and recorded-evidence integrity passed.
- Installer consent and streamed model-download behavior were checked with mocks.
  Python and the 3B model were already installed here, so a real WinGet install or
  a fresh model download was **not** performed during this check.
- A real 3B-model boundary demo produced **2 passed / 1 failed** on original code
  and **3 passed / 0 failed** on corrected code; Fix Verified was **Yes**. Analysis
  took **140.648 seconds** on this computer. The new timestamped raw result is in
  `evaluation/results/` (ignored); all shipped historical evidence stayed unchanged.
  This validates the workflow, not guaranteed model accuracy or instant responses.

### Standalone migration checks (October 6, 2026)

- Fresh Windows Python 3.12 environment: **95 tests passed**. The setup and launch
  helpers, dependency consistency, and Python compilation were checked.
- Fresh Linux Python 3.11 environment in a temporary Docker container:
  **95 tests passed** and no broken dependencies. macOS was not executed.
- Streamlit started without an onboarding prompt; its health endpoint returned
  HTTP 200. A real browser run of the 3B boundary example showed original tests
  **2 passed / 1 failed** and corrected tests **3 passed / 0 failed**, with
  **Fix Verified: Yes**. Displayed analysis time was **2m 00s**, not instant.
- All **21 shipped raw evidence files** matched their original SHA-256 hashes.
  The Evaluation page reads these as saved samples; no model accuracy judgment
  was invented during migration.
