# Recorded validation history

The October 5, 2026 engineering evidence below is preserved, not a claim that
those model runs were repeated during standalone migration. Historical test
counts belong to their respective revisions. New October 8 verification appears
in a separate section at the end. Recorded runs include unsuccessful results.

## Recorded validation

Earlier evidence remains unchanged, including the original three-case 7B success run
`evaluation/recorded/results-20261005T023013283794Z.json` and unsuccessful smaller-model attempts.
Those three fixes passed all nine unchanged tests, but some explanations were contradictory:
human judgments remain Unreviewed, not an AI accuracy claim.

Second-pass results, actual timing comparisons, full-dataset status, unit tests, and OS
verification are recorded in the following final validation notes.

### Second-pass checks (October 5, 2026)

- Windows Python 3.12: **88 passed, 0 failed**. Linux Python 3.11 in a temporary,
  read-only-project Docker container: **88 passed, 0 failed**. macOS was not executed.
- Compilation, dependency consistency, PowerShell/batch setup checks, Linux shell syntax,
  and project-wide whitespace checks passed. Streamlit startup health returned HTTP 200.
- A real browser exercised demo loading, progress, Presentation Mode, results, and the
  saved-evaluation dashboard. Menu/deploy controls are hidden; sidebar controls remain.
- An actual disconnected-endpoint check retained real Pylint results and original tests
  (2 passed / 1 failed) without fabricating AI guidance or claiming a verified fix.
- All nine pre-existing CSV/JSON evidence files remained byte-identical (SHA-256).
  No model output or dataset/reference source was repaired by hand.
- No known credential patterns, source-level machine-specific paths, or nested repositories
  were found. Virtual environments, caches, results, and human reviews remain ignored.

### Measured before / after

The same three original live-demo cases were measured before source changes and after
optimization. Values below are **application analysis seconds**, excluding the evaluation
reference control. Every cell is a real run, not a projected improvement.

| Case | Before: 7B | After: 7B | After: 3B | 3B fix verified? |
| --- | ---: | ---: | ---: | --- |
| Off-by-One Average | 160.94 | 107.54 | 35.16 | No — 2 tests still failed |
| Incorrect Boundary Comparison | 43.87 | 54.75 | 25.54 | Yes — 3/3 passed |
| Impossible Weekend Condition | 43.36 | 67.07 | 33.93 | Yes — 3/3 passed |

All three listed 7B fixes passed their tests. **7B did not get faster consistently**;
3B reduced measured wait time but did not preserve all model-level fix successes.
The independent validator remained strict and correctly rejected the incomplete average fix.
These are single observations with different cold/warm/memory conditions, not statistical
benchmarks. The before run overlapped the explicit model download; part of the 7B run
overlapped automated checks. Do not attribute every difference to prompt optimization.

Exact sources (CSV companions also exist):

- Before: `evaluation/recorded/results-20261005T034324412824Z.json`
- Final 3B three-case trial: `evaluation/recorded/results-20261005T040823879233Z.json`
- Full optimized 7B run: `evaluation/recorded/results-20261005T042255306397Z.json`

The full 7B run attempted/completed **12/12 cases**: 12 schema-valid responses, 12 proposed
source changes, and **12 pytest-verified fixes** (31 unchanged tests passed). Mean evaluation
case time was **69.85 seconds**, including the reference control. Pylint raised the intended
functional symbol on **1/12** under the existing dataset rubric, not a universal detection score.
All human intended-bug/explanation judgments remain **Unreviewed**. In the average case, for
example, the explanation described a changed divisor even though the actual bug was a loop
boundary. Passing corrected tests did not make that explanation correct.

The first shortened-prompt trial emitted invalid line-numbered Python; the subsequent small
model trial also missed cases. Both timestamped raw runs are retained. The final prompt uses
plain source and real original failures; it never substitutes a reference fix or retries until
success. For live class use, rehearse the chosen model/cases and allow CPU waiting time.

Two additional real browser runs of the 3B boundary demo verified the fix: the cold run
displayed **1m 28s**, with **28.515 seconds model loading**; the immediately repeated warm
run displayed **51s**, with **0.004 seconds model loading**. Generation still took
26.400/31.023 seconds respectively. The warm response explained the boundary correctly;
the cold response incorrectly discussed `is` versus `==`, despite passing corrected tests.
These unedited browser observations are retained in `evaluation/recorded/smoke/ui-cold-3b.json`
and `ui-warm-3b.json` and are labeled as UI captures, not reconstructed API exports.

Readiness: the local POC is usable for a **rehearsed, human-reviewed classroom demo**.
It is not consistently an instant-response demo on this CPU. Prepare the model in advance,
close unnecessary applications when memory is tight, and show saved runs explicitly as
recorded evidence if live inference is too slow. Finish human judgments before claiming
intended-bug detection or explanation accuracy. No commits or pushes were made during that historical validation pass.

## Repository completion checks — October 8, 2026

The application implementation, evaluation cases, and all 21 shipped raw evidence
files remain unchanged from the pre-audit revision. This pass added requirements
traceability, architecture, prompt documentation, references, real dated GitHub
planning records, optional Compose, and CI; it did not rebuild the working POC.

### Automated checks

- Windows local Python 3.12: **123 passed, 0 failed**, including six new
  documentation/input-limit cases. Last full local run took **49.04 seconds**.
- Actual [successful GitHub Actions run](https://github.com/Sai4158/bug-hunter/actions/runs/37754034593),
  commit `65de6b4`: Windows Python 3.12 **123 passed**; macOS Python 3.12
  **123 passed**; Linux Python 3.12 **121 passed, 2 skipped**; Linux Python 3.11
  **121 passed, 2 skipped**. Linux skips are Windows PowerShell installer mocks.
- CI compilation, package consistency, helper syntax, and recorded-evidence
  checks passed. These are mocked-AI regression checks, not live model benchmarks.
  Native Ollama inference/startup on macOS and Linux was not exercised in CI.
- The [initial CI run](https://github.com/Sai4158/bug-hunter/actions/runs/37753750175)
  failed in all four jobs on one default-URL assertion: the new workflow had set
  `OLLAMA_BASE_URL` to an unused port. The conflicting workflow override was
  removed; the application and test assertion were not changed to hide failure.
- Local compile, `pip check`, PowerShell syntax, and `git diff --check` passed.
  The repository scan found no known credential patterns, machine-specific source
  paths, nested repositories, or tracked caches/runtime/generated results.
  Pattern scanning is not a guarantee that every possible secret is detectable.

### Real local operation

- Managed Start, repeated Start, HTTP 200 health, Stop, repeated Stop, and restart
  passed on Windows. The pre-existing Docker Ollama was left running. No real
  WinGet installation or fresh model-weight download was needed on this machine.
- An isolated optional Compose service using official Ollama **0.34.0** became
  healthy on loopback port **11436**, returned `/api/version`, and listed an empty
  model store. The temporary container/network/empty volume were removed afterward;
  no shared service or model volume was removed. Compose does not download weights.
- Real 3B evaluation of `02-comparison`: original **2 passed / 1 failed**;
  AI-corrected **3 passed / 0 failed**; **Fix Verified: Yes**. Service time was
  **62.564 seconds**, or **63.184 seconds** including the evaluation control.
  Raw evidence is retained locally in
  `evaluation/results/results-20261008T090106160513Z.json` and its CSV companion
  (ignored, not a replacement for shipped evidence).
- Its explanation incorrectly claimed the original used `is` instead of `==`;
  the actual source was `age > 18`, and the generated fix used `age >= 18`.
  The response is preserved unchanged. Detection/explanation judgments remain
  **Unreviewed**, not automatically marked correct because the fix passed tests.
- A separate real browser run of the boundary example displayed one AI finding,
  two Pylint messages, **Fix Verified: Yes**, and **46s**. Example population,
  execution consent, progress, and the Evaluation dashboard were exercised.
  The built-in in-app browser was unavailable; these checks used the standalone
  test browser. This browser observation is not a fabricated raw API export.

The repository is usable for a rehearsed local POC demo. Independent human review
is still needed before making accuracy claims; [issue 4](https://github.com/Sai4158/bug-hunter/issues/4)
tracks that limitation explicitly. Older failures and timings remain intact.
