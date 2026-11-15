# Task 8 — paired analysis of reviewed outcomes

Recorded 1 November 2026, Asia/Kolkata. The approved offline integration is complete. This is reproducible aggregation of existing evidence and the accepted Task 7 joint human review by **Shradha and Suresh, without AI assistance in those human reviews**. Codex wrote the analysis code/report; it did not provide new human judgments. Earlier review attribution and unknown actual dates remain unchanged. [Analysis plan](ANALYSIS_PLAN.json) was written after review acceptance; it is a descriptive retrospective plan, not a preregistration.

## Reproduction: wording and meaning are different measures

The full saved comparison has 706 requests: 705 completed and one retained truncation. Its original 127-response teammate prefix is preserved. Task 7 directly reviewed the later **579 responses /821 logical links**. They contain 321 exact text matches, 257 changed strings and one truncation. Shared logical links are not independent trials.

Among the **257 changed strings**, accepted semantic labels are **83 none, 163 minor and 11 material**. The eleven material request records concern six cases and thirteen logical links; their exact answers and source qualifications are in [MATERIAL_DIFFERENCES.md](MATERIAL_DIFFERENCES.md). Across all 579 rows the literal review labels are 402 none, 165 minor, 11 material and one unset/incomplete. Two exact-text matches are labelled minor in the return; these are preserved and flagged, not counted as observed wording changes. No string-equality shortcut establishes evidence support or correctness.

For the **35 cases with an explicit new primary endpoint review**, literal labels are four met and 31 not met. Of 34 technically complete matched comparisons, three remain met, 30 remain not met and one changes from not met to met: **NanoMSMARCO:1048359 (PHP)**. The retained test306 truncation excludes one pair. The other 24 original cases have no new primary endpoint record in this Task 7 scope; accepted originals are not silently transferred. This does **not** revise the historical 8/51/0 classification.

## Copy budget/type comparisons

All eight declared contrasts cover all 59 selected cases structurally (472 pairs), with separate reference and reproduction panels (944 case-panel pair records). Inserted budgets and actual retrieved copies differ. PN2 retrieves zero/one/two copied documents in **18/2/39** cases; PE2 in **20/2/37** cases. Distinct documents, not chunk counts, define exposure. [COPY_COMPARISONS.md](COPY_COMPARISONS.md) includes every contrast, dataset stratum and coverage boundary.

| Condition / panel | Case scope | Met | Not met | Uncertain | Missing endpoint review |
|---|---|---|---|---|---|
| PN1 / reference | 59 | 8 | 51 | 0 | 0 |
| PN2 / reference | 59 | 4 | 54 | 1 | 0 |
| PE1 / reference | 59 | 9 | 49 | 1 | 0 |
| PE2 / reference | 59 | 7 | 51 | 1 | 0 |
| PN1 / reproduction | 59 | 4 | 31 | 0 | 24 |
| PN2 / reproduction | 59 | 3 | 54 | 2 | 0 |
| PE1 / reproduction | 59 | 8 | 50 | 1 | 0 |
| PE2 / reproduction | 59 | 5 | 52 | 2 | 0 |

These are literal accepted endpoint labels, not independent success-rate estimates. The PN1 reproduction row has only 35 labels. One test306 truncated physical response underlies its C/PN1/PN2/PE1/PE2 filtered links; literal tables preserve reviewed labels but paired outcome calculations separately exclude incomplete chains. Each affected secondary reproduction row has one such incomplete chain among its labels.

On complete determinate reference pairs, **PN1→PN2 has one endpoint gain and five losses**; PE1→PE2 has one gain and three losses. Thus adding a second copy is not uniformly more harmful. Exact versus prefixed changes also depend on the case: PN1→PE1 has one reference endpoint gain and no loss; PN2→PE2 has three gains and no loss, with uncertainty retained separately. These selected-case observations do not establish a general effect of exact copies or a monotonic attack law. Matched reproduction endpoint comparisons using PN1 are restricted to its 35 reviewed cases; do not compare unmatched bar totals.

## TrustRAG stage 1: support, answers and full chains

All 12 selected cases and 36 U/T context pairs are retained: **60 distinct fresh responses serve 72 logical positions**. U is all retrieved evidence and T is stage-1-selected evidence under the frozen answering protocol. This is not full TrustRAG. [TRUSTRAG_CASES.md](TRUSTRAG_CASES.md) reports every case, including clean failures, surviving alternatives, empty contexts and stable outcomes.

Support stays sufficient in 20 contexts, becomes partial in five and becomes absent in six; five start and stay absent. Of the 32 pairs with determinate core usability, one changes no→yes, eight yes→no, sixteen yes→yes and seven no→no; four other pairs retain uncertainty. Full frozen-answer completeness is separate: one no→yes, eight yes→no, eleven yes→yes, fifteen no→no and one uncertain pair. Three empty T contexts share one physical response.

Strict endpoint judgments are **five met /six not met /one uncertain**. The stronger background-qualified endpoint is **three met /eight not met /one uncertain**. The 12-case historical native comparison has four not-met→met changes and one met→met, but it compares fresh T answers with historical native-filter outcomes. Only seven cases have an explicit new native reproduction endpoint record; among those, two change not-met→met, four stay not-met and one remains uncertain. Neither panel is a fresh matched native/T generator experiment, and neither supports a general defense-ranking claim.

## Other reviewed application outcomes

The older carryover is separate: 19 runs /76 logical outputs in 18 request-answer groups. Four CN false-claim run outputs are human-labelled wrong, all for the same Heather case and the same answer group. Instruction checks contain 12 outputs, eight with the marker supplied and zero literal matches among those eight. These narrow observations are not independent case replications or general instruction-resistance evidence. No pooling with the five Task 6 fresh v2.4 jobs, the primary study or the TrustRAG subset occurs.

## Data quality and limits retained

One accepted cross-record field discrepancy concerns **NanoNQ:test1618 PN2 filtered core usability**: the condition panel says no; its response record says uncertain. Both values remain unchanged. [LIMITATIONS_AND_QUALITY.md](LIMITATIONS_AND_QUALITY.md) traces them and reports a conservative sensitivity that withholds that field from determinate paired comparisons. The secondary PN2→PE2 reproduction core comparison loses one no→no pair under this sensitivity; endpoint counts do not change. The two exact-text/minor-label annotations are also retained. No human-review uncertainty is resolved by this analysis.

All 150 flagged notes and every case, including negatives/stable outcomes, remain accessible through the source return and [CASE_RESULTS.md](CASE_RESULTS.md). Primary **8 events /51 non-events /0 unresolved classifications**, accepted mixed Week-6 findings and **R110 uncertain** stay unchanged. Original post-outcome core/mixed rules, source qualifications, visible references, selected Nano cases, shared requests and mixed-machine/operator reproduction limit interpretation. Historical recovery accounting is not proof of a measured combined eight-hour run. No model, retrieval or filter was rerun. Larger datasets and new mitigation research remain deferred.

[README.md](README.md) explains offline reproduction and validation. Task 8 computation/reporting is complete with these explicit limits; derived tables are administrative analysis of the accepted review, not an additional human sign-off. Task 9 is next and has not been started.

## Standalone figures

[Copy exposure and endpoint labels](figures/copy_exposure_endpoints.png) · [SVG](figures/copy_exposure_endpoints.svg)

[TrustRAG support and core-usability transitions](figures/trustrag_support_core.png) · [SVG](figures/trustrag_support_core.svg)
