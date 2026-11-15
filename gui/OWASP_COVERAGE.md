> v2.9 addendum (10 November 2026): TrustRAG adds fixed-context fresh filtering/answering, verified legacy support libraries, an explicit 12-case/three-condition allowlist and text/token budgets. Project records and report PDF are fixed read-only routes. Legacy NLTK advisory matches remain open; see SECURITY_REVIEW.md. The dated mapping below is retained with this scope extension; no full-compliance claim is made.

# OWASP coverage of the final GUI

Updated 10 November 2026 for v2.8; framework sources checked in the 9 November assessment. Each row records applicability, implementation evidence and remaining limits. Category coverage means every entry was considered. Test counts describe executed checks, not a percentage of OWASP compliance.

The assessment uses Web 2025, API 2023, LLM 2025 and the ML 2023 draft identifiers. Official project pages were checked on the review date. The ML project continues to identify its work as a draft.

## Web Top 10 — 2025

[Official category list](https://top10.owasp.org/2025/). The application-specific judgments below are this review’s mapping.

| ID and risk | Current status | Implementation and evidence | Remaining limit |
|---|---|---|---|
| A01 Broken Access Control | Controlled within local scope | Exact route/case IDs, Host/Origin/token guards and private runs. HTTP path and mutation tests pass. | Multi-user ownership and account login are outside this deployment. |
| A02 Security Misconfiguration | Controlled within local scope | Loopback binding, CSP, no-store, nosniff, frame denial and offline settings. Current-route header tests pass. | Public hosting and a shared hostile host require a new configuration/design. |
| A03 Software Supply Chain Failures | Open residual risk | Pinned profile, hashes, 43-package inventory, current static scan and the dated 9 November dependency query. | 81 package/advisory clusters match versions. Candidate remediation has separate evidence. |
| A04 Cryptographic Failures | Partially applicable | Random run token and SHA-256 identities. Private run storage. | No TLS on local HTTP, release signing or encrypted evidence storage. Hashes provide consistency under trusted distribution. |
| A05 Injection | Application sinks controlled; model semantics open | Strict JSON/fields, fixed subprocess arguments and literal DOM text. Real-browser hostile markup remains text. | Retrieved instructions can still influence a language model; that is assessed separately under LLM01. |
| A06 Insecure Design | Bounded design assessed | Explicit trust boundaries, approved cases, compute limits and independent evidence assessment. | No generally effective answer-support mitigation has been established. |
| A07 Authentication Failures | Local-host assumption | OS account is trusted; browser token protects mutation requests. Guard tests pass. | Remote authentication, roles, sessions and account recovery are absent. |
| A08 Software or Data Integrity Failures | Partly controlled | Release/model/input identity checks, literal records, catalog validation and preserved partial states. Tampering tests pass. | A local attacker who can replace files and manifests defeats unsigned checks. |
| A09 Security Logging and Alerting Failures | Partly controlled | Run timestamps, requests, fingerprints, raw model responses and error states; private bounded HTTP security-event logs now record mutations and error responses. | External alerts and authenticated user attribution remain absent; diagnostic logs rotate. |
| A10 Mishandling of Exceptional Conditions | Tested controls with residual limits | Malformed outputs, unknown IDs, timeouts, failure and cancellation tests. Null-cancel defect fixed. | Every OS/native-library failure has not been exhaustively tested. |

## API Security Top 10 — 2023

[Official category list](https://api-security.owasp.org/editions/2023/en/0x11-t10/). The application-specific judgments below are this review’s mapping.

| ID and risk | Current status | Implementation and evidence | Remaining limit |
|---|---|---|---|
| API1 Broken Object Level Authorization | Local scope | Exact saved-case catalog and strict run IDs prevent arbitrary path selection. | No per-user object ownership for shared deployment. |
| API2 Broken Authentication | Local-host assumption | OS account and local connection boundary with browser request guards. | The mutation token is obtainable by trusted local clients; it is not a login credential. |
| API3 Broken Object Property Level Authorization | Tested | Exact POST property sets and string enums. Browser cannot set files, model, prompts or commands. Null cancellation rejected. | Configuration remains trusted local input. |
| API4 Unrestricted Resource Consumption | Partly controlled | One job, eight HTTP slots, archive/admission/time/byte/token limits. Admission and lifecycle probes pass. | No hard memory limit or hostile-host isolation. |
| API5 Broken Function Level Authorization | Local fixed-function scope | Fixed GET/HEAD/POST routes and rejected alternative methods. | No multi-role permission system. |
| API6 Unrestricted Access to Sensitive Business Flows | Partly applicable | Compute-job creation is the sensitive action and is serialized/bounded. | Repeated authorized jobs can still consume local resources. |
| API7 Server Side Request Forgery | Tested/design controlled | No URL argument from browser, fixed loopback model endpoints, refused redirects and disabled proxies. | Trusted configuration and separate local model service remain assumptions. |
| API8 Security Misconfiguration | Tested within local scope | Current routes have security headers and exact origin rules. | No public deployment hardening claim. |
| API9 Improper Inventory Management | Inventory updated | Current inventory includes /study.js, /findings.js, /api/findings and /api/study/<case_id>; fixed asset/route tests pass. | Bundled historical inventory described an earlier release; updated in this release. |
| API10 Unsafe Consumption of APIs | Partly controlled | Finite response read, strict JSON, model identity, stop reason, shape and token checks. | A well-formed model answer can still be false or unsupported. |

## LLM Top 10 — 2025

[Official category list](https://genai.owasp.org/llm-top-10/). The application-specific judgments below are this review’s mapping.

| ID and risk | Current status | Implementation and evidence | Remaining limit |
|---|---|---|---|
| LLM01 Prompt Injection | Research-tested; general risk open | Fixed system message treats documents as evidence; external text stays in a user message. Nine selected instruction challenges had zero followed instructions per policy. | The fresh prompt-role test verifies structure only. Neither it nor nine selected challenges establishes broad resistance. |
| LLM02 Sensitive Information Disclosure | Limited scope; privacy untested | Fixed public research passages and local storage; request path disclosures are rejected. | No private-training-data extraction, inversion or confidential-corpus evaluation. |
| LLM03 Supply Chain | Open residual risk | Pinned model/vendor/runtime identities and dated dependency analysis. | Current baseline advisories remain open. Model provenance and backdoors remain unassessed. |
| LLM04 Data and Model Poisoning | Adjacent threat; scoped evaluation | Hash-bound fixtures and deliberate corpus additions give controlled evidence for context manipulation. | Training and model-weight poisoning were not exercised. Correct-copy insertion should be described accurately as context/input manipulation. |
| LLM05 Improper Output Handling | Application sinks tested | Model output displayed with textContent; no SQL, shell or executable HTML sink. Real-browser and JavaScript literal-text checks pass. | Text may still contain misleading content, requiring semantic interpretation. |
| LLM06 Excessive Agency | Capability excluded | Answers have no tool-calling, filesystem-action or command-execution interface. Prompt contract includes no tools. | Any later agent/action feature requires a new threat assessment. |
| LLM07 System Prompt Leakage | Limited impact; no resistance evaluation | The experiment system prompt is fixed and contains no application secret. | The project has not measured prompt-extraction resistance. |
| LLM08 Vector and Embedding Weaknesses | Direct research focus; residual failure demonstrated | Controlled copies change retrieval and filtering. Paired answers, support review and fixed-index identity expose the failure chain. | Selected-case results and mixed mitigation outcomes establish no general safe vector-store defense. |
| LLM09 Misinformation | Directly measured; residual risk demonstrated | False-claim trials, saved paired answers and human judgments. CN introduces two harms and avoids one relative to N in the selected panel. | Application hardening does not make generated answers factually correct. |
| LLM10 Unbounded Consumption | Tested application bounds | Four attempts, 128 output tokens, bounded context/time/bytes, one job and archive limits. | Hard host memory/disk isolation remains absent. |

## Machine Learning Security Top Ten — 2023 draft

[Official category list](https://owasp.github.io/www-project-machine-learning-security-top-10/). The application-specific judgments below are this review’s mapping.

| ID and risk | Current status | Implementation and evidence | Remaining limit |
|---|---|---|---|
| ML01 Input Manipulation Attack | Direct research focus | C/BN/PN and exact-copy conditions measure input composition and support loss with fixed inference settings. | Selected inputs do not establish general adversarial robustness. |
| ML02 Data Poisoning Attack | Training scope excluded; retrieval context assessed separately | Fixed corpus/index identities and controlled source additions provide reproducible inference tests. | No training-data poisoning or learned-parameter update experiment. |
| ML03 Model Inversion Attack | Untested | Fixed pretrained public model and bounded queries are used. | No reconstruction of confidential training records assessed. |
| ML04 Membership Inference Attack | Untested | There is no supplied private training cohort or membership ground truth. | No privacy guarantee follows from model identity checks. |
| ML05 Model Theft | Limited applicability | Public local model, fixed GUI inference and no browser model-file export route. | Model extraction resistance and commercial model-IP protection were not evaluated. |
| ML06 AI Supply Chain Attacks | Open residual risk | Version inventory, file identities, separate candidate loading guard and advisory records. | Upstream origin, malicious weights and the full native stack remain outside the current test coverage. |
| ML07 Transfer Learning Attack | Workflow excluded; pretrained trust remains | GUI performs inference with fixed pretrained weights. | No user fine-tuning or transfer-training workflow tested; inherited pretrained backdoors remain possible. |
| ML08 Model Skewing | Update workflow excluded | Fresh runs do not update model weights or learn from feedback. | Feedback-driven poisoning and drift attacks would need testing if introduced. |
| ML09 Output Integrity Attack | Application records partly controlled | Raw replies, request fingerprints, literal rendering, run identity and preserved failure states. | Locally mutable evidence has no external signature. Byte integrity alone says nothing about answer truth. |
| ML10 Model Poisoning | Model-update workflow excluded; supply-chain risk remains | Fixed checked model identities and no upload/model-selection API. | A malicious but approved pretrained artifact could pass identity checks. |

## How to use this in the presentation

Show two or three concrete controls with test evidence in the main talk. Keep the full 40-row mapping as an appendix or accompanying report. State which risks were tested, which are controlled by the local deployment boundary, which are outside the workflow and which remain open. The six STRIDE rows appear in `THREAT_MODEL_AND_CONTROLS.md`.

The strongest research mapping is LLM08 and ML01. The separate instruction and false-claim challenge experiments inform LLM01 and LLM09. A copy that preserves the correct answer should not be presented as a demonstrated malicious instruction, training-data poisoning or model-weight poisoning.
