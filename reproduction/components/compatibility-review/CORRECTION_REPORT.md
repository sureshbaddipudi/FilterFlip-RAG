# Comparator v2 — correction and verification

1 November 2026, Asia/Kolkata. This is a software-verification correction, not a new scientific review or revision of accepted judgments.

## Problem and corrected behavior

The original standalone comparator could report PASS when both profiles agreed on an unplanned case, when recorded cached-index deviations exceeded tolerance, or when recorded time/call limits were exceeded. The original packet validator already checked time/call bounds; it did not make those checks part of the reusable standalone command.

The new checker preserves the comparison calculations and adds mandatory gates:

| Required condition | v2 behavior |
|---|---|
| Exact planned cases and conditions | Derives the 72 retrieval keys and three challenge keys from the frozen plan. Both profiles must match all 75 keys with no duplicates. Matching each other alone is insufficient. A missing key produces a failed result without silently comparing a smaller matched subset. |
| Probe identity and coverage | Derives the exact ordered 75 probe texts and 40 cached-index document identities from the eight frozen selection records. Both profiles must contain the full inventories; cached identities must be unique. Metadata, token-record coverage and actual probe-array dimensions are checked. |
| Cached-index tolerances | Both maximum and mean deviations affect final status. Values must be finite, nonnegative numeric values, with mean no greater than maximum. Missing, duplicate, unplanned, empty or invalid records fail. Empty data has no reported maximum, rather than a default reassuring zero. |
| Recorded execution limits | Requires COMPLETE and the planned coverage, zero generation attempts and one model construction per profile. Encode counts must be nonnegative integers no greater than 1,000; recorded active time must be finite, nonnegative and no greater than 1,800 seconds. |
| Final command status | Any failed gate gives FAIL_COMPATIBILITY and a nonzero command exit. PASS_BOUNDED_COMPATIBILITY requires all declared prerequisites. No diagnostic-only exception is introduced for cached-index compatibility. |

All prior numerical/discrete comparison controls remain: document identity/order, request/token identity, numerical tolerances, valid empty copy arrays and refusal to overwrite output.

## Verification performed

Thirty-one regression tests pass in both normal and optimized Python. Each mode includes 40 temporary copied-record scenarios; mode repetitions are not additional independent tests. Scenarios reproduce the original false passes and verify rejection by v2. They also cover missing/duplicate/unplanned inventory, maximum-only and mean-only deviations, invalid numeric values, each profile's limits independently, incomplete status, empty/mismatched probe data and the five original control behaviors. Relevant command exit codes are checked as well as returned status.

The corrected offline comparison passes in both modes, with byte-identical outputs across modes:

| Saved profile | Exact planned contexts | Expected cached-index probes | Maximum absolute cached delta | Original recorded active seconds | Encode calls |
|---|---:|---:|---:|---:|---:|
| Baseline | 75 | 40 | 8.195638656616211e-08 | 131.3145482079999 | 373 |
| Candidate | 75 | 40 | 8.195638656616211e-08 | 133.1559784419951 | 373 |

All deviations satisfy the frozen maximum 1e-6 and mean 1e-7 tolerances. Both profiles retain 75 encoder probe texts. All 35 comparator gates pass. There are zero fresh-baseline/candidate discrepancies across the 75 contexts and 300 logical answer-request positions. The CONTEXT_COMPARISONS.json and DISCREPANCIES.json files are byte-identical to the historical Task 9 result; summary changes disclose the additional gates and version. The five original-versus-fresh retrieval-ID ordering differences remain unchanged and separate from candidate compatibility.

The 415 entries in the original Task 9 release manifest, the manifest itself and all 32 copied source records are unchanged. Only a new correction folder and its delivery are written. [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) binds every copied record. Original code and outputs are retained under inputs/ for transparent comparison.

## Interpretation and boundaries

This corrects a verification-tool weakness. It does not invalidate the saved compatibility result or establish semantic answer equivalence through new generation. The checker validates recorded values and frozen identities; it does not independently attest historical timing, certify every configuration or replace the sealed-manifest checks. Model/corpus-wide verification, candidate adoption and human residual-risk acceptance remain outside this correction. Task 5's dated residual advisory findings remain open within their recorded scope.

Accepted primary 8/51/0, post-outcome rule qualifications, mixed Week-6 findings, Task 8 uncertainty/discrepancies and R110 uncertainty remain unchanged. Existing human scientific review attribution remains unchanged. The project contribution and literature limits from Task 10 also stand. This engineering correction creates no additional scientific-review category or acceptance record.

No real encoder or answer model was loaded, no new study answer generated, no application/security/transport suite rerun, no service started and no dependency installed. Only the comparator regression tests and saved offline comparison were executed. Task 11 remains unstarted.
