# Task 4 — control traceability

Controls are traced to snapshots and existing tests. Test names identify specific checks, not whole-category certification. Recorded logs and version binding are in the evidence register. No fresh app or Task-3 test execution occurred in Task 4.

## CTRL01 — Restrict the browser-facing service to the intended local origin and mutation token.

Historical demo identifier: `DEMO-v2:SEC-01`. Status: implemented with bounded evidence.

Loopback bind; exact Host/Origin and Fetch-Site checks; constant-time request-token comparison.

Code references:

- [app/server.py](sources/app/server.py) — `Server.__init__`, line 114.
- [app/server.py](sources/app/server.py) — `Handler.guard`, line 137.

Existing test references:

- [app/tests/test_live.py](sources/app/tests/test_live.py) — `HTTPTests.test_bad_host`, line 25.
- [app/tests/test_live.py](sources/app/tests/test_live.py) — `HTTPTests.test_bad_origin`, line 26.
- [app/tests/test_live.py](sources/app/tests/test_live.py) — `HTTPTests.test_cross_site`, line 27.
- [app/tests/test_live.py](sources/app/tests/test_live.py) — `HTTPTests.test_csrf_missing`, line 28.
- [app/tests/test_live.py](sources/app/tests/test_live.py) — `HTTPTests.test_csrf_wrong`, line 29.

Evidence: EV01, EV02, EV20.

**Limit:** Request token is CSRF protection, not login or proof of a reviewer. Trusted local processes and the separate model API can bypass the app boundary.

## CTRL02 — Reject unsupported JSON, modes, objects and properties before worker launch.

Historical demo identifier: `DEMO-v2:SEC-02`. Status: implemented with bounded evidence.

Duplicate/nonfinite rejection, exact field allowlist, known case/mode/condition validation and fixed routes.

Code references:

- [app/safety.py](sources/app/safety.py) — `decode`, line 18.
- [app/safety.py](sources/app/safety.py) — `check_selection`, line 62.
- [app/server.py](sources/app/server.py) — `Handler.do_POST`, line 164.

Existing test references:

- [app/tests/test_security.py](sources/app/tests/test_security.py) — `StrictInputTests.test_duplicate_and_nonfinite_json`, line 9.
- [app/tests/test_security.py](sources/app/tests/test_security.py) — `StrictInputTests.test_unauthorized_modes_and_fields`, line 12.
- [app/tests/test_live.py](sources/app/tests/test_live.py) — `HTTPTests.test_method`, line 34.

Evidence: EV01, EV02.

**Limit:** No multi-user object or role model; absence of such features narrows scope rather than proving public authorization safety.

## CTRL03 — Bind trusted code, inputs, models and requests to expected identities.

Historical demo identifier: `DEMO-v2:SEC-03`. Status: implemented with bounded evidence.

Release/input/model/template/request hashes and fixed native profile, before service/work and model use.

Code references:

- [app/safety.py](sources/app/safety.py) — `verify_release`, line 49.
- [app/common.py](sources/app/common.py) — `verified`, line 39.
- [app/backend.py](sources/app/backend.py) — `main`, line 39.
- [task03/run_task03.py](sources/task03/run_task03.py) — `validate_release`, line 42.
- [task03/run_task03.py](sources/task03/run_task03.py) — `verify_model_assets`, line 252.

Existing test references:

- [app/tests/test_security.py](sources/app/tests/test_security.py) — `StrictInputTests.test_release_tampering_is_rejected`, line 52.
- [app/tests/test_security.py](sources/app/tests/test_security.py) — `StrictInputTests.test_request_settings_frozen`, line 59.
- [task03/test_task03.py](sources/task03/test_task03.py) — `Task03Checks.test_source_mutation_refused_before_model_transport`, line 148.

Evidence: EV01, EV02, EV15, EV16, EV17.

**Limit:** Checksums do not authenticate the distributor or detect an already-backdoored approved model. Same-account replacement/races and coordinated manifest replacement remain assumptions.

## CTRL04 — Constrain data access and preserve private run storage.

Historical demo identifier: `DEMO-v2:SEC-04`. Status: implemented with bounded evidence.

Fixed served assets and run IDs; confined/size-bounded reads; ownership/private folders; atomic mode-0600 output.

Code references:

- [app/server.py](sources/app/server.py) — `Manager.__init__`, line 23.
- [app/server.py](sources/app/server.py) — `Manager.snapshot`, line 91.
- [app/safety.py](sources/app/safety.py) — `read`, line 26.
- [app/safety.py](sources/app/safety.py) — `save`, line 35.
- [app/common.py](sources/app/common.py) — `confined`, line 32.

Existing test references:

- [app/tests/test_security.py](sources/app/tests/test_security.py) — `StrictInputTests.test_atomic_write_symlink_and_permissions`, line 20.
- [app/tests/test_security.py](sources/app/tests/test_security.py) — `StrictInputTests.test_read_symlink_and_oversized`, line 27.
- [app/tests/test_security.py](sources/app/tests/test_security.py) — `ProcessTests.test_private_run_folder_required`, line 102.
- [app/tests/test_live.py](sources/app/tests/test_live.py) — `HTTPTests.test_unknown_file`, line 31.

Evidence: EV01, EV02, EV04.

**Limit:** The trusted account can read/export full passages, names, paths and model metadata. No dataset de-identification, encryption-at-rest or hostile-local-user isolation is established.

## CTRL05 — Treat corpus/model text as data across the browser, process and model-client boundaries.

Historical demo identifier: `DEMO-v2:SEC-05`. Status: implemented with bounded evidence.

Current JS uses textContent; subprocess argument lists are fixed; no shell use; model client uses fixed loopback and rejects redirects/proxies.

Code references:

- [app/backend.py](sources/app/backend.py) — `NoRedirect`, line 37.
- [app/backend.py](sources/app/backend.py) — `request`, line 23.
- [app/server.py](sources/app/server.py) — `Manager.work`, line 59.
- [app/static/app.js](sources/app/static/app.js) — `el` at line 6 uses `textContent`; inspected current source, not a fresh browser fixture.

Existing test references:

- [app/tests/test_security.py](sources/app/tests/test_security.py) — `StrictInputTests.test_no_redirect`, line 43.
- [app/tests/test_live.py](sources/app/tests/test_live.py) — `ControlTests.test_no_arbitrary_browser_arguments`, line 46.

Evidence: EV01, EV02, EV03, EV08.

**Limit:** Browser/OS injection protection is distinct from LLM instruction resistance. Prior browser fixture has selected coverage and changed current JS; no general prompt-injection defense follows.

## CTRL06 — Bound concurrency and response/job time.

Historical demo identifier: `DEMO-v2:SEC-06`. Status: implemented with bounded evidence.

UI: one job/eight HTTP slots/body-header-socket limits/four answer starts/590s each/2400s job. Task 3 has its own approved 60+1 starts and 7200s cap.

Code references:

- [app/server.py](sources/app/server.py) — `Server.process_request`, line 120.
- [app/server.py](sources/app/server.py) — `Manager.start`, line 48.
- [app/server.py](sources/app/server.py) — `Manager.work`, line 59.
- [app/backend.py](sources/app/backend.py) — `main`, line 39.
- [task03/run_task03.py](sources/task03/run_task03.py) — `Budget`, line 138.
- [task03/run_task03.py](sources/task03/run_task03.py) — `run_session`, line 204.

Existing test references:

- [app/tests/test_live.py](sources/app/tests/test_live.py) — `HTTPTests.test_large_body`, line 30.
- [app/tests/test_live.py](sources/app/tests/test_live.py) — `HTTPTests.test_busy`, line 38.
- [app/tests/test_lifecycle.py](sources/app/tests/test_lifecycle.py) — `LifecycleTests.test_timeout_becomes_terminal`, line 28.
- [task03/test_task03.py](sources/task03/test_task03.py) — `Task03Checks.test_time_cap_includes_preflight_and_resumed_elapsed`, line 128.
- [task03/test_task03.py](sources/task03/test_task03.py) — `Task03Checks.test_real_deadline_interrupts_blocking_operation`, line 171.

Evidence: EV01, EV02, EV15, EV16, EV17, EV19.

**Limit:** These profiles are different; do not transfer UI limits to CLI studies. No hard RAM/cgroup isolation; historical task-1 actual combined active time remains unknown.

## CTRL07 — Limit disk/archive and model-response growth.

Historical demo identifier: `DEMO-v2:SEC-07`. Status: implemented with bounded evidence.

UI: 2MiB model response, 128MiB run, 60-run/1GiB archive, 1GiB free admission/256MiB stop thresholds; bounded reads.

Code references:

- [app/server.py](sources/app/server.py) — `Manager.start`, line 48.
- [app/server.py](sources/app/server.py) — `Manager.work`, line 59.
- [app/backend.py](sources/app/backend.py) — `main`, line 39.
- [app/safety.py](sources/app/safety.py) — `read`, line 26.

Existing test references:

- [app/tests/test_lifecycle.py](sources/app/tests/test_lifecycle.py) — `LifecycleTests.test_resource_limit_preserves_partial_output`, line 31.
- [app/tests/test_security.py](sources/app/tests/test_security.py) — `StrictInputTests.test_read_symlink_and_oversized`, line 27.

Evidence: EV01, EV02.

**Limit:** Poll-based admission/stop checks are not filesystem quotas, and Task 3 does not inherit all UI disk/archive caps. Full disk/OS pressure coverage remains limited.

## CTRL08 — Cancel only owned processes and retain terminal state/partial evidence.

Historical demo identifier: `DEMO-v2:SEC-08`. Status: implemented with bounded evidence.

Owned worker/process-group cleanup; cancelled/timed-out/resource-limit/failed status; interrupted snapshots not shown as complete.

Code references:

- [app/server.py](sources/app/server.py) — `kill`, line 17.
- [app/server.py](sources/app/server.py) — `Manager.work`, line 59.
- [app/server.py](sources/app/server.py) — `Manager.cancel`, line 86.
- [app/server.py](sources/app/server.py) — `Manager.snapshot`, line 91.
- [task03/run_task03.py](sources/task03/run_task03.py) — `Backend.close`, line 193.

Existing test references:

- [app/tests/test_security.py](sources/app/tests/test_security.py) — `ProcessTests.test_owned_descendant_listener_is_closed`, line 83.
- [app/tests/test_lifecycle.py](sources/app/tests/test_lifecycle.py) — `LifecycleTests.test_cancel_and_second_job_refusal`, line 35.
- [app/tests/test_lifecycle.py](sources/app/tests/test_lifecycle.py) — `LifecycleTests.test_failed_worker_does_not_become_completed`, line 41.
- [task03/test_task03.py](sources/task03/test_task03.py) — `Task03Checks.test_timeout_and_operator_interruption_are_consumed_not_retried`, line 94.

Evidence: EV01, EV02, EV10, EV16, EV17.

**Limit:** Synthetic cleanup plus selected live cancellations do not prove every native/Ollama/OS failure path. Verify exact ownership before intervention; system Ollama is separate.

## CTRL09 — Retain attributable execution/review records without silent retries or substitution.

Historical demo identifier: `DEMO-v2:SEC-09`. Status: implemented with bounded evidence.

Run IDs, timestamps, exact requests, raw responses, explicit interruption disposition; Task 3 journal is hash-chained with consumed attempt begins.

Code references:

- [app/server.py](sources/app/server.py) — `Manager.snapshot`, line 91.
- [app/backend.py](sources/app/backend.py) — `main`, line 39.
- [task03/run_task03.py](sources/task03/run_task03.py) — `Journal`, line 74.
- [task03/run_task03.py](sources/task03/run_task03.py) — `validate_state`, line 101.

Existing test references:

- [app/tests/test_security.py](sources/app/tests/test_security.py) — `StrictInputTests.test_terminal_snapshot_retains_original_worker`, line 45.
- [task03/test_task03.py](sources/task03/test_task03.py) — `Task03Checks.test_unclosed_session_and_ambiguous_begin_refuse_resume`, line 104.
- [task03/test_task03.py](sources/task03/test_task03.py) — `Task03Checks.test_raw_capture_corruption_missing_duplicate_and_orphan_rejected`, line 114.

Evidence: EV04, EV06, EV10, EV15, EV16, EV17, EV19.

**Limit:** Local records and hashes can be rewritten by the account; no independent timestamping, signature, nonrepudiation or external alerting.

## CTRL10 — Keep scientific outcomes and review attribution tied to exact evidence.

Historical demo identifier: `DEMO-v2:SEC-10`. Status: implemented with bounded evidence.

Current/historical individual/joint/assisted records remain separate; fresh answers have pending semantic review; source qualifications and unknown dates preserved.

Code references:

- [app/server.py](sources/app/server.py) — `Manager.__init__`, line 23.
- [task03/audit_task03.py](sources/task03/audit_task03.py) — `audit`, line 8.

Existing test references:

- [task03/test_task03.py](sources/task03/test_task03.py) — `Task03Checks.test_all_attempts_raw_links_and_audit_do_not_inherit_historical_answers`, line 49.

Evidence: EV05, EV10, EV11, EV12, EV13, EV15, EV18.

**Limit:** Human confirmation is not blinded/unaided proof or a signature; task-2/3 new outputs remain unreviewed and broader teammate report/release binding remains task 6.

## CTRL11 — Fail safely on invalid/truncated backend output and sanitize public errors.

Historical demo identifier: `DEMO-v2:SEC-11`. Status: implemented with bounded evidence.

Bounded response bytes/schema/token/finish checks; preserve raw payload before parsing; no incomplete answer becomes a successful scientific outcome.

Code references:

- [app/backend.py](sources/app/backend.py) — `response_status`, line 28.
- [app/backend.py](sources/app/backend.py) — `main`, line 39.
- [app/server.py](sources/app/server.py) — `Handler.do_POST`, line 164.
- [task03/run_task03.py](sources/task03/run_task03.py) — `response_status`, line 91.

Existing test references:

- [app/tests/test_security.py](sources/app/tests/test_security.py) — `StrictInputTests.test_primary_backend_error_not_hidden`, line 39.
- [app/tests/test_security.py](sources/app/tests/test_security.py) — `ExtraHTTPTests.test_unexpected_failure_sanitized`, line 71.
- [app/tests/test_live.py](sources/app/tests/test_live.py) — `ControlTests.test_truncation_not_success`, line 54.
- [task03/test_task03.py](sources/task03/test_task03.py) — `Task03Checks.test_malformed_empty_wrong_model_tokens_overflow_and_http_stop`, line 75.

Evidence: EV01, EV02, EV10, EV15, EV16, EV17.

**Limit:** Local console/export may reveal paths; real backend branch coverage is not proved by synthetic tests or the report-only 16% figure. UI stops on truncation; approved Task 3 preserves it and may continue other requests.

## CTRL12 — Track software/model supply-chain exposure and preserve the accepted environment.

Historical demo identifier: `DEMO-v2:SEC-12`. Status: implemented with bounded evidence.

Pinned source/models, flat inventory/SBOM and historical advisory/static/secret scans. Fixes must use a separate environment and compatibility checks.

Code references:

- [app/backend.py](sources/app/backend.py) — `main`, line 39.
- [app/common.py](sources/app/common.py) — `verified`, line 39.
- [task03/run_task03.py](sources/task03/run_task03.py) — `verify_model_assets`, line 252.

Existing test references:

- [app/tests/test_security.py](sources/app/tests/test_security.py) — `StrictInputTests.test_release_tampering_is_rejected`, line 52.
- [task03/test_task03.py](sources/task03/test_task03.py) — `Task03Checks.test_wrong_served_version_digest_template_and_gpu_rejected`, line 136.

Evidence: EV07, EV08, EV09, EV15, EV20.

**Limit:** Baseline advisories remain open and per-finding reachability/patch validation is pending task 5/9; hashes and fixed inputs do not patch libraries or establish model/training provenance.

## Release binding

Byte identity only; inherited test evidence retains its execution version and selected coverage. Presentation JS changed; no blanket old-browser-test transfer.

See [BASELINE_CODE_BINDING.json](BASELINE_CODE_BINDING.json). Guard/backend/policy/test byte identity to the named historical versions does not extend to every changed display path or establish the version used for teammate live runs.
