# Using the improved GUI

## What changed

- A nine-condition table compares C, BN1, BN2, PN1, PN2, BE1, BE2, PE1 and PE2 for one question.
- The **Answers shown in overview** selector distinguishes the original reference study from the later reproduction. The compact walkthrough follows the same choice. Full records retain both panels side by side.
- A condition button opens a compact view of the question, native-filter passage decisions and paired answers. Each passage opens to its exact text and identity. Copy labels come from recorded metadata, not an inferred answer-support judgment.
- **Presentation view** shows compact live-result cards and collapses full-evidence drawers; **Detailed view** restores those drawers. This is a display preference, not a filtering policy.
- The page header now distinguishes live demonstration, saved evidence and recorded findings.
- Exports retain all original evidence and identify the selected condition and overview source. They do not create new human judgments.

## A short walkthrough without generation

Start with the Heather example, Reproduction panel. In C and BN1, read the filtered answer alongside the unfiltered answer. Select PN1 and open its removed copy and original biography. Select PN2 to see two inserted copies and the recorded removal pattern. Then compare the exact-copy variants PE1/PE2. Discuss what the saved evidence shows for this case, without claiming that every added copy will be retrieved or every removed source means all semantic support is gone.

The table shows **documents retrieved / documents inserted**, not chunk counts. “2 / 2” means both inserted documents appeared in retrieval. The separate kept count concerns passages supplied to the answer model. Shortened answers have an ellipsis; the selected walkthrough and full records show complete saved text.

A review entry is copied from the selected study panel's condition record. A condition marked `not_applicable` is not a failed attack. The primary C/BN1/PN1 historical decision is case-level and stays in **Live demonstration → Inspect recorded case**. It is not copied onto each later response. “No condition-level review in this panel” does not cancel that historical decision. A linked response review, when available, is displayed separately from the condition endpoint.

`Execution: ok` describes a completed model request, not correctness. Truncated output stays truncated. The known PN2 review disagreement and incomplete response are retained. These screens do not change any accepted classifications.

## Using presentation view during a separately intended live demo

1. Choose the live mode, question and condition as usual.
2. Press **Presentation view**, then start the intended live comparison.
3. As results arrive, compact cards show each supplied passage as kept, removed or grouped out, followed by that policy's answer. The question/run identity remains visible. The setup panel collapses once results exist and can be reopened.
4. Open any passage tile or full-policy drawer to explain the evidence. The standard JSON export remains available.
5. Stop only if you intend to cancel the current job; partial output remains partial evidence.

All nine-condition/native mode generates two fresh answers; original/mitigation/challenge modes keep their existing four-answer behavior. The GUI does not replay saved answers in live mode or infer a strict event from answer text. A new live answer needs its own interpretation.

## What remains for a later small iteration

Question search, more detailed progress indicators, completed-run history and a readable summary export are not part of this release. The exact JSON exports remain available. Later TrustRAG stages, arbitrary corpus uploads, dependency-candidate adoption and larger datasets remain outside this release.

## Findings and Evidence in v2.8

Open the tab to see seven expandable sections. Start with the primary finding, then copy variants and reproduction. Continue to mitigation and challenges to explain why recovering an answer is not enough: both legitimate-answer loss and false-claim acceptance count. The TrustRAG stage-1 section contains a 12-case selector. Open a condition to read the exact saved unfiltered/filtered answers, review judgments and all retrieved passages. Output ordering is retained where it differs from retrieval order. U means unfiltered; T means TrustRAG stage 1. This recorded screen does not run TrustRAG or infer new judgments. Use the separate TrustRAG live mode for fresh filtering and answers.

The application-security section summarizes protections and remaining limits. Full controls and dated tests are in the release documents. Use START_HERE.md for the external private configuration and ARCHIVE_GUIDE.md for explicit offline archiving.

## v2.9 live TrustRAG and project overview

Follow START_HERE.md. The new live mode has 12 cases, three fixed-context conditions and two policies, U/T. It reruns filtering on verified saved embeddings; only Qwen answering and filtering are fresh. Empty output remains an empty document sent to Qwen; the GUI never synthesizes an abstention. Retained order is preserved, even when it differs from retrieval order. Every run has its own request hashes, raw responses, state and export. New decisions may differ from the recorded study and require fresh interpretation.

Project work and security links all 13 later tasks to supporting records and the appropriate live or saved view. Security documents are readable in the page. The report PDF is a draft awaiting review. Historical source documents retain their dates and original status; the current summary indicates later scoped acceptance. No task number by itself certifies all later GUI releases or scientific claims.
