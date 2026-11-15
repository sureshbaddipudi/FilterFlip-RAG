# GUI v2.8 security review

10 November 2026. Supported deployment: local, single user, trusted OS account. No public hosting, multi-user isolation or security certification is claimed.

## Changes and evidence

This release adds private external configuration checks, same-byte verification and loading of the retrieval script, bounded private security-request logs, an exclusive server/archive lock, explicit offline archiving, full application inventory checking, detailed packet-verification errors, extra browser headers and strict cancellation request shape. See REVIEW_DISPOSITION.md for each submitted finding and its treatment.

Existing protections remain: exact Host/Origin checks; a per-launch mutation token; fixed routes and selections; literal rendering of passages and answers; restrictive CSP; private runs; bounded requests, output, workers, jobs and time; owned-process cancellation; preserved failed/partial evidence; pinned assets; and offline generation settings. New research answers are not automatically accepted.

The current test evidence is in VALIDATION_REPORT.md and validation/v28. The unchanged saved data, policy file, native profile and request contract are checked in PRESERVATION.json. Backend changes are shown in validation/v28/BACKEND_CHANGE.diff. The v2.7.2 documents remain under provenance; historical acceptance is not acceptance of this update.

## Static scanner findings

The current production-Python scan reports **one medium and seven low findings**, with zero scan errors. No findings are hidden with suppression comments.

- **B102 / medium, safety.py:** deliberate execution of a frozen retrieval module. The implementation first reads a bounded byte sequence, verifies its SHA-256 against the recorded manifest, then compiles and executes that exact sequence. A mutation test confirms that replacement on disk after reading cannot substitute executed bytes. This is intentionally executable research code, not browser-supplied content. The manifest and trusted local account are trust anchors; this does not establish independent authenticity or defend against an account owner replacing code and hashes together.
- **B404/B603 / six low:** intentional subprocess imports and calls in backend, launcher and server. Commands use argument lists and the fixed interpreter/backend/model workflow; the browser supplies validated selections, not a shell command. External configuration remains trusted owner-only input.
- **B106 / one low:** the model tokenizer delimiter `<|im_end|>` is a protocol value, not a credential.

These are developer dispositions of warnings, not independent security acceptance. The raw JSON and scanner log are retained in validation/v28.

## Residual risks

Dependency advisories remain open. The 9 November filterflip-core inventory and the submitted filterflip-repro inventory differ; counts alone cannot establish fixes. No dependency update or new advisory lookup occurred in this release. See DEPENDENCY_RECONCILIATION.md.

Other processes running as the same OS user remain trusted. The bootstrap token is a browser request control, not human authentication. Direct local access to the separate Ollama API is outside GUI token protection. Config checks cover the file and immediate parent; arbitrary ancestor replacement and compromise of the owner are not addressed.

Audit logs are private and bounded but not signed or externally anchored. Logging failure produces a local warning and does not stop the application. Rotation retains at most three files of approximately 256 KiB each. Run evidence is separate and is never automatically deleted by this feature. Archiving requires stopping the server and choosing terminal runs explicitly; it is not a backup and does not add a disk quota.

Hard OS memory/filesystem quotas, full production-duration resource stress, training/privacy attacks, malicious-model analysis and general prompt-injection resistance remain outside this verification. Mitigation results and their harms remain visible; there is no claim of a generally successful mitigation.

## Framework mapping

THREAT_MODEL_AND_CONTROLS.md and OWASP_COVERAGE.md bundle the STRIDE review and Web 2025, API 2023, LLM 2025 and ML draft category mappings from the dated baseline, with the current logging/inventory additions. A mapped category may have partial controls, research-only evaluation, or be outside scope. Mapping is not certification or proof that every risk is resolved. FINAL_PRESENTATION_SECURITY_NOTES.md records what to explain when the final presentation is prepared.
