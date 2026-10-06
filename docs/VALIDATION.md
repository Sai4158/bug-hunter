# Recorded validation history

This is the original October 5, 2026 engineering evidence, not a claim that these
model runs were repeated during the standalone-repository migration. The historical
88-test counts below belong to that earlier revision; see the main README for the
standalone project's current verification. Recorded runs include unsuccessful results.

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
