# Week-4 recovery v3 — second interruption amendment, 31 October 2026

Suresh authorized: “Yes, retry 487 once and finish the remaining queue”. The prior detailed proposal supplies the bounded accounting and execution design. It changes recovery orchestration only. Model, template, frozen requests, 128-token output limit, sequential CPU profile and dedicated port 11436 remain unchanged. No retrieval/filter execution or scientific-label change is introduced.

## Current verified checkpoint

The original 27-October continuation has 159 starts, 158 durable responses and the original uncertain attempt at 286. The approved v2 retry of 286 completed. The v2 queue then saved 201 complete responses (286–486), started 487, and was interrupted without a saved response or closing journal entry. Its process handle and parent PID are gone. The model log records HTTP 500 and cancellation of 487; parent exit cause is not established. The verified leftover owned daemon was stopped, releasing 11436; unrelated system Ollama on 11434 remains untouched.

Current effective coverage: 485 complete and one truncated unique response, 220 pending of 706. Logical coverage: 796 complete, five truncated, 261 pending of 1062. The old and retried 128 responses are both preserved as truncated. The original uncertain 286 and its successful authorized retry remain distinct. No new output inherits a previous semantic judgment.

All predecessor journal chains and raw captures reconcile. The 24 original v1 continuation/run files still match their fingerprints. `previous_release/` preserves v2 unchanged, including its original v1 snapshots. `second_interrupted_run/` preserves the interrupted v2 run, lock and unclosed journal unchanged. Never delete those locks, fabricate session ends, or append recovery outcomes to predecessor journals.

## Authorized specific exception

Authorize exactly one new retry of 487, then attempt 488–706 once each: 220 requests. Already consumed starts are 159 + 202 = 361. The amended continuation/recovery ceiling is 581 = 361 + 220. The uncertain original 487 remains in the attempt history even if the retry completes. This is one additional exception beyond v2's 580 ceiling, not authorization for automatic retries of future faults.

## Bounded time accounting

Actual historical session totals remain unmeasured because both predecessor sessions lack closing timers. Keep the approved v2 charge of 5988 seconds. Add 6494 seconds (rounded observed v2 start-to-begin-487 elapsed), a 600-second accounting reserve for its unknown ending interval, and 60 seconds for one new metadata-only preflight. Total predecessor/preflight accounting charge: 13142 seconds. New recovery active cap: 15658 seconds (4h 20m 58s). Accounting sum: 28800 seconds.

The reserve is not a measurement or proof that the unknown interval was at most 600 seconds. Actual combined historical active time cannot be certified at eight hours. The new process measures its own active sessions cumulatively and has request and whole-session timers. No time or attempt allowance is reset through an arbitrary new folder.

## Logged workspace worker

The launch method starts one bounded process independently of the chat's temporary process handle, with its own PID/PGID record and durable console file. This lets the continuing chat inspect the existing worker rather than start another. It does not guarantee survival of machine shutdown or forced process termination. Another ambiguous attempt still requires assessment.

The launcher refuses an existing launch record, console or run folder. Only the fixed plan-bound output is accepted. No relaunch/retry loop exists. To stop, verify the worker PID using its command line and recorded run, then send SIGTERM to that worker only; its handler preserves the fault and stops its own model daemon. Do not stop unrelated system services. Ordinary chat closure is not treated as an instruction to launch another worker.

## Authorized execution

```
python3 -B recover_answers.py --verify-only
python3 -B -m unittest -v test_recovery
python3 -O -B -m unittest -v test_recovery
python3 -B recover_answers.py --preflight --out ../FilterFlip_Week04_Recovery_Preflight_v3_2026-10-31
python3 -B launch_worker.py
```

Verify-only and synthetic tests make no model requests. Preflight checks pinned metadata without answer generation. The launcher starts the only approved queue and prints the PID and console paths. Inspect `FilterFlip_Week04_Recovery_Run_v3_2026-10-31/SUMMARY.json` and its journal; do not depend solely on a chat process handle. A clean identity-matching same-folder resume can deduct prior measured v3 time; uncertain/faulted states are deliberately refused.

## Outputs and review

`ATTEMPT_LEDGER.json` preserves all phases and both uncertain predecessor attempts. `COMBINED_LOGICAL_RESULTS.json` maps effective responses to 1062 conditions, with provenance/reuse explicit. `SUMMARY.json` retains unknown historical timing, all truncations, the approved attempt ceiling and technical status. A completed queue is not a correctness verdict. Final integrity audit and human-review packet follow execution; accepted primary/Week-6 results and original review attribution stay unchanged.

Suresh reports that the previous chat stopped at its credit limit. The worker is independent of the temporary chat process handle. `run_pipeline.py` automatically runs the offline final audit and prepares its review packet when generation exits cleanly; failures stop and remain recorded without retry. The pipeline status is stored in the sibling `FilterFlip_Week04_Recovery_v3_Pipeline_Status_2026-10-31.json`.
