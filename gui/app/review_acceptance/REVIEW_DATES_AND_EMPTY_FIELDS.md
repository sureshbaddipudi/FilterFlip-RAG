# Review dates and empty fields — 28 October 2026

## Updates based on Suresh's statements

- Demo-v2 return: Shradha and Suresh jointly adjudicated the four named runs and acceptance findings. Both review dates are 28 October 2026. The original report and machine snapshots stay unchanged; the new decision is a separate record.
- Current Week-4 summary: Suresh instructs using Shradha's corresponding date for his review. Ten individual-review cases use 14 October; eight cases with the later joint adjudication use 26 October. These dates were supplied retrospectively by Suresh on 28 October, not inferred from file timestamps.
- Week-6 scoring: 23 records now have discussion_date = 27 October, based on Suresh's explicit clarification. Corresponding scoring-review dates for both teammates are 27 October. Original first-pass outcome-review dates are unchanged.

## One review-date gap still needs a date

The additional 41 cases are covered by the later 59-case confirmation, but the actual date of that confirmation was never supplied. Its **recording date is 27 October**; this is not necessarily when the review happened. “Use Shradha's date for Suresh” cannot supply a date that is missing for Shradha too. CURRENT_REVIEW_SUMMARY.json therefore displays **Not supplied** for both, without a JSON null. If you confirm the actual date, both can be updated together. The later-confirmation date is also unknown for the original 18 cases, but their earlier individual/joint reviews already have known dates.

## Other empty fields and their meanings

| Fields | What was found | Proposed treatment / decision needed |
| --- | --- | --- |
| Week-4 original proposal joint_decision / decision_date / suresh_response | Eight original proposal entries remain blank inside preserved history. Current decisions and agreement dates already exist. | Keep original proposal intact; show completed decisions from the current agreement. No new review required. |
| Week-6 original scoring proposal suresh_decision / agreed_rule / discussion_date | Original proposals were written before Suresh's agreement. | Preserve source proposals; use current accepted agreement and dated update. |
| UCC: Answer preserved in copy? / All support lost after filter? | Two blanks in the 14 October review. Her explanation explicitly says the copy was not retrieved and these questions were not applicable. | Display “Not applicable — copy not retrieved” in a future friendly view. Do not invent yes/no labels. |
| support_qualifier / support_qualifier_meaning | Five pairs blank in the accepted scoring agreement. | These five are the uncertain-output decisions, separate from the 18 support-label decisions. Leave as not recorded/not applicable pending your preferred display wording; do not invent A/B/C qualifiers. |
| prior_individual_human_review | 41 cases have no separate earlier individual-review form. Later confirmation covers them. | “No separate earlier case-level form”; this does not mean human-unreviewed. |
| prior_joint_adjudication | 51 cases have no prior eight-case joint decision. | “No prior case-specific joint adjudication”; do not spread the new demo agreement across all 59 cases. |
| sample_reason / later_order_note / later_order_source | Empty descriptive or optional mechanism-check fields in historical records. | Keep historical absence explicit. Do not invent sampling reasons or claim an order check without evidence. |
| New live outputs: semantic_review = pending | Generation outputs are saved before humans review them. | Keep raw values intact; join the dated human-adjudication overlay by exact run ID. Future runs remain pending. |
| New demo return: assistance disclosure | Shradha identifies herself as decision-maker but does not fill a separate AI-assistance declaration. Suresh now attests that both manually reviewed all content, including generated reports. | Record that attestation accurately; do not turn it into a statement that no assistance ever occurred. |

MISSING_FIELDS_INVENTORY.json lists exact paths for 440 empty/null occurrences across three authoritative ledgers, including nested historical copies. This is not 440 pending decisions. Duplicate templates, old releases and scientific missing-data values are outside this focused inventory. Original records retain their source bytes and null values; the current readable summary uses explicit date/status text.

## Attribution

Current decisions identify the human reviewers and their manual-review responsibility. Historical source wording remains available so provenance is not rewritten. Manual review of an assisted draft does not erase how that draft was produced. This update makes no claim that all prior work was unaided.
