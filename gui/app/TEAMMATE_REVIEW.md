# Shradha — acceptance check for Week-6 live review demo v2

This is a new GUI/code release. Your accepted Week-4 and Week-6 research reviews remain preserved. Please do not repeat those studies or relabel new answers using the old verdicts.

## What you receive and need

Use this ZIP plus the separate handover Markdown. Keep your existing reproduction inputs, environment, encoder and Ollama model. The ZIP is a supplement and contains no large models/corpora. Copy config.example.json to config.local.json, set your six paths and keep compute_profile as cpu. See README for launch and SECURITY for the known dependency advisories. Do not upgrade the accepted environment in place or expose the server remotely.

## Minimal review before 30 October

1. Verify the ZIP checksum and then `python3 -B verify_release.py` after extraction.
2. Run `python3 -B -m unittest discover -s tests -v` and repeat with `python3 -B -O -m unittest discover -s tests -v`. Record the actual counts and logs; do not assume the developer count.
3. Launch the GUI and run **Original finding / Heather / Clean + answer-source copy** once on CPU. Record elapsed time, run ID, completion/failure, and whether four fresh response records exist. Inspect passage order and read the answers. A different answer is a finding to report, not automatically a software failure.
4. If time permits, run **Week-6 mitigation / Heather / Answer-source copy** once. Verify the four policy panels, grouped/removed distinctions and exact saved requests. This optional second run is four more answer calls.
5. Verify Export this run produces the current run ID and actual result, not another run. Open recorded evidence separately and confirm its human attribution is not copied onto the fresh run.
6. Review SECURITY's STRIDE/Web/API mapping and residual risks. Specifically check the fixed local endpoints/arguments, literal text rendering, failure limits and dependency disclosures. Mark anything not inspected as NOT CHECKED.

The minimal plan is one original run (four answer attempts). The optional mitigation run adds four. A challenge run is optional and adds four; it uses approved forced six-passage exposure, not fresh attacker retrieval. Do not run an unrestricted batch. Preserve failed and interrupted attempts. Live stop/restart behavior is covered by developer synthetic tests; only mark a real-model cancellation check passed if you actually perform and record it, with its extra partial attempt count.

## Semantic review of new responses

For each original condition, state whether the unfiltered and filtered answers are correct, incomplete, wrong, abstaining or uncertain. Read the remaining passages: is sufficient correct evidence still available? Is the clean filtered baseline correct? Is the copied unfiltered answer correct? Only then propose whether the strict endpoint is met. Keep your judgments separate from program status. These demonstrations are selected repeat observations, not new independent cases for a headline rate.

For mitigation/challenges, distinguish the presence of a string from accepting a claim. Explain mixed answers and completeness uncertainty. Do not revise the accepted scoring policy on the fly. Record any use of AI assistance and who made each decision.

## Return this small report, exports and logs

Reviewer: __________  Date: __________
Machine / OS / CPU / RAM: __________
Package ZIP SHA-256: __________
AI assistance (none / tool and purpose): __________
Human decision-maker: __________

| Check | PASS / FAIL / NOT CHECKED | Evidence path / run ID / explanation |
| --- | --- | --- |
| ZIP and release manifest integrity | | |
| Offline tests, normal | | |
| Offline tests, optimized | | |
| CPU original live comparison | | |
| Optional mitigation live comparison | | |
| Optional challenge live comparison | | |
| New answers and remaining support read | | |
| Export matches the current run | | |
| Recorded evidence distinguished from live output | | |
| Human-review attribution preserved | | |
| Security controls inspected (name which) | | |
| Open dependency findings acknowledged | | |
| Real-model cancellation (optional) | | |

Fresh-output judgments and reasoning: __________
Observed errors / discrepancies / time taken: __________
Uninspected controls / unresolved issues: __________
Recommendation: accept for local classroom demo / accept with listed limitations / changes needed: __________

Return your filled Markdown, both offline test logs, the exported JSON and the complete run folders for attempts you made, including partial attempts. Create a ZIP and a .sha256 file. Do not include config.local.json, model weights, caches, API tokens or ~/.ollama keys. Send them to Suresh; do not describe this individual acceptance as joint adjudication until he explicitly agrees.
