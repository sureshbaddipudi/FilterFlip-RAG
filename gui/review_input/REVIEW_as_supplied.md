# Tasks 12–13 re-review and GUI recommendations

Review date: 5 November 2026. This is a software/evidence review, not a new human scientific adjudication. No release, accepted review, original evidence or Desktop file was changed. No model run was started.

## Decision

**Task 12 and Task 13 are complete and jointly accepted within their documented scope. Task 11 remains pending Suresh’s manuscript review and the separately deferred presentation.** The 5 November joint-acceptance record takes precedence over older, frozen “pending” fields for this exact return; those historical fields need not be rewritten.

The earlier F2 return-checker finding is closed. Two reproducible GUI state-display defects remain worth correcting in a new version. Neither changes the saved scientific results or reverses the accepted handover. Optional usability work should follow those corrections.

## What was reviewed

- `../FilterFlip_Task13_Live_GUI_Handover_v2_0_2026-11-04`: the fresh delivery, its actual full v2.6 live application, handover tools, plan, tests and component snapshots.
- `../FilterFlip_Task13_Joint_Acceptance_2026-11-05`: the original returned evidence, trusted validation, joint decision, mechanical annotations and current status.
- Recent continuation-chat completion/acceptance records, including the distinction between the older twenty Task-12 answers and later v2.6 execution evidence.
- The actual GUI in a temporary local server: live selection page, saved Heather PN1 comparison and Findings and Evidence. No Run click. Temporary run directory remained empty; the review server was stopped afterward.

## Acceptance and evidence

The twenty Task-12 answers have accepted corresponding human review: **10 correct_supported, 9 abstention and 1 incorrect**. The incorrect false-claim answer is retained. These are selected Heather examples, not an overall model accuracy estimate. Later v2.6 answers do not automatically inherit these judgments.

Task 13’s returned packet validates against both the trusted delivery checksum and the actual supplied ZIP. Its 39 planned offline checks have complete logs/output bindings and PASS results. The separate joint decision supplies Suresh’s acceptance; the generic validator intentionally does not infer it.

Three citation annotations correctly identify the cast list as P5 rather than P4 while preserving the original comments and judgments. The separate scope annotation preserves the existence of Suresh’s earlier original-mode run without claiming additional tests. Reviewer dates and assistance declarations remain scoped to their actual records.

Existing scientific limits remain: selected Nano datasets; post-outcome scoring qualifications; R110 uncertainty; incomplete/truncated evidence where recorded; bounded TrustRAG stage-1 scope; and a mitigation trade-off rather than a generally secure defense. Task completion does not remove these limits or certify public deployment.

## Checks performed in this re-review

| Check | Outcome |
|---|---|
| Source delivery integrity after review | PASS: 2,733 files, 18 sealed components |
| Joint-acceptance verifier | PASS: original return unchanged; 265 mechanical checks |
| Canonical returned-package validator, trusted ZIP and checksum supplied | COMPLETE_RETURN / PASS; all 39 steps present |
| Application tests | 49 passed normally and 49 with Python `-O` |
| Handover/checker test discovery | 100 executions passed in each mode; **55 unique tests**, because 45 F2 tests are imported into another discovered module and run twice |
| Recorded-case rendering checks | PASS: all 59 cases, answers/passages and review precedence |
| Saved-study rendering checks | PASS: 531 case-condition views and 2,124 answer positions; missing reviews not inferred |
| UI-handler checks with synthetic replies | PASS: all nine live selections/exports; stop/cancel; saved export; stale-output clearing |
| Independent F2 negative check | Empty PASS ledger rejected: “Missing or reordered planned execution checks” |
| New synthetic GUI identity checks | Two display defects reproduced, described below |

Rendering/handler checks are software tests, not 531 manual browser inspections or new human outcome reviews. No new research generation, dependency installation or security scan was performed. The brief local-server disconnection during inspection was resolved by restarting the temporary review server; it is not treated as an application defect.

## Finding G1 — restore the actual selection when reconnecting to a running job (P2)

**Location:** `app/static/app.js`, bootstrap handler at line 114, and polling at line 16.

On page reload with an active non-default job, bootstrap calls `choices()` first, which selects the default Heather/variants/C combination. It then reconnects to the actual job and disables those selectors without replacing their values from the job’s `state.case_id`, `state.mode` and `state.condition`.

The synthetic check supplied an active other-case/mitigation/BN1 job. The screen controls remained Heather/variants/C and disabled. Polling reports the mode but does not display the case identity clearly. This can make a presenter or viewer associate an answer with the wrong question or setup.

**Recommended fix:** restore mode, available cases and condition from the actual run state before showing it; display a persistent run heading containing the question, case ID and condition. Avoid using the ordinary selection-change clearing path in a way that loses the active run. Add a reload/reconnect test with a non-default question and mode. Exports must retain the actual original run identity.

## Finding G2 — discard an old recorded-case reply after selection changes (P2)

**Location:** `app/static/app.js`, `reference` click handler at line 112 and selection-change path at line 13.

“Inspect recorded case” starts an asynchronous request. If the user changes the question before the reply arrives, `describe()` hides the panel, but the old response later renders and reopens it. The panel contains its own old question, so the data are not rewritten; nevertheless the selected question and displayed recorded case disagree.

The synthetic check delayed a Heather reply, changed the selector to another case, then released the old reply. The Heather panel reopened. This tests the real request handler with a render spy and synthetic transport, not a live network race.

**Recommended fix:** capture a selection/request generation number and discard responses when it changes, including when a fresh live run starts. The saved-condition tab already uses this approach (`savedRequest` in `study.js`). Add delayed-response tests for changing question, starting a run and issuing a second inspection.

## Recommended GUI improvements

Keep the current theme, full live tool and expandable evidence. No scientific settings need to change.

| Priority | Improvement | Benefit and acceptance boundary |
|---|---|---|
| First | Fix G1 and G2 | Keep the visible question, condition and result attached to the same run/request. |
| High | Add an all-nine-condition overview table | For one saved case, show C, BN1, BN2, PN1, PN2, BE1, BE2, PE1 and PE2 together: copied documents retrieved, passages kept, unfiltered/filtered answer summaries and the actual available review status. Choose reference or reproduction explicitly. Click a row for existing detail. Missing review must stay “not reviewed,” not be inferred from answer text. |
| High | Add a compact presentation view | Show question → retrieved passages → kept/removed passages → paired answers in one readable screen. Keep full text, identities and review records expandable. Show original/copied passage links from recorded metadata. Do not turn “designated answer passage removed” into an automatic strict-event verdict. |
| High | Update the current-status display in a new release | Findings currently highlights the scoped v2.4 acceptance from 31 October but does not show the subsequent Task-12/13 joint acceptance. Add a dated summary of the 5 November acceptance while keeping earlier scope/history. Task 11 must still say pending. |
| Medium | Make live/saved state unmistakable | The header still says “Local CPU · Fresh inference” on saved and Findings tabs. Make it view-specific: “Live computation,” “Saved study evidence,” or “Accepted findings.” Use separate execution and semantic-review labels; “Saved status: ok” means successful execution, not a correct answer. |
| Medium | Improve navigation and progress | Search the 59 questions; show the actual case/condition beside the result; show truthful stage and elapsed time/answers completed, using real events rather than a guessed percentage. |
| Later | Add run history and a readable summary export | Reopen completed runs without generation; label them saved runs. Keep the existing exact JSON export. A readable summary should include run ID, question, mode, condition, model/settings, timing and review status. Use safe server-selected IDs and bounded history; do not accept arbitrary file paths. |

The first three high-priority improvements would do the most for a final demonstration. A new theme, public hosting, automatic correctness judgments and new research modes are not needed for this GUI refinement. TrustRAG can remain clearly described as a separate recorded bounded study unless a separate live integration is explicitly planned and validated.

## Suggested bounded follow-up

1. Correct G1/G2 and add the two regression tests.
2. Add the saved nine-condition overview and compact presentation view.
3. Refresh the current acceptance summary and live/saved labels.
4. Run existing offline tests plus the new display tests; verify frozen research inputs/results unchanged. Package as a new version, preserving the accepted v2.6 release.
5. Have Suresh/Shradha check the new visual flows. Model reruns are not automatically necessary for display-only changes; run them only for a specific changed execution path or explicit acceptance requirement.

This review does not modify implementation or request new experiments. Task 11 remains with Suresh.

## Reproducing the two new checks

The included `checks/check_gui_identity.cjs` accepts the absolute path to the reviewed `app` directory as its first argument and runs with Node.js. It uses synthetic DOM/transport only and confirms the current defects. A successful test exit currently means both defects were reproduced; after a fix it must be converted into assertions for the correct behavior. `validation/gui_identity.json` records the observed mismatches.

The accompanying logs distinguish source integrity, returned evidence validation and synthetic software tests from human scientific judgment. No raw evidence or acceptance files are replaced by this report.
