# FilterFlip-RAG GUI v2.6.1 — display identity corrections

5 November 2026. This is the full live-capable GUI, with two display defects corrected after the Astra software/evidence review. Use app/launch.py or app/server.py. No generation-blocking GUI wrapper is included. The accepted v2.6 GUI, Task-13 v2.0 delivery, returns and joint acceptance are preserved unchanged.

## Start

Extract this ZIP into a new folder, activate your existing pinned environment and work from the new packet root. Reuse your existing real configuration and cached assets; no package/model extraction or installation is required. Use a new external work folder to keep the new test separate:

```bash
python3 -B tools/verify_packet.py
python3 -B app/configure.py --from-config /ABSOLUTE/PATH/TO/YOUR/EXISTING/config.local.json --work /ABSOLUTE/PATH/TO/NEW/FilterFlip_v261_test
python3 -B app/launch.py /ABSOLUTE/PATH/TO/NEW/FilterFlip_v261_test/config.local.json
```

Open http://127.0.0.1:8767. For another free local port:

```bash
python3 -B app/server.py --config /ABSOLUTE/PATH/TO/NEW/FilterFlip_v261_test/config.local.json --port 8770
```

Only Run live comparison starts generation. Actual app/server.py is unchanged. Its four modes, all-nine selection, saved views, original recorded view and existing generation limits remain available. Model answers are not automatically correct or accepted. Keep config, runs, screenshots and notes outside this packet. Stop your own server with Ctrl+C when finished; do not stop unrelated services.

## Changes

- Reconnecting to an active run restores its actual question, mode and condition. A persistent identity line stays with its results and JSON export uses the original snapshot.
- Outdated Inspect recorded case responses/errors are ignored after changing question, condition or mode, starting a run, or issuing another inspection.
- Findings and Evidence now displays the dated Task-12/13 joint completion. Original scoped v2.4 history remains.

Read REVIEW_DISPOSITION.md, VALIDATION_REPORT.md and TEST_PLAN.md for scope and checks. No new model run is required for these display corrections. The original Task-12/13 acceptance is not acceptance of this new GUI version; its visual flows remain available for Suresh/Shradha to check. The comprehensive report awaits Suresh’s manuscript review; presentation instructions remain pending. Prior documents retained in baseline/v2_6_docs and dated app documentation describe their historical releases and do not reopen completed tasks.
