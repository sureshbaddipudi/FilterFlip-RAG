# Task 3 implementation: TrustRAG stage-1 selection + evidence-only Qwen

Recorded 31 October 2026, Asia/Kolkata. Suresh approved the delivered design by instructing “Its time for the implementation”. The separate authorization record binds the unchanged design manifest; the original proposed design retains its historical approval fields.

## Scope and execution

Use the twelve existing questions, C/BN1/PN1 and the saved TrustRAG stage-1 outputs. Generate 60 distinct fresh Qwen requests serving 72 logical U/T positions, reusing only identical requests inside the new run. One frozen synthetic preflight is allowed. Maximum generation starts: 61 including preflight; total active allowance 7,200 seconds, per-request cap 600 seconds, startup/metadata cap 60 seconds. Temperature 0, seed 42, context 4096 and output 128 are unchanged.

Three filtered signal-transduction positions contain no passages and share one request. Three saved component outputs have native survivor order different from sorted retrieval indices. Both are preserved. Historical answers remain diagnostic references, with their original provenance; no historical answer fills the new primary panel or replaces an incomplete attempt.

## Files

- `design/`: unchanged approved design, draft requests, source records and offline compatibility checks.
- `EXECUTION_AUTHORIZATION.json`: dated user authorization and exact design binding.
- `run_task03.py`: request/release validation, full model-asset hashes, owned CPU service, one synthetic preflight, bounded generation, raw captures and chained journal.
- `audit_task03.py`: offline integrity and coverage audit, fresh logical joins, historical comparisons, twelve complete case-review packets and a readable answer table. It makes zero model calls.
- `launch.py`, `pipeline.py`: a single logged workspace worker; the generation invocation is followed once by the offline audit. No automatic relaunch or retry.
- `test_task03.py`, `validation/`: isolated synthetic checks; test responses are not study evidence.
- `inputs/`: unchanged historical reference/reproduction and original filter snapshots. Input/source manifests bind them to the originals.

## Running and inspection

This checkpoint is bound to the current Codex workspace. It is not final task-13 portable acceptance. A single production launch is authorized; first inspect whether its worker/run/status records already exist. The launcher refuses any existing execution evidence. Do not replay a completed launch.

From this release directory the execution entry point is:

```bash
python3 -B launch.py
```

The worker writes sibling `FilterFlip_Task03_Worker_2026-10-31.json` and `.log`, `FilterFlip_Task03_Pipeline_Status_2026-10-31.json`, `FilterFlip_Task03_Run_2026-10-31/`, and the separate final audit directory. Its ownership record identifies the exact pipeline PID. The runner records its owned loopback service on port 11437; system Ollama is not controlled. The worker can continue if the chat handle is lost. Inspect saved records and exact process ownership before any intervention.

The active timer starts before service startup and the synthetic request. Durable begin records precede every generation attempt; raw bytes and hash-chained completion records follow. Length stops are retained as incomplete and remaining unattempted requests may continue within the caps. Other faults stop the run. An ambiguous begin remains a consumed attempt and cannot be retried automatically. Clean, closed durable prefixes can be resumed with the existing approved budget, skipping every saved request and the already-completed synthetic probe. Faulted, corrupt, ambiguous or unclosed sessions require a separate recorded assessment. A standalone resume command is not a recovery approval.

The owned service is requested on CPU, with parallelism one and cloud/proxies disabled. Full model-layer hashes are checked before startup; model/version/template identity is checked during execution, and loaded model metadata must show zero VRAM. All sources and approved requests must match their manifests. No input shortening, passage reordering, output-token increase or threshold adjustment is permitted.

## Review and acceptance

A successful response or integrity audit does not establish semantic correctness. Human review under task 7 must inspect actual support, full/core answer completeness, abstention/wrong/incomplete status, wrong extras and uncertainty against exact source-qualified passages. Earlier assistant component interpretations and human-reviewed primary outcomes keep their original attribution and do not become new hybrid-pipeline decisions. The code supplies separate new review fields, not guessed labels or dates. Material disagreements are resolved by Suresh and Shradha with both assessments retained.

The experiment evaluates only TrustRAG stage-1 survivor selection followed by the established evidence-only Qwen answering protocol. It does not run later TrustRAG self-assessment/memory/consolidation stages or establish full-system failure. The accepted primary 8/51/0 and Week-6 findings, original review attribution and R110 uncertainty remain unchanged. No teammate message is sent. Desktop and frozen evidence are preserved.
