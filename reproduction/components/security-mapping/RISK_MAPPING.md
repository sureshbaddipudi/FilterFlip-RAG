# Task 4 — complete applicability matrix

46 rows; six STRIDE and ten per OWASP list. This is the project-specific mapping of the supplied system. Each entry connects a scenario to controls, evidence, residual risk and scope. An excluded feature is not a safety pass. All entries have status `applicability_mapped_not_category_certified`.

Use [control traceability](CONTROL_TRACEABILITY.md) for exact code and test methods, [evidence](EVIDENCE_REGISTER.md) for execution attribution, and [residual risks](RESIDUAL_RISKS_AND_FOLLOWUP.md) for later tasks. IDs are edition-qualified. ML:2023 remains a draft.

## STRIDE — STRIDE

[Official source](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats). Threat-model taxonomy.

### S — Spoofing

Applicability: **applicable**.

Cross-origin client or forged reviewer identity targets browser jobs/review provenance.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL01, CTRL02, CTRL10 |
| Residual risks | R05, R08 |
| Attributed evidence | EV01, EV02, EV05 |

**Remaining gap:** No public account or authenticated reviewer system; request token is not login.

**Scope / reassessment:** No blanket exclusion; bounds stated in scenario/gap.

[Official taxonomy reference](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats).

### T — Tampering

Applicability: **applicable**.

Inputs, responses, release identities or review overlays are changed.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL02, CTRL03, CTRL09, CTRL10, CTRL12 |
| Residual risks | R04, R05, R09 |
| Attributed evidence | EV01, EV02, EV06, EV15 |

**Remaining gap:** Same-account/coordinated manifest rewrite and malicious approved artifacts remain possible.

**Scope / reassessment:** No blanket exclusion; bounds stated in scenario/gap.

[Official taxonomy reference](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats).

### R — Repudiation

Applicability: **applicable**.

An actor disputes a run, intervention or scientific review attribution.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL09, CTRL10 |
| Residual risks | R05, R10 |
| Attributed evidence | EV04, EV06, EV10, EV12 |

**Remaining gap:** Mutable local logs cannot provide independent nonrepudiation; record missing dates honestly.

**Scope / reassessment:** No blanket exclusion; bounds stated in scenario/gap.

[Official taxonomy reference](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats).

### I — Information Disclosure

Applicability: **applicable**.

Unintended file access or export exposes passages, reviewer details, local paths or model outputs.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL01, CTRL04, CTRL05, CTRL09 |
| Residual risks | R07, R08, R12 |
| Attributed evidence | EV01, EV02, EV04, EV09 |

**Remaining gap:** No confidential-training privacy assurance or hostile-local-user isolation.

**Scope / reassessment:** No blanket exclusion; bounds stated in scenario/gap.

[Official taxonomy reference](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats).

### D — Denial of Service

Applicability: **applicable**.

HTTP/model/disk load blocks local use; separately, evidence suppression denies a supported answer.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL06, CTRL07, CTRL08, CTRL10, CTRL11 |
| Residual risks | R01, R06, R11 |
| Attributed evidence | EV01, EV02, EV12, EV15, EV19 |

**Remaining gap:** Operational quotas do not solve research answer suppression or enforce hard RAM/disk isolation.

**Scope / reassessment:** No blanket exclusion; bounds stated in scenario/gap.

[Official taxonomy reference](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats).

### E — Elevation of Privilege

Applicability: **applicable with limited exposure**.

Browser selections or generated text could become paths, commands or privileged actions.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL02, CTRL04, CTRL05, CTRL08, CTRL12 |
| Residual risks | R08, R09, R14 |
| Attributed evidence | EV01, EV02, EV03, EV08 |

**Remaining gap:** Run trusted local code without admin privileges; no proof against compromised account/dependencies.

**Scope / reassessment:** No blanket exclusion; bounds stated in scenario/gap.

[Official taxonomy reference](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats).

## WEB — 2025

[Official source](https://top10.owasp.org/2025/). 2025 release page verified.

### A01:2025 — Broken Access Control

Applicability: **applicable with scope**.

Fixed routes/run objects and strict selections limit access within a local single-user service.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL01, CTRL02, CTRL04 |
| Residual risks | R07, R08 |
| Attributed evidence | EV01, EV02 |

**Remaining gap:** No per-user object ownership or remote authorization model.

**Scope / reassessment:** Remote/multiuser access is outside profile; reassess before exposure.

[Official taxonomy reference](https://top10.owasp.org/2025/).

### A02:2025 — Security Misconfiguration

Applicability: **applicable with scope**.

Loopback, headers, CPU/offline profile and configured private storage define deployment.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL01, CTRL04, CTRL05, CTRL06 |
| Residual risks | R06, R08, R09 |
| Attributed evidence | EV01, EV02, EV20 |

**Remaining gap:** Separate Ollama service is not protected by app nonce; hardening every local service is not demonstrated.

**Scope / reassessment:** No public hosting or arbitrary model/upload configuration.

[Official taxonomy reference](https://top10.owasp.org/2025/).

### A03:2025 — Software Supply Chain Failures

Applicability: **applicable with scope**.

Packages, vendored code and pretrained assets enter the trusted execution chain.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL03, CTRL12 |
| Residual risks | R04, R09 |
| Attributed evidence | EV07, EV08, EV09, EV15 |

**Remaining gap:** Open historical advisories, no signed release/provenance or general backdoor detection.

**Scope / reassessment:** Task 5 assesses findings; task 9 verifies selected changes.

[Official taxonomy reference](https://top10.owasp.org/2025/).

### A04:2025 — Cryptographic Failures

Applicability: **applicable with scope**.

Checksums protect consistency, random token supports CSRF, loopback transport carries local data.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL01, CTRL03, CTRL04, CTRL09 |
| Residual risks | R05, R07, R08 |
| Attributed evidence | EV01, EV02, EV20 |

**Remaining gap:** No TLS, storage encryption, signed audit or crypto protocol audit. Hashes are not signatures.

**Scope / reassessment:** No password/payment/remote session system; those paths need new design if introduced.

[Official taxonomy reference](https://top10.owasp.org/2025/).

### A05:2025 — Injection

Applicability: **applicable with scope**.

Untrusted corpus/model/browser text crosses request, render and process boundaries.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL02, CTRL05, CTRL11 |
| Residual risks | R03, R14 |
| Attributed evidence | EV01, EV02, EV03, EV08, EV14 |

**Remaining gap:** Literal rendering/fixed arguments address app sinks; they do not establish LLM instruction immunity.

**Scope / reassessment:** No SQL/database or model-generated shell executor is exposed.

[Official taxonomy reference](https://top10.owasp.org/2025/).

### A06:2025 — Insecure Design

Applicability: **applicable with scope**.

Correct-copy suppression and mitigation trade-offs affect useful answers despite valid inputs.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL02, CTRL06, CTRL10, CTRL12 |
| Residual risks | R01, R02, R03, R06 |
| Attributed evidence | EV12, EV13, EV14, EV15 |

**Remaining gap:** No generally successful mitigation; no population robustness claim.

**Scope / reassessment:** Approved fixed cases/profiles only; expansion/new mitigation research deferred.

[Official taxonomy reference](https://top10.owasp.org/2025/).

### A07:2025 — Authentication Failures

Applicability: **applicable with scope**.

Local origin/token gates govern browser jobs, with a trusted OS account.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL01, CTRL02, CTRL04 |
| Residual risks | R05, R08 |
| Attributed evidence | EV01, EV02, EV20 |

**Remaining gap:** No user login, role/session or authenticated reviewer model.

**Scope / reassessment:** Authentication feature tests are scoped out because no account system exists; not a public-service pass.

[Official taxonomy reference](https://top10.owasp.org/2025/).

### A08:2025 — Software or Data Integrity Failures

Applicability: **applicable with scope**.

Evidence, code/model identities and interpretation overlays require integrity.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL03, CTRL09, CTRL10, CTRL12 |
| Residual risks | R04, R05, R09, R10 |
| Attributed evidence | EV06, EV10, EV12, EV15 |

**Remaining gap:** Coordinated local replacement, provenance authenticity and unreviewed new outputs remain limits.

**Scope / reassessment:** No automatic acceptance of task-2/3 answers.

[Official taxonomy reference](https://top10.owasp.org/2025/).

### A09:2025 — Security Logging and Alerting Failures

Applicability: **applicable with scope**.

Run events/raw replies support reconstruction of jobs and interventions.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL09, CTRL10, CTRL11 |
| Residual risks | R05, R10, R11 |
| Attributed evidence | EV06, EV10, EV15 |

**Remaining gap:** HTTP access/security logging is suppressed; no centralized monitoring/alerting or external timestamps.

**Scope / reassessment:** No claim that local artifact logs constitute production monitoring.

[Official taxonomy reference](https://top10.owasp.org/2025/).

### A10:2025 — Mishandling of Exceptional Conditions

Applicability: **applicable with scope**.

Malformed responses, native faults, timeouts and cancellation must stay terminal/incomplete.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL02, CTRL06, CTRL07, CTRL08, CTRL11 |
| Residual risks | R06, R11 |
| Attributed evidence | EV01, EV02, EV10, EV15 |

**Remaining gap:** Coverage of all native/OS errors is not established; retain original failure bytes.

**Scope / reassessment:** Original upstream assertion use remains historical; new explicit guards are the tested surface.

[Official taxonomy reference](https://top10.owasp.org/2025/).

## API — 2023

[Official source](https://api-security.owasp.org/editions/2023/en/0x11-t10/). 2023 edition page verified.

### API1:2023 — Broken Object Level Authorization

Applicability: **applicable with scope**.

Allowlisted cases and validated run IDs constrain objects.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL01, CTRL02, CTRL04 |
| Residual risks | R07, R08 |
| Attributed evidence | EV01, EV02 |

**Remaining gap:** No cross-user ownership model; run IDs are not authorization credentials.

**Scope / reassessment:** Public/multiuser/remote business flows are outside this local profile; reassess before adding them.

[Official taxonomy reference](https://api-security.owasp.org/editions/2023/en/0x11-t10/).

### API2:2023 — Broken Authentication

Applicability: **applicable with scope**.

Origin/token checks protect local browser actions under trusted account scope.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL01, CTRL04 |
| Residual risks | R05, R08 |
| Attributed evidence | EV01, EV02 |

**Remaining gap:** No login/authenticated reviewer service; app token does not secure direct local model APIs.

**Scope / reassessment:** Public/multiuser/remote business flows are outside this local profile; reassess before adding them.

[Official taxonomy reference](https://api-security.owasp.org/editions/2023/en/0x11-t10/).

### API3:2023 — Broken Object Property Level Authorization

Applicability: **applicable with scope**.

Exact mutation fields keep paths, endpoints, models and reviewer flags out of browser-selected properties.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL02, CTRL10 |
| Residual risks | R05, R08, R09 |
| Attributed evidence | EV01, EV02 |

**Remaining gap:** Trusted operator config and review imports remain separate local boundaries.

**Scope / reassessment:** Public/multiuser/remote business flows are outside this local profile; reassess before adding them.

[Official taxonomy reference](https://api-security.owasp.org/editions/2023/en/0x11-t10/).

### API4:2023 — Unrestricted Resource Consumption

Applicability: **applicable with scope**.

Bounded HTTP work, one job and response/job/output caps constrain compute.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL06, CTRL07, CTRL08 |
| Residual risks | R06 |
| Attributed evidence | EV01, EV02, EV15 |

**Remaining gap:** No hard RAM/disk quota or public multi-client load assurance; CLI limits differ.

**Scope / reassessment:** Public/multiuser/remote business flows are outside this local profile; reassess before adding them.

[Official taxonomy reference](https://api-security.owasp.org/editions/2023/en/0x11-t10/).

### API5:2023 — Broken Function Level Authorization

Applicability: **applicable with scope**.

Fixed GET/POST inventory; unsupported methods and operations rejected.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL01, CTRL02, CTRL04 |
| Residual risks | R08, R14 |
| Attributed evidence | EV01, EV02 |

**Remaining gap:** No admin/multi-role model; separate Ollama management routes are not app routes.

**Scope / reassessment:** Public/multiuser/remote business flows are outside this local profile; reassess before adding them.

[Official taxonomy reference](https://api-security.owasp.org/editions/2023/en/0x11-t10/).

### API6:2023 — Unrestricted Access to Sensitive Business Flows

Applicability: **applicable with scope**.

Repeated job starts/cancels consume local compute and affect demonstration flow.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL01, CTRL02, CTRL06, CTRL08 |
| Residual risks | R06, R08 |
| Attributed evidence | EV01, EV02 |

**Remaining gap:** No per-user rate limiting, payment or account workflows; one-job control is a bound, not production fraud protection.

**Scope / reassessment:** Public/multiuser/remote business flows are outside this local profile; reassess before adding them.

[Official taxonomy reference](https://api-security.owasp.org/editions/2023/en/0x11-t10/).

### API7:2023 — Server Side Request Forgery

Applicability: **applicable with scope**.

Client endpoint is fixed loopback; browser cannot pass a destination; redirects/proxies refused.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL02, CTRL05 |
| Residual risks | R07, R08, R14 |
| Attributed evidence | EV01, EV02 |

**Remaining gap:** Trusted local configuration/executable compromise is outside this browser-destination guard.

**Scope / reassessment:** Public/multiuser/remote business flows are outside this local profile; reassess before adding them.

[Official taxonomy reference](https://api-security.owasp.org/editions/2023/en/0x11-t10/).

### API8:2023 — Security Misconfiguration

Applicability: **applicable with scope**.

Loopback bind, headers, fixed deployment/profile and private files.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL01, CTRL04, CTRL05, CTRL06 |
| Residual risks | R06, R08, R09 |
| Attributed evidence | EV01, EV02, EV20 |

**Remaining gap:** No public-hosting, all-service hardening or network TLS acceptance.

**Scope / reassessment:** Public/multiuser/remote business flows are outside this local profile; reassess before adding them.

[Official taxonomy reference](https://api-security.owasp.org/editions/2023/en/0x11-t10/).

### API9:2023 — Improper Inventory Management

Applicability: **applicable with scope**.

Browser and separate model-service interfaces need an accurate inventory.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL01, CTRL02, CTRL05, CTRL09 |
| Residual risks | R08, R10 |
| Attributed evidence | EV20, EV22 |

**Remaining gap:** Route inventory is the app surface plus used model client calls, not an exhaustive audit of Ollama management APIs.

**Scope / reassessment:** Public/multiuser/remote business flows are outside this local profile; reassess before adding them.

[Official taxonomy reference](https://api-security.owasp.org/editions/2023/en/0x11-t10/).

### API10:2023 — Unsafe Consumption of APIs

Applicability: **applicable with scope**.

Model replies are size/schema/token bounded and raw failures retained before interpretation.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL03, CTRL05, CTRL11 |
| Residual risks | R04, R11 |
| Attributed evidence | EV01, EV02, EV15 |

**Remaining gap:** Checked shape/identity is not semantic truth; backend/native failure coverage remains bounded.

**Scope / reassessment:** Public/multiuser/remote business flows are outside this local profile; reassess before adding them.

[Official taxonomy reference](https://api-security.owasp.org/editions/2023/en/0x11-t10/).

## LLM — 2025

[Official source](https://genai.owasp.org/llm-top-10/). Official index explicitly labels this list 2025; intentionally edition-pinned, no claim to assess every later AI/agentic framework.

### LLM01:2025 — Prompt Injection

Applicability: **applicable to instruction challenge**.

Separate instruction-bearing fixtures can influence generation; the main correct-copy attack contains no instruction override.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL02, CTRL05, CTRL10 |
| Residual risks | R03, R14 |
| Attributed evidence | EV13, EV14, EV10 |

**Remaining gap:** Evidence-only prompt is a constraint, not a complete defense. Selected marker tests do not prove semantic/obfuscated resistance.

**Scope / reassessment:** Do not relabel all eight correct-copy events as prompt injections.

[Official taxonomy reference](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).

### LLM02:2025 — Sensitive Information Disclosure

Applicability: **applicable with scope**.

Responses, full evidence/export and pretrained memorization may disclose data.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL04, CTRL05, CTRL09, CTRL12 |
| Residual risks | R07, R12 |
| Attributed evidence | EV04, EV09, EV20 |

**Remaining gap:** No private training/corpus privacy audit, inversion test or DP claim.

**Scope / reassessment:** Current public research fixtures; reassess before using confidential documents or personal training data.

[Official taxonomy reference](https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/).

### LLM03:2025 — Supply Chain

Applicability: **applicable**.

Packages, encoder/Qwen checkpoints and vendored defense code are trusted dependencies.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL03, CTRL12 |
| Residual risks | R04, R09 |
| Attributed evidence | EV07, EV08, EV15 |

**Remaining gap:** Pinned hashes identify approved content; unresolved dependency reachability and malicious-origin/backdoor risks remain.

**Scope / reassessment:** No installation or patch run performed by task 4.

[Official taxonomy reference](https://genai.owasp.org/llmrisk/llm032025-supply-chain/).

### LLM04:2025 — Data and Model Poisoning

Applicability: **conditional analogy not demonstrated training attack**.

Controlled corpus insertion changes inference-time retrieval context; future mutable data/embedding/training intake could enable poisoning.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL02, CTRL03, CTRL10, CTRL12 |
| Residual risks | R01, R02, R04, R13 |
| Attributed evidence | EV12, EV13, EV14, EV20 |

**Remaining gap:** The study never alters training data or weights, and does not demonstrate compromise of an ingestion service. Primary fit is LLM08/ML01.

**Scope / reassessment:** Training, fine-tuning, learned backdoors and malicious parameter updates are outside the experiment.

[Official taxonomy reference](https://genai.owasp.org/llmrisk/llm042025-data-and-model-poisoning/).

### LLM05:2025 — Improper Output Handling

Applicability: **applicable**.

Model/corpus text must not become browser HTML, commands or trusted actions.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL02, CTRL05, CTRL11 |
| Residual risks | R07, R14 |
| Attributed evidence | EV01, EV02, EV03, EV08 |

**Remaining gap:** Current literal text/fixed process code limits sinks; no blanket new-JS browser test or future action safety.

**Scope / reassessment:** No generated code execution, SQL sink, arbitrary hyperlink fetch or tool executor.

[Official taxonomy reference](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/).

### LLM06:2025 — Excessive Agency

Applicability: **scoped feature exclusion with reassessment**.

The model returns text; trusted application code starts a fixed worker, rather than obeying model-selected tool calls.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL02, CTRL05, CTRL06 |
| Residual risks | R08, R14 |
| Attributed evidence | EV01, EV02, EV20 |

**Remaining gap:** Model API itself is a separate trusted-local surface. Adding actions/tools/credentials would create a new boundary.

**Scope / reassessment:** No autonomous agent/tool/action execution; no adversarial agentic workflow evaluated.

[Official taxonomy reference](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/).

### LLM07:2025 — System Prompt Leakage

Applicability: **scoped low confidentiality requirement**.

The frozen system prompt is deliberately documented and contains no designed secret/access-control credential.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL01, CTRL05, CTRL12 |
| Residual risks | R07, R08, R12 |
| Attributed evidence | EV09, EV20 |

**Remaining gap:** No extraction-resistance evaluation. Do not place secrets in prompts or rely on prompt secrecy as authorization.

**Scope / reassessment:** Prompt disclosure is not a demonstrated confidentiality breach for this public template; reassess if secrets or hidden policy become assets.

[Official taxonomy reference](https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/).

### LLM08:2025 — Vector and Embedding Weaknesses

Applicability: **direct research applicability**.

Copies alter top-five context composition and joint filter geometry, suppressing sufficient answer evidence.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL03, CTRL10 |
| Residual risks | R01, R02, R09 |
| Attributed evidence | EV12, EV13, EV14, EV15, EV18 |

**Remaining gap:** No successful general defense or shared-tenant/vector-store privacy assessment. Stage-1 new answers remain pending human review.

**Scope / reassessment:** Mapping is an application-specific interpretation, not endorsement by OWASP or proof of every vector-store attack.

[Official taxonomy reference](https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/).

### LLM09:2025 — Misinformation

Applicability: **direct research applicability**.

Wrong/unsupported claims and the false-claim mitigation challenge affect answer trustworthiness.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL05, CTRL10, CTRL11 |
| Residual risks | R01, R02 |
| Attributed evidence | EV12, EV13, EV14, EV10, EV15 |

**Remaining gap:** Abstention/support loss is availability, not automatically misinformation. Mixed-answer cores and wrong extras remain distinct.

**Scope / reassessment:** Archived contact/medical/legal examples are source-relative evidence, not current advice; no truth guarantee from matching strings.

[Official taxonomy reference](https://genai.owasp.org/llmrisk/llm092025-misinformation/).

### LLM10:2025 — Unbounded Consumption

Applicability: **applicable**.

HTTP jobs and model response lengths/durations/output growth can exhaust resources.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL06, CTRL07, CTRL08, CTRL11 |
| Residual risks | R06, R11 |
| Attributed evidence | EV01, EV02, EV15, EV19 |

**Remaining gap:** Application/CLI bounds are finite but do not provide hard OS isolation; task-1 historical total active time is unknown.

**Scope / reassessment:** No paid remote inference or autonomous loops in this deployment; do not equate their absence with all resource risks solved.

[Official taxonomy reference](https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/).

## ML — 2023 draft

[Official source](https://owasp.github.io/www-project-machine-learning-security-top-10/). Official project still states draft; IDs are MLxx:2023; example risk scores/mitigation suggestions are not copied as project measurements.

### ML01:2023 — Input Manipulation Attack

Applicability: **direct research applicability**.

Answer-preserving copies change inference-time input composition and can alter filter/answer behavior.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL02, CTRL03, CTRL10 |
| Residual risks | R01, R02, R03 |
| Attributed evidence | EV12, EV13, EV14, EV15, EV18 |

**Remaining gap:** The result is for selected cases/configurations; schema-valid inputs may still induce semantic loss.

**Scope / reassessment:** No new adversarial training, threshold tuning or prevalence claim.

[Official taxonomy reference](https://owasp.github.io/www-project-machine-learning-security-top-10/docs/ML01_2023-Input_Manipulation_Attack.html).

### ML02:2023 — Data Poisoning Attack

Applicability: **scoped training lifecycle exclusion**.

The draft category targets training-data manipulation; the coursework changes retrieval inputs, not a training dataset.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL03, CTRL12 |
| Residual risks | R04, R13 |
| Attributed evidence | EV20, EV22 |

**Remaining gap:** Pretrained supply-chain uncertainty remains, but no training-data poisoning experiment or protection is claimed.

**Scope / reassessment:** No training/fine-tuning path; future mutable training ingestion requires reassessment.

[Official taxonomy reference](https://owasp.github.io/www-project-machine-learning-security-top-10/docs/ML02_2023-Data_Poisoning_Attack.html).

### ML03:2023 — Model Inversion Attack

Applicability: **conditional inherited model risk**.

A private-training deployment could expose reconstructed training information through outputs.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL04, CTRL06, CTRL12 |
| Residual risks | R07, R12 |
| Attributed evidence | EV09, EV20 |

**Remaining gap:** No inversion experiment or privacy protection measured; private files/query caps are not a proof.

**Scope / reassessment:** No sensitive training dataset under project control; do not declare pretrained models privacy-safe.

[Official taxonomy reference](https://owasp.github.io/www-project-machine-learning-security-top-10/docs/ML03_2023-Model_Inversion_Attack.html).

### ML04:2023 — Membership Inference Attack

Applicability: **conditional inherited model risk**.

A query process might infer whether a record belonged to model training data.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL04, CTRL06, CTRL12 |
| Residual risks | R07, R12 |
| Attributed evidence | EV09, EV20 |

**Remaining gap:** No training membership labels, membership audit or DP mechanism; retrieval-source membership is a different concept.

**Scope / reassessment:** No confidential training cohort used here; reassess with private data or model-serving changes.

[Official taxonomy reference](https://owasp.github.io/www-project-machine-learning-security-top-10/docs/ML04_2023-Membership_Inference_Attack.html).

### ML05:2023 — Model Theft

Applicability: **scoped asset exclusion with reassessment**.

Selected pretrained weights are already locally available; the app serves text and fixed evidence, not a proprietary weights endpoint.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL02, CTRL04, CTRL06 |
| Residual risks | R07, R08, R12 |
| Attributed evidence | EV01, EV02, EV20 |

**Remaining gap:** No extraction resistance evaluated; direct local model access and a compromised account are trusted-boundary assumptions.

**Scope / reassessment:** No proprietary model-IP protection objective or private-weight API; reassess if those assets are introduced.

[Official taxonomy reference](https://owasp.github.io/www-project-machine-learning-security-top-10/docs/ML05_2023-Model_Theft.html).

### ML06:2023 — AI Supply Chain Attacks

Applicability: **applicable**.

Trusted packages/checkpoints/vendored code can be vulnerable or originate from an untrusted supply chain.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL03, CTRL12 |
| Residual risks | R04, R09 |
| Attributed evidence | EV07, EV08, EV15 |

**Remaining gap:** The index uses AI Supply Chain Attacks while its category page says ML Supply Chain Attacks; same ML06:2023 ID. Hashes do not authenticate origin.

**Scope / reassessment:** No source authenticity/backdoor or universal dependency safety claim.

[Official taxonomy reference](https://owasp.github.io/www-project-machine-learning-security-top-10/docs/ML06_2023-AI_Supply_Chain_Attacks.html).

### ML07:2023 — Transfer Learning Attack

Applicability: **scoped training lifecycle exclusion**.

The project loads pretrained encoders/models but performs no local task-to-task fine-tuning or adapter training.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL03, CTRL12 |
| Residual risks | R04, R13 |
| Attributed evidence | EV20, EV22 |

**Remaining gap:** Inherited malicious checkpoint risk is handled as supply-chain exposure, not proof of a performed transfer-learning attack.

**Scope / reassessment:** No transfer-training pipeline is evaluated; reassess before fine-tuning/adapters.

[Official taxonomy reference](https://owasp.github.io/www-project-machine-learning-security-top-10/docs/ML07_2023-Transfer_Learning_Attack.html).

### ML08:2023 — Model Skewing

Applicability: **scoped training lifecycle exclusion**.

The draft describes training-distribution/feedback manipulation; this project has no feedback-based model update.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL02, CTRL03, CTRL10, CTRL12 |
| Residual risks | R01, R04, R13 |
| Attributed evidence | EV12, EV20, EV22 |

**Remaining gap:** A changed retrieval mixture or filter geometry is not evidence of changed learned parameters/training distribution.

**Scope / reassessment:** No online learning or feedback retraining; do not confuse ML08 with LLM08.

[Official taxonomy reference](https://owasp.github.io/www-project-machine-learning-security-top-10/docs/ML08_2023-Model_Skewing.html).

### ML09:2023 — Output Integrity Attack

Applicability: **applicable**.

A local artifact/API/export manipulation could change what a reviewer sees as model output.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL03, CTRL04, CTRL09, CTRL10, CTRL11 |
| Residual risks | R05, R07, R09, R10, R11 |
| Attributed evidence | EV04, EV06, EV10, EV15 |

**Remaining gap:** Byte/response integrity and semantic correctness are distinct; mutable logs have no external authenticity.

**Scope / reassessment:** The main research does not demonstrate an attacker rewriting raw answer files; this is tool/evidence integrity mapping.

[Official taxonomy reference](https://owasp.github.io/www-project-machine-learning-security-top-10/docs/ML09_2023-Output_Integrity_Attack.html).

### ML10:2023 — Model Poisoning

Applicability: **scoped parameter lifecycle exclusion**.

The draft category concerns malicious changes to model parameters.

| Trace | Reference |
|---|---|
| Controls / related tests | CTRL03, CTRL12 |
| Residual risks | R04, R09, R13 |
| Attributed evidence | EV15, EV20, EV22 |

**Remaining gap:** Known model hashes detect mismatch but cannot reveal a backdoor in the approved content.

**Scope / reassessment:** No weight modification or parameter-update experiment; corpus-copy insertion is not model-weight poisoning.

[Official taxonomy reference](https://owasp.github.io/www-project-machine-learning-security-top-10/docs/ML10_2023-Model_Poisoning.html).
