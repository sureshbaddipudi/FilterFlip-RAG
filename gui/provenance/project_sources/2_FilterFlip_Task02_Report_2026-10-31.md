# Task 2 — secondary copy/type analysis

Recorded: 31 October 2026, Asia/Kolkata. Offline analysis of saved evidence; zero retrieval, filter or model calls.

All nine predeclared conditions already ran in the original study. The additional reproduction is now accounted for. This analysis retains all 59 selected cases (35 NanoNQ, 24 NanoMSMARCO), including clean failures and exposure misses. Conditions are repeated measures on those cases, not independent samples. Current primary findings remain 8 events / 51 non-events / 0 unresolved primary classifications; R110 remains uncertain in the separate Week-6 study.

## Inventory and review scope

531 saved contexts and native-filter decisions join to 1062 logical answer rows per answer panel and 706 distinct generation requests. The reference panel is complete. The combined-machine/operator reproduction has 1057 complete logical rows and five truncated links to one unique request (NanoNQ:test306 filtered C/PN1/PN2/PE1/PE2). Its full unique coverage is 705 complete, one truncated, zero pending. Requests 286 and 487 have preserved uncertain originals and separately authorized successful retries; original/retried 128 truncations remain preserved in task 1. No new run is required for these analyses.

The accepted human confirmation covers all 59 original primary assessments (C/BN1/PN1), with individual and eight-case joint decisions taking precedence. The inspected records provide no condition-specific human decisions for the six secondary variants. This is a review-coverage gap for 354 case-condition comparisons and 708 logical answers per panel, not a claim that the original cases remain human-unreviewed. Existing selected-field retrieval/filter rerun comparisons are computational evidence, not semantic adjudication. REVIEW_COVERAGE.json preserves their exact scope.

## Copy exposure and quotation tracking

Digits are inserted document budgets. A document can contribute several chunks or none to the top five. The exposure columns count distinct inserted documents actually retrieved, not chunks or guaranteed correct/supporting passages. B denotes the background-source control; it is not a semantic irrelevance label. P denotes copies of the selected answer source.

The quote metric checks the complete archived support quote in any one passage after collapsing whitespace, exactly as the historical screen. It does not classify all sufficient semantic support. Missing quotes can coexist with adequate alternative evidence; source identity or answer-name occurrence alone cannot establish support.

| Condition | Cases with 0 / 1 / 2 copy documents retrieved | Quote before /59 | Quote after /59 | Quote disappeared | Clean-qualified quote-loss screen |
| --- | --- | --- | --- | --- | --- |
| C | 59 / 0 / 0 | 40 | 20 | 20 | n/a |
| BN1 | 2 / 57 / 0 | 39 | 33 | 6 | n/a |
| BN2 | 1 / 3 / 55 | 37 | 33 | 4 | n/a |
| PN1 | 18 / 41 / 0 | 42 | 9 | 33 | 16 |
| PN2 | 18 / 2 / 39 | 42 | 13 | 29 | 12 |
| BE1 | 0 / 59 / 0 | 39 | 34 | 5 | n/a |
| BE2 | 0 / 0 / 59 | 37 | 33 | 4 | n/a |
| PE1 | 20 / 39 / 0 | 40 | 7 | 33 | 18 |
| PE2 | 20 / 2 / 37 | 40 | 11 | 29 | 13 |

The last column requires: clean filtered quote retained; at least one P-copy document retrieved; P quote present before filtering and absent afterward. It is a structural screening flag, not an attack-success count. The complete case list, per-dataset tables and background-qualified screens are in the JSON outputs. A positive flag does not check clean/unfiltered answer usability or alternative surviving support; a negative flag does not prove safety.

## Paired copy-count and copy-type changes

Every pair below contains the same 59 cases. “0→1” means the full quote is absent after filtering in the left condition and present in the right. “1→0” means the reverse. Neither transition alone establishes a semantic gain or loss.

| Left → right | 0→0 | 0→1 | 1→0 | 1→1 | Identical ordered input text | Identical ordered survivor text |
| --- | --- | --- | --- | --- | --- | --- |
| BN1 → BN2 | 21 | 5 | 5 | 28 | 1 | 8 |
| PN1 → PN2 | 42 | 8 | 4 | 5 | 20 | 23 |
| BE1 → BE2 | 21 | 4 | 5 | 29 | 0 | 5 |
| PE1 → PE2 | 45 | 7 | 3 | 4 | 22 | 23 |
| BN1 → BE1 | 25 | 1 | 0 | 33 | 0 | 49 |
| BN2 → BE2 | 26 | 0 | 0 | 33 | 0 | 45 |
| PN1 → PE1 | 50 | 0 | 2 | 7 | 18 | 48 |
| PN2 → PE2 | 46 | 0 | 2 | 11 | 18 | 51 |

Two inserted P copies do not yield a monotonic worsening in this frozen configuration. PN1→PN2 restores the full quote in eight cases and loses it in four; PE1→PE2 restores it in seven and loses it in three. Equal marginal totals can also hide reversals: BN1 and BN2 each retain 33 quotes, with five gains and five losses. BE1→BE2 has four gains and five losses.

Exact versus prefixed P copies changes quote retention in two cases at each budget. PN1→PE1 loses the full quote for test3090 and test3108; PN2→PE2 loses it for Targeted Victory (1045374) and test2721. These are not four automatically confirmed new events. All case IDs and transitions are retained in PAIRED_CASES.json.

This is a comparison of the full predefined variants, not an isolated causal estimate of adding a prefix. Copy 1 uses “Source excerpt.\n”; copy 2 uses “Reference excerpt.\n”. Exact copies have neither prefix. The complete source is copied before fixed-window chunking, so prefixes can change chunk boundaries, embeddings, rankings, exposure, displaced passages and downstream filter behavior. The two-copy arm adds a different second prefix in N variants. Different copy identities also remain subject to the documented hash-based tie rule. No setting, passage order, label or threshold was changed to favour an outcome.

## Paired answer text

The two answer panels are shown separately. Counts below are identical/different/incomplete **strings** among the 59 paired filtered answers. An incomplete pair is excluded from same/different counts. “Different” includes harmless wording changes and material changes; “same” can still be wrong. Shared request hashes reuse one response and are not independent confirmations.

| Pair | Reference: same / different / incomplete | Reproduction: same / different / incomplete |
| --- | --- | --- |
| BN1 → BN2 | 30 / 29 / 0 | 26 / 33 / 0 |
| PN1 → PN2 | 33 / 26 / 0 | 31 / 27 / 1 |
| BE1 → BE2 | 27 / 32 / 0 | 21 / 38 / 0 |
| PE1 → PE2 | 33 / 26 / 0 | 30 / 28 / 1 |
| BN1 → BE1 | 54 / 5 / 0 | 55 / 4 / 0 |
| BN2 → BE2 | 51 / 8 / 0 | 49 / 10 / 0 |
| PN1 → PE1 | 52 / 7 / 0 | 52 / 6 / 1 |
| PN2 → PE2 | 54 / 5 / 0 | 52 / 6 / 1 |

### Reproduction versus reference by condition

| Condition | Complete logical rows /118 | Truncated links | Exact reference strings | Different complete strings |
| --- | --- | --- | --- | --- |
| C | 117 | 1 | 70 | 47 |
| BN1 | 118 | 0 | 67 | 51 |
| BN2 | 118 | 0 | 76 | 42 |
| PN1 | 117 | 1 | 71 | 46 |
| PN2 | 117 | 1 | 70 | 47 |
| BE1 | 118 | 0 | 61 | 57 |
| BE2 | 118 | 0 | 69 | 49 |
| PE1 | 117 | 1 | 71 | 46 |
| PE2 | 117 | 1 | 62 | 55 |

These counts overlap across conditions when the full generation request is identical. They must not be summed as independent requests or converted to accuracy/event rates. Task 1 retains the unique-request denominators; each per-case packet supplies request hashes, reference and reproduction answers, actual surviving text, and original attribution.

## Review and acceptance boundary

The six secondary variants have blank per-case human support, answer, endpoint, reviewer/date and disagreement fields in cases/. Original primary decisions are included for context and remain unchanged. Exact ordered-context matches to a primary arm are navigation aids, never silent transfer of acceptance to a secondary or newly reproduced answer. Human review must inspect every survivor, the clean prerequisite and exposed unfiltered condition, and the matching background control. Preserve accepted core/mixed interpretation and its original scope/post-outcome provenance; disclose any proposed extension to a new comparison, and obtain joint agreement where material. Do not mark a case as reviewed merely because a string or quote matches.

Task 2 implementation and offline paired analysis are complete. Human semantic review and scientific acceptance of the secondary/new outcomes remain pending under task 7; integrated reviewed outcome analysis follows under task 8. The companion CASE_INTERPRETATIONS.md supplies three explicitly assistant-authored examples, not a replacement 59-case adjudication. No teammate message is sent. Bigger datasets and new mitigation research remain deferred.
