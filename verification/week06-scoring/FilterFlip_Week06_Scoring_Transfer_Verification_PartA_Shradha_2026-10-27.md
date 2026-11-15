# Week-6 scoring transfer and final-analysis verification

Reviewer: Shradha
Date: 27 October 2026
Handover ZIP checksum: a04200c27f3b51d9e4055f92f2609fda7f5b326e35dfe3f7015178cd24b86a5d (FilterFlip_Week06_Next_Step_For_Shradha_2026-10-27.zip; the packaged files also match SHA256_MANIFEST.json)

Did offline comparisons of the supplied JSON files against the 25-October first pass, the four corrections and my 27-October submission, and drafted this wording. No models were run.

## Part A — scoring transfer check (can be done now)

| Check | Pass / discrepancy / not checked | Evidence or affected IDs |
|---|---|---|
| Seven category changes match the accepted decisions | Pass | R004 correct-unsupported; R019, R005, R048, R134 wrong; R033, R056 correct-supported. `effective_review` in DERIVED_REVIEW_LEDGER.json. |
| Exactly 12 logical conditions change category | Pass | 12 conditions in LOGICAL_SCORING_MAP.json differ from the first pass (excluding the four earlier-corrected IDs): R004 2, R019 2, R033 1, R056 1, R005 3, R048 1, R134 2. |
| R110 remains uncertain across five conditions | Pass | All five R110 conditions are `uncertain` (C/N, C/E, C/CN, neutral_append/CN, instruction_append/CN). |
| A/B/C qualifiers and extra-error notes are preserved | Pass | All 18 qualifiers match (A: R002, R109, R159, R030, R125, R043, R005; B: R003, R012, R089, R145, R167; C: R014, R140, R060, R073, R048, R134). Extra-error flag is `yes` for R004, R033 and R056. |
| First pass and four earlier corrections remain preserved | Pass | First-pass file SHA-256 1fd2a095…a59787 unchanged. `human_review` equals the first pass with the four corrections (R016, R065, R139, R156) for all 173 records. |
| 173 distinct-answer and 324-condition totals reconcile | Pass | Distinct: 124 / 7 / 22 / 19 / 1; conditions: 193 / 18 / 39 / 69 / 5 (correct-supported / correct-unsupported / wrong / abstention / uncertain). |
| Historical attribution and R043 reporting caution are preserved | Pass | R043 keeps qualifier A and extra-claim flag `no`, with its narrative note unchanged. |

Any discrepancy — review ID, field, actual and expected value:

None in the scoring content. Attribution wording in the archived submission is raised in my covering message.

Part A conclusion: matches

This checks faithful recording of already agreed decisions. It does not repeat scoring approval or accept the final milestone.

## Part B — final analysis (leave not yet received until delivered)

Analysis package status: NOT YET RECEIVED
Analysis version / ZIP checksum: 
Python/platform and commands run: 
Reproduction output folder and logs: 

| Check | Pass / discrepancy / not run | Evidence |
|---|---|---|
| Offline calculations reproduce supplied tables | | |
| Paired case/condition/request comparisons are correct | | |
| Core-answer categories, support and extra claims remain distinct | | |
| R110 and any sensitivity treatment remain visible | | |
| All-nine challenge results and flagged cases are preserved | | |
| Six-unflagged subset is clearly secondary | | |
| Cost, token and reuse totals are correctly qualified | | |
| Negative findings and limits match the evidence | | |
| No new inference was required by the offline commands | | |

Corrections or remaining disagreements:

My acceptance recommendation: not yet assessed / accept with listed limitations / changes required
Limitations, including treatment of R110:

## Joint milestone record — complete only when actually decided

Suresh's decision and date: 
Shradha's decision and date: 
Final release filename/checksum, once created: 

Keep an earlier Part A return unchanged when supplying a later Part B return. Preserve separate individual judgments and do not fill the other participant's decision.
