# Task 4 — residual risks and follow-up

All 14 risks remain open or partially controlled. This assistant-authored mapping records no risk acceptance, formal severity score or measured likelihood. Priority labels guide the already approved coursework sequence; they do not manufacture CVSS values.

## R01 — Supported-answer availability loss

An accessible correct source is copied into a target-question corpus; joint filtering may remove all sufficient evidence and the downstream answer fails.

Controls: CTRL03, CTRL10. Evidence: EV12, EV13, EV14, EV15, EV18.

**Residual:** Eight events and 51 non-events among 59 selected cases form the primary assessment, not population success rate. Current mitigation is mixed and no general successful defense is established. Task-3 answers still need human review.

**Follow-up:** approved task(s) 7, 8, 11. Priority basis: observed research risk; Project-specific sequencing and observed gaps; not a CVSS score or measured likelihood.

Risk acceptance: not recorded by this mapping.

## R02 — Misleading or unsupported answer content

The generator may repeat planted false claims or wrong material, including mixed answers with accepted cores and incorrect extras.

Controls: CTRL05, CTRL10, CTRL11. Evidence: EV13, EV14, EV10, EV15.

**Residual:** Separate support, core/full completeness and wrong extras. CN adds two false-claim harms and avoids one in accepted selected tests; no deployment-grade truth guarantee.

**Follow-up:** approved task(s) 7, 8, 11. Priority basis: observed research risk; Project-specific sequencing and observed gaps; not a CVSS score or measured likelihood.

Risk acceptance: not recorded by this mapping.

## R03 — Indirect instruction influence

A separately approved instruction fixture enters retrieved context; obeying it could divert answers.

Controls: CTRL02, CTRL05, CTRL10. Evidence: EV13, EV14, EV10.

**Residual:** Zero marker successes on selected cases/policies is narrow. Exposure misses, the unresolved report 0/15 denominator and general semantic/obfuscated attacks remain limits.

**Follow-up:** approved task(s) 6, 7, 8. Priority basis: bounded research evidence; Project-specific sequencing and observed gaps; not a CVSS score or measured likelihood.

Risk acceptance: not recorded by this mapping.

## R04 — Dependency and model supply-chain compromise

Trusted packages/checkpoints/installation paths could be vulnerable, replaced or already malicious at the accepted hash.

Controls: CTRL03, CTRL12. Evidence: EV07, EV08, EV09, EV15.

**Residual:** 71 preserved baseline component/advisory records are not 71 demonstrated exploits. Per-advisory reachability, platform matching and separate-environment selected fixes remain open.

**Follow-up:** approved task(s) 5, 9. Priority basis: next security assessment; Project-specific sequencing and observed gaps; not a CVSS score or measured likelihood.

Risk acceptance: not recorded by this mapping.

## R05 — Evidence or reviewer provenance manipulation

A local actor changes answers, hashes, dates, attribution or current/historical overlays and presents them as signed-off.

Controls: CTRL03, CTRL09, CTRL10. Evidence: EV04, EV05, EV06, EV10, EV12, EV15.

**Residual:** Same-account rewrite is not prevented by hashes/chains. No independent signing/timestamping or authenticated reviewer service; no fabricated dates or acceptance.

**Follow-up:** approved task(s) 6, 7, 13. Priority basis: coursework follow up; Project-specific sequencing and observed gaps; not a CVSS score or measured likelihood.

Risk acceptance: not recorded by this mapping.

## R06 — Operational resource exhaustion

Long generation, repeated submissions, HTTP pressure or growing outputs consume CPU/RAM/disk.

Controls: CTRL06, CTRL07, CTRL08, CTRL11. Evidence: EV01, EV02, EV10, EV15, EV19.

**Residual:** UI quotas differ from CLI caps. No hard OS RAM/disk quota; polling can overshoot; full overload/failure-path proof absent. Research evidence suppression is a separate availability mechanism.

**Follow-up:** approved task(s) 6, 9. Priority basis: coursework follow up; Project-specific sequencing and observed gaps; not a CVSS score or measured likelihood.

Risk acceptance: not recorded by this mapping.

## R07 — Disclosure through local storage/export

Full passages, model outputs, reviewer information, archived contacts and absolute source paths are exposed to unintended recipients.

Controls: CTRL04, CTRL05, CTRL09. Evidence: EV03, EV04, EV09, EV10.

**Residual:** Private account/storage assumptions and intended exports only; no de-identification, encryption-at-rest or model-training privacy guarantee. No private corpus was evaluated.

**Follow-up:** approved task(s) 6, 11, 13. Priority basis: coursework follow up; Project-specific sequencing and observed gaps; not a CVSS score or measured likelihood.

Risk acceptance: not recorded by this mapping.

## R08 — Local-interface impersonation or bypass

A browser-origin attacker targets compute endpoints, or an untrusted local process talks directly to localhost/model services.

Controls: CTRL01, CTRL02, CTRL04, CTRL05. Evidence: EV01, EV02, EV20.

**Residual:** App token is not authentication and does not guard separate Ollama management APIs. No hostile-local-user or public/multiuser deployment approval.

**Follow-up:** approved task(s) 6, 9, 13. Priority basis: coursework follow up; Project-specific sequencing and observed gaps; not a CVSS score or measured likelihood.

Risk acceptance: not recorded by this mapping.

## R09 — Trusted artifact or configuration replacement

An operator/local compromise substitutes code, model, executable or source manifest, or exploits check-to-use races.

Controls: CTRL03, CTRL04, CTRL12. Evidence: EV01, EV02, EV07, EV15.

**Residual:** Pinned content is not authenticated origin or backdoor detection. Local configuration/OS account are trusted; broader race/adversarial loader assurance is not established.

**Follow-up:** approved task(s) 5, 9, 13. Priority basis: coursework follow up; Project-specific sequencing and observed gaps; not a CVSS score or measured likelihood.

Risk acceptance: not recorded by this mapping.

## R10 — Testing and release claims exceed supplied evidence

A report-only pass, shared backend hash or stale display text is treated as independent acceptance of all current UI/code/new answers.

Controls: CTRL09, CTRL10. Evidence: EV05, EV10, EV11.

**Residual:** Raw report scanner/coverage/probe evidence and UI release identity remain missing. Earlier exact-run acceptance is preserved; no blanket transfer to v2.4 or 88 answers.

**Follow-up:** approved task(s) 6, 7, 13. Priority basis: next testing reconciliation; Project-specific sequencing and observed gaps; not a CVSS score or measured likelihood.

Risk acceptance: not recorded by this mapping.

## R11 — Exceptional conditions produce misleading states

Partial/truncated/malformed data or native failure becomes completed, or public errors leak detail.

Controls: CTRL08, CTRL09, CTRL11. Evidence: EV01, EV02, EV10, EV15.

**Residual:** Synthetic branch checks and selected real runs do not exhaust backend/native/OS failures. Preserve fault semantics and retain uncertainty.

**Follow-up:** approved task(s) 6, 9. Priority basis: coursework follow up; Project-specific sequencing and observed gaps; not a CVSS score or measured likelihood.

Risk acceptance: not recorded by this mapping.

## R12 — Pretrained-model privacy uncertainty

Queries could reveal memorized training information or support inversion/membership inference in a different/private-data deployment.

Controls: CTRL04, CTRL06, CTRL12. Evidence: EV09, EV20.

**Residual:** No inversion/membership/privacy audit performed; no DP or training-data control. Current public fixed-fixture profile does not demonstrate or solve these attacks.

**Follow-up:** approved task(s) 11, 13. Priority basis: conditional inherited model risk; Project-specific sequencing and observed gaps; not a CVSS score or measured likelihood.

Risk acceptance: not recorded by this mapping.

## R13 — Training/update threats outside current lifecycle

Transfer learning, adaptive feedback skew or parameter poisoning would require a training/update path not present in this coursework pipeline.

Controls: CTRL02, CTRL03, CTRL12. Evidence: EV20, EV22.

**Residual:** Keep pretrained supply-chain risk separate. No training, fine-tuning, feedback learning or weight modification is implemented; reassess if those features are added.

**Follow-up:** approved task(s) 11, 13. Priority basis: scoped lifecycle exclusion; Project-specific sequencing and observed gaps; not a CVSS score or measured likelihood.

Risk acceptance: not recorded by this mapping.

## R14 — Untrusted output gains executable authority

Future tool execution/HTML rendering could turn model content into system actions, links or code.

Controls: CTRL02, CTRL05, CTRL11. Evidence: EV01, EV02, EV03, EV08, EV20.

**Residual:** Current generation has no tools/action executor and text is rendered literally. Privileged local workers are fixed application code, not LLM agency. Reassess before adding tool, upload or rendering features.

**Follow-up:** approved task(s) 6, 9, 13. Priority basis: conditional feature risk; Project-specific sequencing and observed gaps; not a CVSS score or measured likelihood.

Risk acceptance: not recorded by this mapping.

## Concrete handoff within the approved plan

| Task | Needed result | Current boundary |
|---|---|---|
| 5 — dependencies / selected fixes | Reconcile exact component versions/advisory aliases/platform constraints; assess reachability; choose justified fixes in a separate environment | Preserved 71 component/advisory records are version-match evidence. Do not silently patch accepted baseline or assume a listed fix preserves scientific outputs |
| 6 — testing reconciliation | Obtain raw commands, environment/source identity, logs, coverage/scanner units, probe results and an attributed addendum through Suresh | The testing PDF reports 42 tests, 55% overall coverage and additional checks; missing raw support stays missing |
| 6 — live-log reconciliation | Bind exact UI/static release; reconcile report 0/15 with supplied exposure/answer counts; record reasons/corrections for four pre-generation integrity failures if supplied | 27 attempts, 22 completed / 88 answers; backend byte identity does not prove UI version |
| 7 — outcome review | Review new reproduction, secondary and stage-1 answers; compare exact support, core completeness and wrong extras; resolve material disagreements jointly | Earlier exact four-run acceptance and all original attributions remain. Additional 19 completed runs / 76 answers are not automatically accepted |
| 8 — paired analysis | Integrate reviewed differences, negative results and insertion-versus-retrieval qualifications | No new event labels from lexical matches or execution success alone |
| 9 — selected security verification | Target the changed control and scientific compatibility in an isolated environment; document changed outputs and unresolved risks | No full research regeneration by default; no blanket closure from synthetic guards |
| 11 / 13 — final report and handover | Carry version/edition limits, uncertainty and scoped exclusions into final deliverables | Risk acceptance and reviewer decisions require an attributed record |

The supplied logs have four instruction runs / 16 outputs, ten marker-exposed outputs and zero literal marker matches. These counts do not establish the testing report’s 0/15 denominator. The accepted research result of nine instruction cases per policy with no observed marker successes remains a different, narrowly scoped result.

The four failed attempts report an index.html integrity mismatch before generation. Their intended cause/correction is unknown; do not label them deliberate successful tampering tests. Completed Heather neutral and false-claim runs exist. Historical GUI text that says these variants remain outside live validation needs reconciliation, rather than erasing the later intake or declaring every later answer accepted.

Training, parameter poisoning, privacy attacks, private model theft, public multi-user hosting and agent tools/actions are scoped out or conditional as specified in the category rows. Reassess if the corresponding feature/asset is introduced. Larger-dataset expansion and a new mitigation programme are deferred until after coursework; this list does not authorize them.
