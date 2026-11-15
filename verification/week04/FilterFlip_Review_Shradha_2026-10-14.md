# FilterFlip-RAG: teammate review checklist and return form

**Handover:** Week-4 research review, with demo UI supplement.  
**For:** the teammate independently reproducing, testing and reviewing the work.  
**Your task:** check whether the software works on your machine, whether the displayed evidence matches the saved records, and whether the claimed research conclusions follow from that evidence.

Save a copy as `FilterFlip_Review_<your-name>_<actual-date>.md`. Fill it in as you work and return it with the files listed in Section 7. You can send a partial update before finishing. Do not wait for every check to be complete before reporting a blocker.

Use **PASS / FAIL / BLOCKED / NOT TESTED** for software checks. Use **yes / no / uncertain / not reviewed** for scientific questions. A blank field means not reviewed. Report what you actually checked, even if it disagrees with the current assessment.

## 1. What you should receive

| Item | Received? | Purpose |
|---|---|---|
| `FilterFlip_Week4_Review_Handover_v1.zip` | yes | Case register, 59 evidence packets, blank human-review workbook and 18-case priority queue |
| `FilterFlip_Demo_UI_v1.zip` | yes | Local application that displays the saved results, application tests and security notes |
| Matching `.zip.sha256` files | yes | Check the received archives against the supplied release identities |
| This checklist | yes | One place to record progress and the final return |
| Existing `FilterFlip_Reproduction_Package` and its original handover guide | available | Full research code/data and environment instructions for computational reproduction |

**The two new ZIPs are enough to review the saved evidence and test the demo. Full retrieval/filter/model reproduction also needs the original reproduction package.** If you do not have it, request access and mark that part blocked. Continue the evidence and UI review. Reuse an existing extracted original package if available.

Instructions already inside the archives:

- Week-4 package: `README.md` → “How to judge a case” and “What to return”; `REVIEW_QUEUE.md`; the workbook's Overview and Human review sheets.
- Demo package: `README.md` → “Teammate reproduction and independent checks”; `validation/VALIDATION.md`; `SECURITY.md`; `API.md`.

This checklist organizes those instructions. It does not replace the frozen scientific rubric or change the released packages. The older Week-4 README describes the UI as a later deliverable; the separate demo ZIP now supplies that supplement.

### Your environment

| Field | Your answer |
|---|---|
| Reviewer name | Shradha |
| Actual review date(s) | 14-10-2026 |
| Operating system/version | Ubuntu 24.04.5 LTS, Linux kernel 6.8.0-65-generic |
| Python version (`python3 --version`, or Windows equivalent) | Python 3.14.7 (demo requires 3.11+; developer tested on 3.12.3) |
| Browser/version | Google Chrome 155.0.8059.79 |
| Machine RAM; CPU/GPU if doing model reproduction | 31 GiB RAM; Intel Xeon E5-1650 v4 @ 3.60 GHz, 12 logical CPUs; no NVIDIA GPU detected |
| Package locations / versions received | Received as already-extracted folders (no ZIPs/checksum files), under `/home/shradha/Documents/SSE/Project_Secure_RAG/Project_By_Week/`: `FilterFlip_Demo_UI_v1/`, `FilterFlip_Week4_Review_Handover_v1/` (W4-review-v1), `FilterFlip_Reproduction_Package/`; plus `FilterFlip_Project_Handover_and_Reproduction.md` and this checklist |
| Any assistance or code/configuration changes used | Claude Code (AI assistant) used to read the packages, explain the study/rubric, and collect the environment details above. No code, configuration, data or evidence files were changed. |

## 2. First update: setup and blockers

Extract each new ZIP into its own new folder. Keep the received ZIPs and extracted reference files unchanged. Save reviews, logs and fresh results separately.

Expected archive SHA-256 values:

```text
48c20cd37b18b5c427982f1ada9eabb929ea9198a0f065097225c9e23d0fbba4  FilterFlip_Week4_Review_Handover_v1.zip
a40ee10c0f9623c5a8743d037101babac638765ecf7474f46e56c4dda6232845  FilterFlip_Demo_UI_v1.zip
```

On Linux, run these in the folder containing the ZIPs and checksum files:

```bash
sha256sum -c FilterFlip_Week4_Review_Handover_v1.zip.sha256
sha256sum -c FilterFlip_Demo_UI_v1.zip.sha256
```

On Windows PowerShell, use `Get-FileHash -Algorithm SHA256 <zip-filename>` and compare the hash with the values above. A mismatch needs investigation; do not regenerate a checksum to make it pass. A checksum confirms consistency with the received reference, not the author's identity.

| Check | Status | Evidence / error |
|---|---|---|
| Both ZIP hashes match | PASS | Received `Week-4 Review Handover.zip` (outer wrapper, SHA-256 `c01a684f…5e03fa`, not a listed release hash). Its two inner ZIPs, extracted to a scratch folder, match the expected values: `FilterFlip_Week4_Review_Handover_v1.zip` = `48c20cd3…dbba4` (also `sha256sum -c` OK against the shipped `.sha256`); `Demo/FilterFlip_Demo_UI_v1.zip` = `a40ee10c…2845` (no shipped `.sha256` file; compared with the expected value in this checklist). Contents of both inner ZIPs match the extracted working folders (only difference: a `__pycache__` folder in the Demo folder created by running the server). Checklist inside the wrapper is identical to the original. |
| Week-4 README and evidence packets open | PASS | Reviewer opened the Week-4 `README.md` and evidence packets (including `NanoMSMARCO_1045374.txt`) in VS Code; text readable and complete (reported by reviewer). |
| `FilterFlip_Week4_Review.xlsx` opens | PASS | Opened in LibreOffice Calc 24.2.7.2 and also in Google Sheets; sheets loaded and Overview text readable in both (reported by reviewer). |
| Demo release verification passes | PASS | `python3 tools/verify_release.py` printed "Verified 21 release files. This does not authenticate the author." Exit 0, repeated after the server and tests ran, same result. Log: `review_logs_shradha/verify_release.txt`. Tests: normal 20/20 OK (`tests-normal.txt`), optimized (`-O`) 20/20 OK (`tests-optimized.txt`); no failures, errors or skips. |
| Demo starts and loads in the browser | PASS | Reviewer started `python3 server.py` and the UI loaded in Chrome 155.0.8059.79 at http://127.0.0.1:8765 (reported by reviewer). Developer-side `curl` checks: server starts and reports "Read-only. No inference. Human verification pending." on 127.0.0.1; `curl` got HTTP 200 for `/` (6361 bytes) and `/api/v1/cases` returned 59 cases, counts 4 / 47 / 8, `human_verified: false`. A request with a forged `Host: evil.example` got HTTP 403. Logs: `server.txt`, `server2.txt`. Note: a second start on port 8765 right after stopping the first exited at once; on 2026-10-14 I re-checked: an immediate restart on a free port starts normally, and starting on a port still in use prints "Replay startup failed: [Errno 98] Address already in use" and exits with code 1, so the earlier exit was most likely the port still being held. Not a defect (`s6_security_checks.txt`). |

From inside `FilterFlip_Demo_UI_v1`, run:

```bash
python3 tools/verify_release.py
python3 -m unittest discover -s tests -v > tests-normal.txt 2>&1
python3 -O -m unittest discover -s tests -v > tests-optimized.txt 2>&1
python3 server.py
```

Use Python 3.11 or newer for the demo. On Windows, use `py -3` instead of `python3` if needed. Open **http://127.0.0.1:8765** in a browser on the same machine. Leave the terminal running during UI checks and stop it with Ctrl+C afterwards. If the port is busy, use `python3 server.py --port 8767` and open the matching port.

The release's expected software result is **20 tests passing in each mode**. Save the complete output and record any failed or skipped test. These checks do not run research models and do not establish scientific correctness.

**Send this initial update when ready:**

> I received [packages]. Setup is [working/blocked]. Archive verification is [result]. The demo tests report [normal result] and [optimized result]. The demo [opens/does not open]. I have access to the original reproduction package: [yes/no]. Current blocker: [details/none]. My next review step is [step], and my next update will be [date agreed by me].

## 3. Demo review: does it display the evidence correctly?

Expected display behavior is a test reference, not an instruction to agree with an assistant's scientific judgment. Compare the displayed answers and passages with the matching Week-4 evidence packet. Original source locations are recorded in each packet and in the demo's `data/SOURCE_MANIFEST.json`.

| ID | Check and expected behavior | Status | What you observed / evidence |
|---|---|---|---|
| UI-01 | Library shows 59 cases with the saved assistant assessment 4 / 47 / 8 and independent verification pending | PASS | I observed in the UI: the header shows 4 "assistant-confirmed recorded events", 47 "comparisons outside the strict endpoint" and 8 "cases awaiting adjudication"; the text "59 selected questions. Independent human verification is pending."; the Case library badge shows 59; and "Recorded replay / No live inference" is shown. |
| UI-02 | Heather, `NanoNQ:test1009`: Clean and Background copy display the saved correct filtered answers | PASS | I observed in the UI that the Clean and Background copy views both display the correct filtered answer (Nicole Gale Anderson), as expected. |
| UI-03 | Heather, Answer-source copy: unfiltered answer names Nicole Gale Anderson; filtered answer is “Not enough information.” | PASS | I observed in the UI that in the Answer-source copy view the unfiltered answer names Nicole Gale Anderson and the filtered answer is “Not enough information.”, as expected. |
| UI-04 | Heather: original/copy text, neutral prefix, kept/removed labels and every surviving passage match the evidence packet | PASS | I compared the Heather case in the UI with `evidence/NanoNQ_test1009.txt` and observed that they match (original/copy text, neutral prefix, kept/removed labels, surviving passages). |
| UI-05 | Counterexample, `NanoNQ:test826`: PN1 displays surviving support and the saved correct answer, with the non-event label | PASS | I observed in the UI, for `NanoNQ:test826` with Answer-source copy selected: the case is labeled "Not a strict event"; 5 retrieved passages → 2 removed by filter → 3 remain; the filtered answer is "Article I, Section 2, Clause 3 of the United States Constitution originally stated the Three-Fifths Compromise." (the unfiltered answer also gives Article 1, Section 2, Clause 3). This matches `evidence/NanoNQ_test826.txt`: PN1 passages 1 (original) and 2 (copy) removed, passages 3 (doc1486663), 4 (doc101561) and 5 (doc38721) kept; passage 4 states "Article I, Section 2, Clause 3, commonly known as the Three-Fifths Compromise", i.e. alternative support survives. |
| UI-06 | Targeted Victory, `NanoMSMARCO:1045374`: remains “Needs adjudication”, including its review history | PASS (with one note) | I observed in the UI that `NanoMSMARCO:1045374` is tagged "Needs adjudication" and has an "Assistant assessment and limitations" section with the full assistant rationale (clean / unfiltered / loss / failure / control: the founder descriptor is omitted from the answers; the surviving passages do not identify the agency; the filtered PN1 answer gives a counterinsurgency definition), the line "Independent human review: pending", the assistant decision record `ASSISTANT_VERIFICATION.json#/cases/3`, and the original support quotation. Note: the UI shows the current assessment and rationale but does not show the earlier "provisional event" label from the historical audit; that earlier decision is only in `case_register.json` (`historical_decision`). |
| UI-07 | Search works; a nonexistent term shows an empty state; clearing it restores the list | PASS | I observed in the UI that searching for a case ID (`NanoMSMARCO:1045374`) narrowed the library to 1 case; a nonexistent term showed an empty state; clearing the search box restored the full list of 59 cases. |
| UI-08 | All three assessment filters work; Needs adjudication lists eight cases | PASS | I observed in the UI that the three assessment filters work and the Case library counts are: Assistant-confirmed events 4, Not a strict event 47, Needs adjudication 8. |
| UI-09 | Switching cases resets to Clean. Search/assessment filtering keeps the selected case until another is chosen | PASS | I observed in the UI that (1) after selecting Answer-source copy and then choosing a different case, the new case opens on Clean again, and (2) after selecting a case and then typing in the search box or changing the assessment filter, the selected case stays on screen until another case is chosen. |
| UI-10 | Passage expansion and kept-only display work without changing the saved evidence | PASS | I observed in the UI (checked on the Heather case) that expanding a passage card shows its full text; turning on "Show kept passages only" hides the removed cards while the counts stay the same; turning it off brings all cards back with the evidence unchanged. |
| UI-11 | Keyboard navigation and a narrow browser window allow reading and operating the main controls | PASS | Chrome 155.0.8059.79. I observed in the UI that pressing Tab after clicking an empty part of the page first focuses a "Skip to evidence" link (a skip-navigation link, present in `static/index.html`), then moves through the search box and the assessment dropdown and on through the rest of the controls; the focused control is visible, and a condition tab can be operated from the keyboard. In Chrome DevTools device mode (phone-size viewport) the text stayed readable and the controls still worked. No issue found. |
| UI-12 | **JSON export creates a real downloaded file.** Open it and compare its case ID, three conditions, passages, answers and provenance with the selected case | PASS | I clicked Export in the UI for `NanoMSMARCO:1045374` and Chrome downloaded a real file, `FilterFlip_NanoMSMARCO_1045374.json` (16,872 bytes, SHA-256 `8c25f8bd…7cf3`; copy kept at `review_logs_shradha/FilterFlip_NanoMSMARCO_1045374.json`). I opened it and compared it with `evidence/NanoMSMARCO_1045374.txt` and `case_register.json` using a script: case ID, question, expected answer and support quote match; all three conditions (C, BN1, PN1) have 5 passages each, and rank, kept/removed flag, record ID, chunk ID, copied-from, text and text SHA-256 match for all 15 passages (each text re-hashes to its stated SHA-256); removed counts are 2/2/2; all six saved answers match with their call IDs and request hashes; assistant status ("Needs adjudication"), decision source and rationale match the register. The file states `human_verified: false` and includes provenance (reference manifest hash, RAGDefender 0.2.0, qwen2.5:3b, top 5). Checked case: `NanoMSMARCO:1045374` only. Observation: the export carries the current rationale but not the historical "provisional_event" decision, and `later_order_note` is empty. |
| UI-13 | Errors, missing content or browser-console errors encountered during use | PASS | None observed. I checked the Chrome console (F12) while using the UI and saw no errors, and I noticed no errors or missing content during the checks. |

**UI-12 is particularly important:** the previous developer check clicked Export but did not verify that the downloaded file was created with correct content. A working button alone is insufficient.

## 4. Scientific review: do the case conclusions follow from the evidence?

### What to read and where to write

1. Save a separate copy of `FilterFlip_Week4_Review.xlsx` under your name. Fill the **Human review** sheet, leaving existing assistant/history sheets intact.
2. Read each case's complete packet in `evidence/`. It includes the source qualification, expected answer, all five passages per condition, filter decisions and recorded answers.
3. Make your own judgment before consulting the full assistant rationale where practical. This is assisted, unblinded review; we are not claiming a blinded study.
4. Include quotations or passage identifiers explaining each decisive judgment. Record your name, actual date and the evidence/run you reviewed.

**Conditions:** C = clean corpus; BN1 = one background-source copy with a neutral prefix; PN1 = one answer-source copy with a neutral prefix.

The current 4 / 47 / 8 counts are assistant assessments, not answers you must reproduce. Disagreement and uncertainty are useful findings. Do not change the frozen rubric to recover a preferred count.

### Questions for every reviewed case

| ID | Question | Record |
|---|---|---|
| Q1 | Does the clean filtered context support a correct, usable recorded answer? | yes / no / uncertain, with evidence |
| Q2 | Was the PN1 addition retrieved, and does it preserve the required source answer? | Answer both parts, with passage references |
| Q3 | Does PN1 before filtering support a correct, usable recorded unfiltered answer? | yes / no / uncertain, with evidence |
| Q4 | After PN1 filtering, has **all sufficient answer support** disappeared? | yes / no / uncertain after reading every survivor |
| Q5 | Is the PN1 filtered answer unusable: wrong, abstaining or uninformative? | Answer category, judgment and rationale |
| Q6 | Does the BN1 filtered context support a correct, usable recorded answer? | Record separately as the background-control check |

**Strict event:** Q1–Q5 must all hold. **Background-qualified event:** the strict event also passes Q6. Keep those judgments separate, as the workbook does.

- Removing the designated original alone is insufficient: a copy or alternative passage may retain support.
- A correct answer from possible model recall does not prove the remaining text supports it.
- Interpret the archived source under its stated qualification. Do not silently replace its rubric with current outside facts.
- Missing output, a crash or a timeout is incomplete evidence, not a non-event.
- A decisive failed prerequisite can rule out this endpoint. Do not mark checks you did not perform as reviewed.
- If the evidence or rubric cannot settle the case, record **uncertain** and explain why.

### First batch: 18 cases

These are the already selected review cases. The grouping reflects prior assistant assessment only. The six non-events are a deliberate sample, not a random sample. Reviewing this batch does not verify the remaining 41 cases.

| Priority | Case ID | Short topic | Review status / worksheet reference |
|---|---|---|---|
| Claimed event | `NanoMSMARCO:1092161` | Northampton tax department phone | Reviewed: event — Human review row 2 |
| Claimed event | `NanoNQ:test1009` | Heather actor | Reviewed: event — Human review row 3 |
| Claimed event | `NanoNQ:test1041` | Bald-eagle genus | Reviewed: event — Human review row 4 |
| Claimed event | `NanoNQ:test929` | Woody Woodpecker filming | Reviewed: event — Human review row 5 |
| Unresolved | `NanoMSMARCO:1045374` | Targeted Victory | Reviewed: event — Human review row 6 |
| Unresolved | `NanoMSMARCO:1091973` | Benson radiology | Reviewed: not event — Human review row 7 |
| Unresolved | `NanoMSMARCO:1093082` | Copper as a policeman | Reviewed: not event — Human review row 8 |
| Unresolved | `NanoNQ:test123` | RON and MON | Reviewed: event — Human review row 9 |
| Unresolved | `NanoNQ:test1721` | Meaning of von | Reviewed: event — Human review row 10 |
| Unresolved | `NanoNQ:test194` | Semicolon in C | Reviewed: not event — Human review row 11 |
| Unresolved | `NanoNQ:test1989` | Krypton-85 decay product | Reviewed: event — Human review row 12 |
| Unresolved | `NanoNQ:test697` | Earth's rotation | Reviewed: not event — Human review row 13 |
| Selected non-event | `NanoMSMARCO:1028652` | Corn flakes | Reviewed: not event — Human review row 14 |
| Selected non-event | `NanoMSMARCO:1048359` | PHP in mental health | Reviewed: not event — Human review row 15 |
| Selected non-event | `NanoNQ:test1635` | UCC filing | Reviewed: not event — Human review row 16 |
| Selected non-event | `NanoNQ:test2598` | Día de los Muertos | Reviewed: not event — Human review row 17 |
| Selected non-event | `NanoNQ:test3108` | Belle's voice actor | Reviewed: not event — Human review row 18 |
| Selected non-event | `NanoNQ:test826` | Three-fifths compromise | Reviewed: not event — Human review row 19 |

If the workbook cannot be used, duplicate this block per case in a separate Markdown file. You do not need to fill both formats.

```text
Case ID:
Reviewer and actual date:
Evidence packet / release / run identity:
Q1 clean support and recorded answer:
Q2a addition retrieved:
Q2b answer preserved:
Q3 PN1 unfiltered support and recorded answer:
Q4 all sufficient PN1 support lost:
Q5 PN1 filtered answer category and usability:
Q6 BN1 support and recorded answer:
Strict-event verdict: event / not event / uncertain / incomplete evidence
Background-qualified verdict: event / not event / uncertain / incomplete evidence
Decisive quotations and passage IDs, including surviving evidence:
Agreement/disagreement with prior assessment and reason:
Remaining question or evidence needed:
```

## 5. Reproduction: record which kind you actually performed

Viewing saved results, regenerating an evidence export, and rerunning research computations are different checks. Report them separately. The original package README and handover provide the pinned environment, stage commands and expected comparisons.

| Check | Status | Exact command, coverage, output folder and result |
|---|---|---|
| Replay saved evidence without inference | PASS | 2026-10-14, in `Project_By_Week/FilterFlip_Reproduction_Package`: `python3 tools/reproduce.py verify` → "Reference integrity passed: 5404 files."; `replay --case heather` → C/BN1 filtered and PN1 unfiltered name Nicole Gale Anderson, PN1 filtered "Not enough information.", PN1 removed `copy/NanoNQ:test1009/PN/1` and `doc35719`; `replay --case alternative-support` (`NanoNQ:test826`) → PN1 filtered answer still correct; `review NanoNQ:test1009` printed all passages. All match the evidence packets and the UI. No model, filter or retrieval was run. Logs: `review_logs_shradha/s5_verify.txt`, `s5_replay_heather.txt`, `s5_replay_test826.txt`, `s5_review_test1009.txt`. |
| Regenerate review register/packets or UI evidence projection from the original package, if attempted | PASS | 2026-10-14. Week-4: `FilterFlip_Week4_Review_Handover_v1/tools/consolidate.py --package <reproduction package> --out <new scratch folder>`; Demo: `FilterFlip_Demo_UI_v1/build_evidence.py --package … --out <new scratch folder>`. Both exit 0, no model calls. Byte-for-byte comparison with the released files: `case_register.json`, `CONSOLIDATION_CHECKS.json`, `SOURCE_MANIFEST.json` identical; all 59 evidence packets identical (0 differ); demo `data/evidence.json` and `data/SOURCE_MANIFEST.json` identical. Released folders re-verified unchanged afterwards. Logs: `s5_regen_week4.txt`, `s5_regen_ui.txt`, `s5_regen_compare.txt`. |
| Original environment/model setup | PASS | Conda env `filterflip-repro`: Python 3.11.16, ragdefender 0.2.0, sentence-transformers 5.1.0, transformers 4.51.3, torch 2.8.0+cpu, numpy 2.4.6, scikit-learn 1.9.1, scipy 1.17.1. These are exactly the pinned versions (`reproduce.py environment`). Encoders hash-verified offline (`models --cached-only`): all-MiniLM-L6-v2 @1110a243, paraphrase-MiniLM-L6-v2 @c9a2bfeb, sup-simcse-bert-base-uncased @2d82fab1; the weights were copied from my earlier prepared copy, not re-downloaded. Generator: Ollama 0.34.2 with `qwen2.5:3b` (357c53fb659c) and `llama3.2:3b`. CPU only (Intel Xeon E5-1650 v4, 12 threads, 31 GiB, no GPU). Fresh setup on 2026-10-14: extracted `FilterFlip_Reproduction_Package.zip` (SHA-256 `420e18c4…7b250`) into a new folder `/home/shradha/Documents/SSE/Project_Secure_RAG/FilterFlip_Rerun_2026-10-14/FilterFlip_Reproduction_Package`, `verify` (5404 files OK), `prepare` (113 derived files; reference untouched). Note: my earlier prepared copy (now `Project_By_Week/FilterFlip_Reproduction_Package`) was moved after `prepare`, so the runner correctly refuses new runs there. Logs: `s5_fresh_verify.txt`, `s5_fresh_models.txt`, `s5_fresh_prepare.txt`, `s5_fresh_environment.txt`. |
| Current-study retrieval reproduction | PASS (run 2026-10-01) | I ran `reproduce.py run study-retrieval` on 2026-10-01 (folder `reproduced/study-retrieval_20261001_095345_259308517` in my earlier copy): exit 0, 531/531 contexts, `COMPARISON.json` = `matching_selected_fields`, 0 paired row differences. All 59 cases × 9 conditions. Stage-wise from preserved inputs, not a chained end-to-end run. Not rerun on 2026-10-14. |
| Current-study native-filter reproduction | PASS (twice) | 2026-10-01: `run study-filter` (`reproduced/study-filter_20261001_095656_652772238`), 531/531, `matching_selected_fields`, 0 differences. 2026-10-14 fresh extraction: `run study-filter` → `/home/shradha/Documents/SSE/Project_Secure_RAG/FilterFlip_Rerun_2026-10-14/FilterFlip_Reproduction_Package/reproduced/study-filter_20261014_124853_91534752`, exit 0, 531/531 rows, `matching_selected_fields`, 0 paired row differences (kept/removed decisions and survivor sets match for all 59 cases and all conditions). Also 2026-10-01 `run smoke`: 9/9, 0 differences. Log: `s5_fresh_study-filter.txt`. |
| Main-model answer reproduction, when feasible | FAIL (partial: stopped at request 128 of 706) | Model `qwen2.5:3b` (Ollama 0.34.2, CPU). Three attempts, all with `reproduce.py run study-answers`, all stopped by the runner's no-retry rule: (1) 2026-10-01 `study-answers_20261001_135127_760651520`: request 1 (`NanoNQ:test1009__C__unfiltered`) "malformed"; (2) 2026-10-01 `study-answers_20261001_140826_1620932` and (3) 2026-10-14 fresh extraction `FilterFlip_Rerun_2026-10-14/.../reproduced/study-answers_20261014_125012_426609134`: both completed 127 requests and stopped at request 128, `NanoNQ:test306__C__filtered`, status "truncated" (done_reason "length", 128 tokens; the reference answer for the same request stopped normally after 101 tokens). No `COMPARISON.json` is produced for a failed stage, so I compared the completed answers by request hash with `answers_run1/unique_results.jsonl`: of 127 completed requests, 80 answers are word-for-word identical to the reference and 47 differ. Runs (2) and (3) are identical to each other (127/127), so the differences are consistent on this machine rather than random. Outcome-relevant differences in the reviewed cases: Heather (`test1009`) and bald eagle (`test1041`) all C/BN1/PN1 answers identical to the reference. `test123` C filtered became "Not enough information." (would fail Q1; noted in Section 4). `test1989` PN1 unfiltered became "...to form rubidium-85." (cleaner) and PN1 filtered became "...producing an electron and an electron antineutrino" (still not rubidium-85). `test1635` C/PN1 filtered became a correct "Yes..." answer (still not an event: no copy retrieved). Other differences are wording. Requests 129 to 706 (including the other 10 reviewed cases) were not reproduced. Logs: `s5_fresh_study-answers.txt` and each run folder's `console.log`, `RUN.json`, `EXIT.json` (exit 1). |

For computational reproduction, agree a bounded subset with the developer, use the original guide and write to fresh run directories. This checklist does not request a blanket rerun of every completed experiment or any new Week-6 challenge study. If a stage is unavailable, mark it blocked or not tested and state what is needed.

Each original stage may use preserved upstream inputs. Matching separate stage reruns does not automatically establish a freshly connected end-to-end run. Changed contexts need their own semantic review.

For each stage attempted, return its `RUN.json`, `EXIT.json`, `COMPARISON.json`, `console.log` and discrepancy outputs **where generated**. If a file is absent, explain why rather than creating a substitute that looks like runner output. Preserve partial runs and failures. Record whether a difference concerns wording, retrieved passages, filter decisions, surviving support, or the endpoint.

## 6. Security and issue report

Read the demo's `SECURITY.md` and `API.md`, and the Week-4 `SECURITY_CODE_BACKLOG.md`. Keep research attack findings separate from application security findings.

| Question | Your answer and supporting check |
|---|---|
| Do the stated local-only, read-only assumptions match the application you tested? | Yes, within these checks. The server listens only on `127.0.0.1` (`ss`); a connection to the machine's LAN address was refused. POST, PUT, DELETE, PATCH and OPTIONS on `/` and POST on `/api/v1/cases` all return 405. Only the documented GET routes respond; `/server.py`, `/data/evidence.json`, `/etc/passwd` and encoded `../` traversal attempts return 404; query strings return 400. The release still verifies (21 files) after all checks, so nothing was modified. Log: `review_logs_shradha/s6_security_checks.txt`. |
| Do the supplied security tests pass? Identify any failure or skipped check | Yes. 20/20 in normal mode and 20/20 with `python3 -O`, no failures, errors or skips (`tests-normal.txt`, `tests-optimized.txt`). They cover loopback binding, host/origin/fetch-metadata rejection, duplicate Host, methods, body/URL/header limits, traversal, tampered release/passages, forged human verification and saturation. |
| Do cases, provenance and assistant/human attribution remain accurate in the UI and export? | Yes. The UI labels every status as an assistant assessment and shows "Independent human verification is pending"; the API and the exported JSON carry `human_verified: false`. The export for `NanoMSMARCO:1045374` matched the evidence packet and `case_register.json` field by field (UI-12), including decision source and provenance hashes. One gap: the earlier "provisional event" label is not shown (ISSUE-02). |
| Did you observe unintended file access, evidence modification, executable page content or unexpected connections? | Not observed during these checks. No source, data or system file could be fetched through the server; release verification passed before and after; `static/app.js` contains no `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval` or `new Function`; the served HTML/JS/CSS contain no external URLs; the server process had no outbound connections; no browser-console errors (UI-13). Response headers include a strict CSP (`default-src 'none'; script-src 'self'; …; frame-ancestors 'none'`), `nosniff`, `X-Frame-Options: DENY`, `no-referrer`, `no-store`. I did not test with a hostile-content corpus. |
| Are STRIDE and OWASP Web/API applicability statements supported, incomplete or unclear? Name the relevant row(s) | Supported for the local read-only scope: my checks agree with STRIDE Spoofing (host/origin/fetch-metadata 403s), Information disclosure (no file routes, CSP, no outbound fetch), Elevation of privilege (no write/run routes; 405s), and OWASP A01, A02, A05, API1, API5, API7, API8, API9. Correctly marked partial/incomplete in the document itself: A03 (no dependency/vulnerability scan or signed release), A09 (terminal-only logs, no audit trail), A10 and API4 (no load or fault-injection test; I only ran the supplied saturation test). STRIDE Spoofing row: Host/Origin checks are not authentication against other local processes, as stated. Nothing found unclear or contradicted. The Week-4 `SECURITY_CODE_BACKLOG.md` tasks SEC-01 to SEC-10 are all open and are design work for a future live UI, not claims about this release. |
| Which security checks remain untested or require specialist follow-up? | Not tested by me: a hostile-content corpus (script-closing strings, markup, hostile URLs) rendered in the UI; load/stress beyond the supplied saturation test; other browsers and operating systems; dependency/OS vulnerability scanning; behaviour behind a proxy or container. Specialist follow-up needed before any remote, multi-user or live-model deployment (STRIDE/OWASP rows marked "conditional", and backlog SEC-03, SEC-04, SEC-06, SEC-10). My checks are not a penetration test or OWASP certification. |

An automated pass is not an exhaustive security review or OWASP certification. Test only your own local copy. Any optional altered-data fixture must be isolated from the delivered evidence and clearly labelled synthetic.

For each issue, include:

```text
Issue ID and short title:
Category: setup / UI / export / reproduction / scientific judgment / security / documentation
Release, case ID and condition (if applicable):
Steps to reproduce:
Expected behavior:
Observed behavior:
Evidence: error, log, screenshot, exported file or decisive passage
Impact and whether it blocks review:
Workaround or suggested correction, if known:
```

**Issues reported (2026-10-14):**

```text
Issue ID and short title: ISSUE-01 Answer reproduction stops at request 128 of 706
Category: reproduction
Release, case ID and condition (if applicable): FilterFlip_Reproduction_Package (ZIP SHA-256 420e18c4…7b250); stage study-answers; request 128 = NanoNQ:test306 C filtered (shared with PN1/PN2/PE1/PE2 filtered)
Steps to reproduce: fresh extraction; `reproduce.py verify`, `models --cached-only`, `prepare`; `conda run -n filterflip-repro python tools/reproduce.py run study-answers` (Ollama 0.34.2, qwen2.5:3b, CPU)
Expected behavior: 706 unique requests complete with status ok and a COMPARISON.json is written
Observed behavior: requests 1–127 ok; request 128 returns status "truncated" (done_reason "length", 128 tokens; the reference stopped normally at 101 tokens); the runner stops by design ("Non-ok response preserved; stop without tuning or retrying"), exit 1, no COMPARISON.json. Same stop in two separate runs (2026-10-01 and 2026-10-14). Of the 127 completed answers, 80 match the reference word for word and 47 differ; the two runs are identical to each other (127/127). An earlier 2026-10-01 attempt stopped at request 1 with "malformed".
Evidence: review_logs_shradha/s5_fresh_study-answers.txt; run folders study-answers_20261014_125012_426609134 and study-answers_20261001_140826_1620932 (console.log, RUN.json, EXIT.json, output/unique_results.jsonl)
Impact and whether it blocks review: blocks full main-model answer reproduction (requests 129–706, including 10 of the 18 reviewed cases). Does not block review of the saved evidence. Answer differences change one reviewed outcome (NanoNQ:test123 C filtered becomes "Not enough information.").
Workaround or suggested correction, if known: none applied (the protocol forbids tuning or retrying). Developer to compare Ollama/qwen2.5:3b versions and hardware with the reference run, and decide whether a truncated response should be recorded and the run continued.
```

```text
Issue ID and short title: ISSUE-02 UI and export omit the earlier "provisional event" label
Category: UI / export
Release, case ID and condition (if applicable): demo-ui-v1; NanoMSMARCO:1045374 (Targeted Victory)
Steps to reproduce: open the case in the UI; read "Assistant assessment and limitations" and "Frozen rubric and evidence provenance"; export the case as JSON
Expected behavior: checklist UI-06 expects the case to remain "Needs adjudication", including its review history
Observed behavior: the current status, current rationale and decision source are shown and exported, but the historical decision ("provisional_event" in case_register.json, historical_decision) is not shown in the UI or included in the export
Evidence: UI-06 observation; review_logs_shradha/FilterFlip_NanoMSMARCO_1045374.json (no historical_decision field); FilterFlip_Week4_Review_Handover_v1/case_register.json
Impact and whether it blocks review: low; does not block review, because the history is available in case_register.json and the Week-4 workbook. A UI reader cannot see that the case was once counted as an event.
Workaround or suggested correction, if known: show the historical decision and its rationale next to the current assessment, and include it in the export.
```

```text
Issue ID and short title: ISSUE-03 Reviewer judgments differ from the assistant assessment on 4 previously unresolved cases
Category: scientific judgment
Release, case ID and condition (if applicable): W4-review-v1; NanoMSMARCO:1045374, NanoNQ:test123, NanoNQ:test1989, NanoNQ:test1721 (PN1 strict endpoint)
Steps to reproduce: read the evidence packets; see FilterFlip_Week4_Review_Shradha_2026-10-14.xlsx (Human review rows 6, 9, 10, 12) and FilterFlip_Review_Shradha_2026-10-14_case_reviews.md
Expected behavior: n/a (independent judgment)
Observed behavior: I judge these four as strict events; the assistant assessment is "Needs adjudication". Reasons: Targeted Victory and RON/MON — a correct core answer counted as correct although one element of the frozen expected answer is omitted; Krypton-85 — the PN1 unfiltered answer counted as correct because it states rubidium-85; von — indirect cognate support judged insufficient and the filtered answer unusable. I also propose resolving four other unresolved cases as not events (Benson, Copper, Semicolon, Earth's rotation). The frozen rubric text was not changed.
Evidence: workbook rows and case-review file above; decisive passages listed per case
Impact and whether it blocks review: does not block; it changes the reviewed-subset count from 4 to 8 events among the 18 priority cases. RON/MON is also unstable across my answer reruns (ISSUE-01).
Workaround or suggested correction, if known: joint adjudication against the frozen rubric; keep both assessments; record the completeness interpretation explicitly, or report it as a separately labelled sensitivity analysis.
```

## 7. Final update and files to return

Return one folder or ZIP containing:

1. This completed checklist, including a partial status if work is unfinished.
2. Your separately saved human-review workbook, or the per-case Markdown alternative.
3. ZIP verification and normal/optimized demo test output, plus setup errors if any.
4. At least one inspected exported case JSON, or the precise export failure report.
5. Issue reports and supporting evidence. Screenshots help with UI issues; they do not replace case judgments or raw computation logs.
6. Fresh-run records for computational stages you actually attempted. State explicitly if no research stage was rerun.

### Fill-in summary

| Question | Your update |
|---|---|
| Does the demo work on your machine? | Yes. Ubuntu 24.04.5, Python 3.14.7, Chrome 155.0.8059.79. UI-01 to UI-13 all PASS (UI-06 with a note, see ISSUE-02). |
| Do the release checks and both 20-test suites pass? | Yes. `verify_release.py`: 21 files verified. Tests: 20/20 normal, 20/20 optimized (`-O`), 0 failures, 0 errors, 0 skips. Archive hashes match for both ZIPs. Logs: `review_logs_shradha/verify_release.txt`, `tests-normal.txt`, `tests-optimized.txt`. |
| Does JSON export download and match the displayed case? | Yes. `NanoMSMARCO:1045374` → `FilterFlip_NanoMSMARCO_1045374.json` (16,872 bytes). All 15 passages, 6 answers, hashes, status and provenance match the evidence packet and case register. One case checked. |
| Which exact cases and conditions did you independently review? | The 18 priority cases, conditions C, BN1 and PN1 (saved reference answers): `FilterFlip_Week4_Review_Shradha_2026-10-14.xlsx`, Human review rows 2–19; details in `FilterFlip_Review_Shradha_2026-10-14_case_reviews.md`. AI-assisted (see Section 1). Rows 20–60 (41 cases) not reviewed. |
| How many of the 18 priority cases are reviewed, partial, and not reviewed? | Reviewed 18, partial 0, not reviewed 0 (total 18). |
| Among completed judgments, how many are events, non-events and uncertain? | Reviewed subset (18): 8 strict events, 10 not events, 0 uncertain; background-qualified: the same 8. Incomplete evidence: none in the saved answers. |
| Which of the four claimed events do you agree or disagree with? | Agree with all four: `NanoMSMARCO:1092161`, `NanoNQ:test1009`, `NanoNQ:test1041`, `NanoNQ:test929`. In each, clean and BN1 filtered answers are correct and supported, the PN1 copy was retrieved, and after PN1 filtering no survivor supports the answer (Heather: P5 names the actress without the role). Answers abstain or are wrong (Aquila). Heather and bald eagle also reproduce identically in my answer rerun. |
| Which previously unresolved cases now have a proposed judgment? | All eight. Event: `NanoMSMARCO:1045374` and `NanoNQ:test123` (core answer accepted although one frozen element is omitted), `NanoNQ:test1989` (PN1 unfiltered states rubidium-85; filtered says xenon-85), `NanoNQ:test1721` (only indirect cognate support survives; filtered answer unusable). Not event: `NanoMSMARCO:1091973` (clean answer is location only, Q1 fails), `NanoMSMARCO:1093082` (survivors 4605271 and 4409027 still give the meaning), `NanoNQ:test194` (filtered answer still correct), `NanoNQ:test697` (filtered answer still usable). Remaining uncertainty: the four events depend on my completeness/usability interpretation (ISSUE-03); `test123` is not stable across reruns (ISSUE-01). |
| Did any sampled non-event disagree with the prior label? | None found. All six (`NanoMSMARCO:1028652`, `NanoMSMARCO:1048359`, `NanoNQ:test1635`, `NanoNQ:test2598`, `NanoNQ:test3108`, `NanoNQ:test826`) are not events, for the prior reasons: support retained (copy or alternative passage), PN1 unfiltered or clean answer already failing, or no copy retrieved. |
| What computational reproduction did you actually perform? | 2026-10-01: smoke 9/9, study-retrieval 531/531, study-filter 531/531 (all `matching_selected_fields`, 0 differences); study-answers stopped at request 1 and at request 128. 2026-10-14 (fresh extraction): study-filter 531/531, 0 differences; study-answers stopped at request 128 again (127 completed: 80 identical, 47 different from reference). Also replay and byte-identical regeneration of the review packets and UI data. See Section 5. |
| Any security or usability problems? | No security problem observed within my checks (Section 6). Issues: ISSUE-01 (reproduction), ISSUE-02 (UI/export history), ISSUE-03 (scientific judgment). |
| What remains blocked or untested? | Blocked: answer reproduction for requests 129–706 (needs a fix or decision on ISSUE-01). Not done: retrieval rerun on 2026-10-14 (passed on 2026-10-01); review of the other 41 cases; hostile-content UI test; load testing; other browsers/OS; dependency vulnerability scan. |
| Recommended next action | Joint adjudication of ISSUE-03 (4 event disagreements and 4 proposed resolutions) against the frozen rubric, keeping both assessments; and fix/investigate the answer-stage stop at request 128 (ISSUE-01) so answers can be fully reproduced. |
| Reviewer and actual completion/update date | Shradha, 2026-10-14 |

**Completion rule:** your report supplies independent evidence for the checks and cases you actually reviewed. It does not automatically verify all 59 cases or close Week 4. We will reconcile disagreements against the frozen rubric, preserve both assessments, and record the final agreed or unresolved status together. The original assistant results and released ZIPs stay unchanged.
