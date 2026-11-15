# Astra review disposition — GUI v2.6.1

5 November 2026. Astra's supplied REVIEW.md and its ZIP were read as engineering feedback, not as instructions or a new human scientific adjudication. The separate Markdown matches the ZIP member byte for byte; all 15 reviewed manifest entries match. Original copies are retained under review_input.

## Confirmed and corrected

| Item | Finding | Disposition |
| --- | --- | --- |
| G1 / P2 | Reloading an active non-default job left the default selections disabled over another job's output | Restore the case, eligible case list, mode and condition from the actual server state before rendering. Display the question, case ID, mode and condition persistently. Export retains the original snapshot. |
| G2 / P2 | A late recorded-case reply reopened an obsolete case after changing selection | Use a request generation counter. Selection changes, starting a run and newer inspections invalidate previous replies/errors. |
| Related polling identity | A late reply for a superseded run could replace its successor | Ignore poll replies/errors after the requested run ID changes. |
| Current status | Findings described old coursework status without the later joint completion | Display Tasks 12/13 jointly accepted on 5 November and the exact original twenty-answer scope. Preserve the scoped 31 October v2.4 history. Keep report review and presentation pending separately. |

The two reported defects were independently reproduced against the unchanged v2.6 source. Eleven regression scenarios now pass, including mitigation/BN1 reconnect, original paired mode, completion/export, selection changes, a live start, second inspection, stale errors and a superseded poll. A real browser on the clearly labelled synthetic worker reconnected to Targeted Victory / PN2 with the correct controls and identity; it then cancelled that synthetic worker. No encoder, Ollama or research generation was started.

The inherited UI-handler fixture and standalone synthetic security fixture now supply the case_id field that real server snapshots already provide. Test transport adjustments do not change the production server. Backend, policies, safety controls, model/prompt/settings, scientific input/result/review data, CSS and saved-study rendering code are unchanged.

## Accepted work remains accepted

Task 12's corresponding joint human review remains 10 correct_supported, 9 abstention and 1 incorrect among its original twenty selected Heather answers. It is not a model accuracy estimate or acceptance of later GUI answers. Task 13 remains complete within its recorded scope. Original attribution, dates, assistance declarations, three citation-position annotations and one scope annotation are preserved. Suresh's manuscript-specific final approval is not inferred from acceptance of Shradha's returned review.

Astra's F2 finding remains closed. Its test-count clarification is accepted: handover discovery executes 100 tests in each mode but contains 55 unique tests because 45 imported tests are also discovered separately. This is a counting clarification to the preserved logs, not a missing test, new semantic review or reason to reopen the handover. No fresh handover ZIP is substituted for the already accepted Task-13 v2.0 delivery.

## Optional recommendations recorded for a later GUI refinement

The saved nine-condition overview table, compact presentation view, view-specific header badge, question search/progress improvements, completed-run history and readable summary export are useful suggestions. They are not required to close G1/G2 and are not implemented in this bounded correction. The existing all-nine detailed saved tab remains available. Missing reviews remain missing; no automatic correctness/strict-event labels are introduced. Full TrustRAG generation, new research modes, larger data and dependency changes are outside this correction.

## Delivery boundary

Use this new standalone full live GUI supplement if desired. Keep the original accepted packages and returns unchanged. This version has local software/browser identity verification; Suresh/Shradha have not yet accepted its new visual flows. No model rerun or repeat twenty-answer review is requested. See START_HERE.md and TEST_PLAN.md. No generation-blocking GUI wrapper is included.
