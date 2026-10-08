# Bug Hunter requirements and acceptance criteria

This is the behavioral baseline for the existing SWENG 889 proof of concept,
recorded October 8, 2026. It documents the implemented scope; it is not a claim
that every possible Python bug can be detected or repaired.

## Intent and users

As a developer or student, I want to compare local AI advice with an independent
Pylint baseline and unchanged pytest tests, so I can evaluate a proposed fix
without treating model confidence as proof. As a reviewer, I want preserved raw
results and separate human judgments so unsuccessful runs remain visible.

## Scope and non-goals

The input is a single Python source snippet, optional pytest tests importing
`candidate`, and optional expected-behavior/error context. Everything runs on the
user's computer. The POC does not provide login, a database, cloud AI, GitHub
integration, automatic commits, multi-language analysis, or a security sandbox.
It does not promise correct explanations, perfect detection, or instant CPU inference.

## Numbered acceptance criteria

### AC1 — Local interface

Starting the app shall present the Bug Hunter analysis interface and an Evaluation
workspace. Ollama being offline shall not prevent the interface from opening.

### AC2 — Input validation

Before analysis/execution, empty or syntactically invalid source shall produce a
clear validation error. Source and tests shall each accept at most 50,000
characters; supplied error context shall accept at most 20,000. Invalid pytest
syntax shall be rejected rather than executed.

### AC3 — Optional tests and context

Tests and error context shall be optional. Missing tests shall produce a not-run
test result, never a verified-fix claim. Actual original-test failures may be
included as model context; reference fixes shall not be model inputs.

### AC4 — Independent static baseline

Pylint shall analyze the original source independently and expose its messages
and availability/error state. Missing Pylint or malformed lint output shall not
be presented as zero confirmed defects.

### AC5 — Local-only AI

The provider shall accept only HTTP loopback Ollama URLs, defaulting to
`http://localhost:11434` and configurable with `OLLAMA_BASE_URL`. It shall reject
remote URLs, credentials, extra URL paths, and redirects; discovery shall exclude
cloud/remote models. Normal analysis shall make one generation request, without
proxying source through environment-configured proxies.

### AC6 — Explicit model selection

The interface shall offer locally installed models. Fast Demo shall prefer an
installed `qwen2.5-coder:3b`; Higher Quality shall prefer an installed
`qwen2.5-coder:7b`. The interface shall not download models. The Start helper shall
require approval before downloading a missing 3B model and shall not silently
download the 7B model.

### AC7 — Validated findings

AI output shall match the schema in `bug_hunter/models.py`: summary, findings,
and full corrected source. Findings shall carry title, category, severity
(`Low`, `Medium`, or `High`), explanation, why incorrect, suggested fix, and a
positive original-source line or null when unknown. Out-of-range lines and
invalid field types shall be rejected. Recovery shall extract only valid JSON,
never execute text or invent missing fields.

### AC8 — Reviewable proposals

Results shall display the proposed corrected code and a before/after unified
diff. A proposal shall not overwrite the user's source files. Invalid proposed
Python shall remain unverified with a clear warning.

### AC9 — Identical before/after tests

The same supplied tests shall run against original and proposed source in
temporary directories using the project interpreter. Actual counts, exit status,
and logs shall remain available. Execution shall have timeouts and bounded output.

### AC10 — Strict fix verification

Fix Verified shall be Yes only when the original has at least one failed test,
the proposal changes the source, and all collected corrected tests pass with
exit code zero and no failures, errors, or skips. No tests, an already-passing
original, unchanged code, exceptions, or timeouts shall not verify a repair.
This label shall not imply complete correctness or explanation accuracy.

### AC11 — Graceful AI failure

Offline Ollama, a missing model, timeout, incomplete generation, HTTP errors, or
malformed output shall show a useful AI failure state. Available Pylint and
original-test evidence shall remain visible; no AI success/fix shall be invented.

### AC12 — Honest progress and timing

The interface shall show actual analysis stages and measured elapsed time,
formatted readably. Token counts and model timings shall come from recorded
responses, not estimated speed or invented progress percentages.

### AC13 — Demo and execution consent

Built-in examples shall populate both source and tests, and Reset shall clear
inputs predictably. Executing analysis shall require the user's trusted-code
acknowledgment, even without tests. The UI shall explain that timeouts and
temporary directories are not a production security sandbox.

### AC14 — Presentation view

Presentation Mode shall adjust readability and hide advanced controls without
altering input source, tests, or the underlying analysis behavior. Results shall
separate AI findings, Pylint, proposed fix, test validation, and diagnostics.

### AC15 — Controlled evaluation

The evaluator shall contain 12 uniquely identified cases with buggy code,
unchanged tests, reference control, and intended category. It shall check that
original tests fail and reference tests pass before exporting statistics. New
runs shall retain real statuses, before/after counts, fix state, durations, and
raw AI output in timestamped CSV/JSON, including unsuccessful responses.

### AC16 — Evidence and human judgment

The dashboard shall read saved runs without requesting new AI analysis. Shipped
recorded evidence shall remain byte-identical to its hash manifest. Human
judgments shall be stored separately and tied to the exact evidence/response.
Unreviewed judgments shall not count as confirmed detection or explanation
accuracy. Heuristics and Pylint's dataset-symbol rubric shall be labeled separately.

### AC17 — Portable, scoped setup and lifecycle

Setup shall use Python 3.11+ and pinned dependencies installed only into the
project `.venv`. Windows and macOS/Linux helpers shall start/check the app,
avoid duplicates, refuse occupied ports, and stop only verified helper-owned
processes. Reused native or Docker Ollama shall be left running. OS/software
installation and model downloads shall require explicit approval where offered.

### AC18 — Repeatable repository verification

The repository shall contain automated regression tests and CI on Windows,
macOS, and Linux. CI shall verify application behavior with mocked AI, dependency
consistency, compilation, helper syntax, and recorded-evidence integrity without
downloading model weights or claiming live model accuracy. Live inference is a
separate, explicitly recorded check.

## Test plan and traceability

These are representative executable checks, not a claim of exhaustive coverage.
All references below are test function names in `tests/`.

| Criterion | Representative automated checks |
| --- | --- |
| AC1 | `test_initial_ui_survives_ollama_unavailability` |
| AC2 | `test_invalid_python_is_rejected_before_execution`, `test_invalid_pytest_input_is_a_clear_validation_error`, `test_input_limits_reject_before_tool_execution` |
| AC3 | `test_empty_tests_are_not_run`, `test_original_failure_feedback_is_observed_not_a_reference_answer` |
| AC4 | `test_real_pylint_finds_undefined_variable`, `test_missing_pylint_returns_unavailable`, `test_malformed_pylint_output_is_graceful` |
| AC5 | `test_hosted_or_ambiguous_provider_urls_are_rejected`, `test_local_model_discovery_excludes_cloud_models`, `test_exactly_one_generation_request_and_loaded_model_reuse` |
| AC6 | `test_mode_recommendations_keep_quality_and_fast_options`, `test_performance_and_presentation_settings_do_not_change_inputs`, `test_missing_selected_model_is_not_sent_to_server` |
| AC7 | `test_invalid_finding_fields_are_rejected`, `test_out_of_range_model_line_is_rejected`, `test_safe_recovery_accepts_only_a_valid_json_object` |
| AC8 | `test_diff_shows_correct_change`, `test_ui_displays_independent_before_after_evidence` |
| AC9 | `test_service_reuses_identical_tests_for_both_versions`, `test_unchanged_tests_produce_real_before_after_results`, `test_infinite_loop_is_terminated` |
| AC10 | `test_no_collected_tests_does_not_verify_a_fix`, `test_skipped_tests_do_not_verify_a_fix`, `test_passed_original_or_unchanged_code_is_not_a_verified_repair`, `test_timeout_or_error_never_verifies` |
| AC11 | `test_ollama_failure_preserves_original_test_evidence`, `test_model_timeout_is_reported`, `test_non_object_generation_response_is_a_graceful_failure` |
| AC12 | `test_real_progress_stages_preserve_identical_test_inputs`, `test_human_readable_time`, `test_request_is_local_structured_and_tracks_only_real_tokens` |
| AC13 | `test_selecting_demo_automatically_populates_both_inputs`, `test_demo_loader_and_reset_work`, `test_consent_required_even_without_tests` |
| AC14 | `test_performance_and_presentation_settings_do_not_change_inputs`, `test_ui_displays_independent_before_after_evidence` |
| AC15 | `test_dataset_has_twelve_complete_unique_cases`, `test_all_dataset_originals_fail_and_references_pass`, `test_evaluation_export_contains_real_baseline_and_no_fabricated_ai` |
| AC16 | `test_shipped_evidence_matches_original_hashes_and_validates`, `test_human_review_is_separate_hash_bound_and_raw_file_unchanged`, `test_judgements_are_tied_to_exact_saved_response`, `test_evaluation_dashboard_reads_recorded_data_without_an_ai_call` |
| AC17 | `test_setup_installs_only_in_project_environment`, `test_windows_installer_consent_and_exact_user_scope`, `test_reused_ollama_is_not_recorded_as_owned`, `test_repeated_start_does_not_launch_duplicate`, `test_occupied_port_is_not_taken_over` |
| AC18 | `test_requirements_map_every_criterion_to_existing_tests`, `test_documented_prompt_matches_runtime`, `test_shipped_evidence_matches_original_hashes_and_validates`; `.github/workflows/ci.yml` |

Run the full suite using the project Python as documented in [README](../README.md).
Separately check managed Start, repeated Start, HTTP health, Stop, restart, and
one real local-model analysis. Windows installer mocks are not a fresh installation;
CI passing on an OS is not proof that every teammate's Ollama/GPU setup works.

## Open questions and limitations

- Larger datasets and completed independent human reviews are needed before
  making general accuracy claims. Current saved responses include incorrect explanations.
- Multi-module packages, external snippet dependencies, concurrency, and a true
  untrusted-code sandbox are outside this POC's accepted scope.
- Model tags, hardware load, and warm/cold state affect reproducibility. Raw
  recorded results and their metadata remain the evidence, not a guaranteed SLA.
