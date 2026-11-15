# FilterFlip-RAG final GUI security review

9 November 2026 · Current GUI reviewed against its implementation, threat model and security tests.

## Decision

The local, single-user GUI has implemented and tested security controls. The final checks found one cancellation-input bug, corrected in GUI 2.7.2. The application and additional security tests pass. Residual dependency and deployment risks remain open. This is a bounded engineering review for the coursework demonstration. Independent security certification and public-service readiness have not been established.

The assessed source is `FilterFlip_GUI_v2_7_1_Demo_2026-11-06`. The deliverable is `FilterFlip_GUI_v2_7_2_Security_2026-11-09`. Both are tied to hashes in `SOURCE_BINDING.json` and the release manifests. All work was performed in the Codex workspace. The only production-code modification is validation of the cancellation run ID in `app/server.py`.

## Fresh verification

| Verification | Result | What it establishes |
|---|---|---|
| Original GUI integrity | PASS, 381 packet files | The starting release matches its manifest |
| Original application suite | 49 tests PASS normally and with Python -O | Starting regression baseline |
| Additional security probes on original | 14 pass, 1 fails | Null cancellation accepted while idle |
| Corrected application suite in filterflip-core | 50 tests PASS normally and with -O | Regression protection plus the new cancellation case |
| Additional security probes on corrected GUI | 15 tests PASS normally and with -O | Real HTTP handlers and Manager checks, fixed-route safety, resource admission and model-response contract |
| Existing JavaScript suites | Five suites PASS | 59 recorded cases, 531 case/condition views, 118 overviews and 1,062 focused views, identity, export and literal rendering checks |
| Real Chrome browser | Six checks PASS | Actual page loading, saved navigation, hostile-text display, synthetic start/cancel/export and absence of JavaScript errors |
| Static production-Python scan | Seven low-severity findings, zero medium/high, zero scan errors | Six subprocess-use alerts reviewed against fixed argument lists and one tokenizer delimiter alert |
| Runtime dependency inventory | 43 distributions | Read from the configured filterflip-core interpreter without loading models |
| Fresh dependency advisory lookup | 92 raw records, grouped into 81 package/advisory clusters across seven packages | Version matches requiring assessment; open findings |
| Final release and ZIP integrity | See RELEASE_VERIFICATION.json | Exact tested code and packaged file identities |

Normal and optimized executions are repetitions of the same suites. They are not 130 independent security properties. Passing a software test does not establish model answer correctness. Research model calls during this review were zero.

The initial execution restrictions prevented local test sockets from opening. Those attempts are retained in the logs. The tests passed after localhost connections were permitted. The first browser attempt waited for a text element inside a collapsed evidence panel to become visible. The fixture was corrected to wait for that element to be present. The later browser run passed. These records are retained rather than presented as product defects.

## Finding F01 — cancellation with null run ID

**Observed behavior.** With no active job, a valid-token request containing `{"run_id": null}` received HTTP 200. The Manager compared null with its null active-job value and reported cancellation success.

**Impact.** Low-severity input-validation and state-reporting defect. The observed request falsely reported a successful cancellation. The reproduction required access to the local API and its run token.

**Fix.** Validate that the ID is a string containing exactly 32 lowercase hexadecimal characters before acquiring the cancellation lock or changing state. Then require an exact match with the active job. Invalid IDs receive HTTP 400. Valid cancellation still passes the lifecycle and browser tests.

**Evidence.** `logs/additional_before.log`, `logs/additional_after.log`, `logs/additional_optimized.log` and `app/tests/test_live.py::ControlTests.test_cancel_rejects_invalid_or_inactive_run` in the new GUI.

**Mapping.** Web A10 exceptional conditions, API3 property validation and STRIDE tampering. This engineering fix has no effect on retrieval, filtering policies, prompts or model settings.

## Security already implemented

- Localhost binding, exact Host and Origin checks, browser cross-site rejection and a random per-launch token for state-changing requests.
- Fixed API routes and strict case/mode/condition choices. Browser requests cannot provide commands, file paths, model choices or remote fetch URLs.
- Literal text display of passages and model responses, restrictive content security policy, frame denial and no-store response headers.
- Checked release/input/model identities, private run directories, atomic private JSON writes and restrictions on links and paths.
- One job at a time, bounded HTTP workers, request sizes, response bytes, tokens, time, run archives and output growth.
- Cancellation of owned process groups, preservation of partial output and explicit failed/interrupted/truncated states.
- Fixed model request structure, offline model-loading flags, refused redirects, disabled proxies and request fingerprints.
- Preserved evidence, recorded judgments and separate fresh-output interpretation.

The complete current threat model and the category-by-category review are in `THREAT_MODEL_AND_CONTROLS.md` and `OWASP_COVERAGE.md`.

## Dependency result and candidate status

The fresh lookup matches 81 package/advisory clusters in the configured baseline. Counts by package are certifi 1, filelock 12, Pillow 39, sentence-transformers 1, setuptools 1, Torch 8 and Transformers 19. `DEPENDENCY_FINDINGS.json` records the ID grouping. The local Torch version `2.8.0+cpu` was queried as upstream `2.8.0`, so CPU-build applicability requires separate analysis.

This query used pip-audit's PyPI advisory service. Historical Task 5 combined its own dated sources and produced 83 baseline clusters and 27 candidate clusters. Different source coverage and advisory aliases prevent interpreting the new count of 81 as two repaired vulnerabilities. All current matches remain open pending relevance assessment and selected remediation.

Tasks 5 and 9 already tested a separate dependency candidate, including a local SentenceTransformer loading guard and bounded scientific compatibility. The live GUI still requires the original profile, including sentence-transformers 5.1.0. The candidate's 27 advisory clusters and compatibility findings are historical evidence, not a new scan or deployment of that candidate. Candidate adoption requires an explicit profile change and a bounded end-to-end check.

The fresh scan does not cover OS vulnerabilities, the Python interpreter, Ollama binary vulnerabilities, vendored RAGDefender vulnerabilities, nested bundled distribution metadata or malicious pretrained weights. Inventory and hashes provide identity checks, while authenticity and backdoor assessment require additional evidence.

## Residual risks and decisions

| Risk | Current treatment | Remaining work |
|---|---|---|
| Dependency advisories | Fixed local assets and dated reachability analysis | Prioritize reachable paths and validate a candidate before adopting it |
| Other local users/processes | Trusted OS-account deployment assumption | Public or shared-host deployment needs authentication and stronger isolation |
| Separate Ollama service | Dedicated loopback port, owned service and identity checks | Application token does not protect direct local access to the model API |
| Audit authenticity | Hashes, timestamps, raw replies and request fingerprints | Local records can be changed by the account owner; external signing/anchoring absent |
| Resource exhaustion | Finite application budgets and timeouts | Hard memory and filesystem quotas absent; rate limits beyond one active job absent |
| Security-event visibility | Run and failure events retained | Rejected-request monitoring and external alerting absent |
| Prompt injection and false claims | Fixed challenge evaluation, evidence inspection and human interpretation | General resistance and a successful general mitigation remain unproven |
| Model privacy and training attacks | Fixed pretrained inference-only workflow | Membership inference, inversion, training poisoning and model extraction were not evaluated |

These items are recorded as residual risks. This report does not attribute a new human risk-acceptance decision to either researcher.

## Final presentation requirement

The final presentation must explain the STRIDE trust boundaries, implemented controls, concrete testing evidence and all four OWASP mappings. Use `FINAL_PRESENTATION_SECURITY_NOTES.md` when preparing it. Include the dependency caveat and distinguish the application protections from the research result about answer-support loss. Slides remain pending the agreed presentation instructions.
