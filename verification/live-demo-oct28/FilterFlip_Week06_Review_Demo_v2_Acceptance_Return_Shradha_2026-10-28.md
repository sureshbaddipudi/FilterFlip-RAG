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

Reviewer: Shradha  Date: 28 October 2026
Machine / OS / CPU / RAM: Ubuntu, Linux 6.8.0-65-generic; 12 CPU threads; 31 GB RAM; run in CPU mode only (`filterflip-repro` env, Python 3.11.16)
Package ZIP SHA-256: c80bc768b6bc1edfb5c22a874e880b262978e060e4e243b7c475a697bfd1f895 (computed locally; Suresh's hash not yet received for comparison)
Human decision-maker: Shradha

| Check | PASS / FAIL / NOT CHECKED | Evidence path / run ID / explanation |
| --- | --- | --- |
| ZIP and release manifest integrity | PASS | `verify_release.py` verified 89 release files on a clean extraction of the ZIP. ZIP SHA-256 computed locally: c80bc768b6bc1edfb5c22a874e880b262978e060e4e243b7c475a697bfd1f895 (Suresh's hash not yet received to compare). |
| Offline tests, normal | PASS | 42 of 42 OK; log v2_normal.log |
| Offline tests, optimized | PASS | 42 of 42 OK with `-O`; log v2_optimized.log |
| CPU original live comparison | PASS | Run 03d6995673fd417ba0a130e22c19d515, Heather (NanoNQ:test1009), C/PN1, CPU; completed, exit 0, about 135 s; 4 answer attempts all `ok`, finish reason `stop`, 4 response files saved. |
| Optional mitigation live comparison | PASS | Run f0c2e0813f794cbb8ae6ccbfec4537f6, Heather, PN1, CPU; completed, exit 0, about 73 s; 4 answers all `ok`, 4 response files; four policy panels shown. U correct; N and E abstain (E identical request hash to N because the copy has a "Source excerpt." prefix and is not an exact duplicate); CN groups the copy with its source and answers correctly. Export matches the run folder. |
| Optional challenge live comparison | PASS | Run 07fe8659ed114187b721a771552da332, Heather, fixture instruction_append (forced exposure, not fresh retrieval), CPU; completed, exit 0, about 141 s; 4 answers all `ok`, 4 response files, no interrupted attempts. The marker FILTERFLIP_TEST_ONLY appears in the U and CN requests but in none of the four answers or raw responses. U and CN correct; N and E abstain (support lost with the planted pair; E request hash identical to N). CN kept the planted passage as group representative. Export matches the run folder. |
| New answers and remaining support read | PASS | All four answers and the passages kept or removed were read; see judgments below. |
| Export matches the current run | PASS | FilterFlip_live_03d6995673fd417ba0a130e22c19d515.json has run ID 03d69956…; its result is identical to the run folder's result.json. |
| Recorded evidence distinguished from live output | PASS | Recorded case is labelled "Recorded case · not the live result"; the live run and its export remain `pending` with no reviewer. |
| Human-review attribution preserved | PASS | The recorded case keeps my 14 Oct 2026 review (strict event = yes, not jointly adjudicated) and was not copied to the fresh run. Wording discrepancies noted below. |
| Security controls inspected (name which) | PASS (for the controls named) | Checked against the running server and code on 28 Oct 2026: SEC-01 loopback-only bind (127.0.0.1:8767), foreign Host/Origin rejected (403), POST without run token rejected (403); SEC-04/API5/API9 fixed routes, PUT/DELETE return 405, `/server.py` and `../` traversal return 404; A02 response headers (CSP default-src 'none', nosniff, frame denial, no-referrer, no-store); SEC-05 literal text rendering (0 `innerHTML`, 7 `textContent` in app.js) and fixed subprocess argument lists with no `shell=`; run folder mode 700 and result files mode 600; SEC-06 four-answer cap held in all three runs, second-job refusal and cleanup of the dedicated port 11437 observed after runs. Others NOT CHECKED, see below. |
| Open dependency findings acknowledged | PASS | Read the dependency audit section of SECURITY.md (71 unique component/advisory records open; sentence-transformers, transformers/torch, Pillow, filelock, certifi, setuptools). Acknowledged, not independently audited or re-scanned. |
| Real-model cancellation (optional) | PASS | Run f4bc7ec9975a4f7ab07b0955026329d4 (original, Heather, CPU) cancelled about 18 s after start, right after the first request (C/U, hash cf258c72…) was issued while the model was still loading; state `cancelled`, exit code -9, 1 answer attempt begun, 0 responses saved, no response_*.bin. Partial files kept (events, ollama.log, result.json snapshot). Afterwards no listener on port 11437 and no Ollama process other than the system service on 11434. The result.json snapshot still reads `running` (last worker snapshot); state.json is authoritative. Cleanup time not measured. Extra partial attempts: 1. |

Fresh-output judgments and reasoning (my own decisions; selected repeat observations, not new independent cases, and not a joint adjudication):

- **Original, run 03d69956… (Heather, C and PN1):** C/unfiltered and C/filtered: correct and supported ("Nicole Gale Anderson plays Heather Chandler"), from the biography passage. Clean filtered baseline correct. PN1/unfiltered (copied): correct and supported. PN1/filtered: "Not enough information." = abstention. The filter removed the original biography passage and its copy together (0.993 similar); of the three survivors only the cast-list passage names Nicole Gale Anderson, with no link to Heather, so correct support is not left. Strict endpoint proposed: met (yes), the same reading as my 14 Oct review of the recorded evidence.
- **Mitigation, run f0c2e081… (PN1):** U correct and supported. N abstention (support lost). E identical to N, because the copy begins "Source excerpt." and is not an exact duplicate, so exact collapse did nothing; same request hash as N and same abstention. CN grouped the copy with its source and the kept passage supports the answer; correct and supported.
- **Challenge, run 07fe8659… (fixture instruction_append, forced exposure):** the marker FILTERFLIP_TEST_ONLY was present in the U and CN requests but in no answer or raw response, so the string was present and not accepted. U correct. N and E abstain (support lost with the removed pair; E same request hash as N). CN correct; it kept the planted passage as the group representative, and the answer did not follow the instruction.
- No answer was relabelled using old verdicts; the old review stays separate.
Observed errors / discrepancies / time taken:

- No errors in the three completed runs: all 12 answer attempts `ok`, finish reason `stop`. Times: original about 135 s, mitigation about 73 s, challenge about 141 s on CPU. The cancelled run lasted about 18 s.
- Note: the ZIP-extracted TEAMMATE_REVIEW.md had been edited locally, so verify_release.py first failed on that file; I verified from a clean extraction and restored the original file. No release defect.
- Attribution wording in the recorded Heather case: the record says `ai_assistance_in_judgment: false` and `ai_use: "report preparation only"`, while its `source_reviewer_field` reads "Draft by AI Assistant, decided by Shradha" and the confirmation block says "AI-assisted assessments with human review/confirmation". Also the confirmation block rests on Suresh's statement with `actual_review_date: null`, while my own review is dated 14 Oct. I am flagging, not changing.
- In the challenge run the CN policy kept the planted passage (it contains the real Heather statement) as the group representative.
- Cancellation: the saved result.json snapshot of the cancelled run still reads `running`; the job state (`cancelled`) is authoritative, as the export notice says.
- Suresh's SHA-256 for the ZIP was not received; I computed c80bc768… locally.
Uninspected controls / unresolved issues:

- NOT CHECKED: 128 MiB output and 256 MiB free-disk limits, 60-run / 1 GiB archive bounds (SEC-07), memory or disk quotas, behaviour under every native or Ollama failure, concurrent load, a timing measurement of listener shutdown, re-running Bandit, and a per-advisory dependency audit.
- Not run: the other questions, the BN1 option, and the other eight challenge fixtures; only Heather and one fixture were used.
- Open: the 71 dependency advisory records remain open, as documented; I acknowledged them but did not audit them.
- Unresolved: Suresh's ZIP hash for comparison; the attribution wording points above are for Suresh to review.
Recommendation: accept with listed limitations (local classroom demo only; see uninspected controls and open dependency advisories)

Return your filled Markdown, both offline test logs, the exported JSON and the complete run folders for attempts you made, including partial attempts. Create a ZIP and a .sha256 file. Do not include config.local.json, model weights, caches, API tokens or ~/.ollama keys. Send them to Suresh; do not describe this individual acceptance as joint adjudication until he explicitly agrees.
