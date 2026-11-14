# FilterFlip-RAG — Task 4: consolidated security-risk mapping

31 October 2026 · coursework checkpoint · prepared by the assistant for Suresh’s review


Task 4's mapping deliverable is complete: **46 taxonomy entries, 12 traced controls and 14 residual risks**. It covers six STRIDE threats and all ten entries in each approved OWASP Web, API, LLM and ML list. Inclusion means applicability was assessed; it does not mean 46 vulnerabilities were found, 46 tests passed, or any category was certified safe. Reviewer acceptance and any decision to accept residual risk are not recorded by this assistant-authored mapping.

The strongest research fit is **LLM08:2025 (Vector and Embedding Weaknesses)** and **ML01:2023 (Input Manipulation Attack)**. This is a project-specific interpretation: correct answer-bearing copies change retrieval/context composition and filtering, sometimes removing sufficient support. The main correct-copy experiment has no instruction override and does not demonstrate training-data or model-weight poisoning. Prompt-injection challenges, false-claim challenges and output-file tampering are separate scenarios.

## What the evidence establishes

The accepted primary result stays **8 events / 51 non-events / 0 unresolved classifications among 59 selected cases**. These are selected-case findings, with agreed post-outcome core-answer and mixed-answer rules; they are not a population attack-success rate. Eight cases have specific joint adjudication; the wider confirmation record does not turn every case into a blinded, unaided or jointly signed assessment.

Accepted Week-6 mitigation remains mixed: CN versus N has seven core-answer gains, eight losses and one uncertain comparison; two new false-claim harms and one avoided harm. **R110 remains uncertain.** New Task-2 comparisons and Task-3 answers await human review under Task 7. Task 3's 60 complete distinct responses / 72 logical positions establish execution and integrity, not semantic acceptance or full TrustRAG failure. Later TrustRAG stages were not evaluated.

The local application has request validation, fixed routes/process arguments, literal text rendering, release checks, private storage, bounded work, and partial/failure preservation. The mapping links these controls to named source symbols and existing test methods. Fresh offline Task-4 checks resolved **84 code/test references**, verified **53 unchanged source snapshots**, and checked **all 156 current v2.4 release entries**. They did not execute model inference, the application test suite, dependency scanners, or browser probes.

The recorded application logs contain 42 synthetic tests in normal and optimized Python; Task 3 has its own 19 synthetic checks in both modes. These retain their execution versions and scope. They are not added into a single security coverage score. Current source byte identity supports only the named unchanged surfaces. The earlier browser fixture does not validate every later JavaScript change.

## Where protection remains limited

- Local checksums and chained logs establish consistency, not authentic origin, external nonrepudiation, reviewer identity or absence of backdoors in approved assets.
- The browser request token is protection against cross-site requests, not user authentication. It does not guard the separate local Ollama API. The trusted operating-system account remains an assumption.
- Finite job/time/output limits reduce operational exposure. They do not impose hard RAM or filesystem quotas and do not prevent the research mechanism of losing answer support.
- Literal rendering and fixed subprocess arguments address application injection sinks. They do not prove resistance to instructions embedded in model context.
- The preserved 71 dependency component/advisory records require relevance assessment. They are not 71 demonstrated exploits or a fresh scan. Private training-data privacy, public hosting, model tools/actions, training and parameter updates were not evaluated.

## Editions and authority

- [STRIDE — STRIDE](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats): Threat-model taxonomy.
- [WEB — 2025](https://top10.owasp.org/2025/): 2025 release page verified.
- [API — 2023](https://api-security.owasp.org/editions/2023/en/0x11-t10/): 2023 edition page verified.
- [LLM — 2025](https://genai.owasp.org/llm-top-10/): Official index explicitly labels this list 2025; intentionally edition-pinned, no claim to assess every later AI/agentic framework.
- [ML — 2023 draft](https://owasp.github.io/www-project-machine-learning-security-top-10/): Official project still states draft; IDs are MLxx:2023; example risk scores/mitigation suggestions are not copied as project measurements.

Official pages were checked on 31 October 2026. The [OWASP ML project](https://owasp.org/projects/machine-learning-security-top-ten) explicitly describes the work as a draft. This mapping pins the ML:2023 identifiers rather than claiming a finalized certification standard. ML06 has an index/page title variation, preserved in its row. No OWASP or Microsoft endorsement of the project mapping is implied.

Latest explicit user instructions and the [current handover](sources/current_handover.md) govern scope. Attributed acceptance overlays govern scientific decisions; earlier report bytes and missing dates are preserved. The old Week-4 backlog and later demo reuse SEC identifiers for different meanings: see the qualified [crosswalk](LEGACY_ID_CROSSWALK.md). CTRL01–CTRL12 are navigation identifiers, not silent renames of old requirements.

## Read and reproduce this checkpoint

1. Read the [trust boundaries](THREAT_MODEL.md) and [execution profiles](EXECUTION_PROFILES.md).
2. Use the [46-entry mapping](RISK_MAPPING.md), [control traceability](CONTROL_TRACEABILITY.md) and [evidence register](EVIDENCE_REGISTER.md) to inspect the basis and limit of each claim.
3. Review the [14 residual risks and later-task handoff](RESIDUAL_RISKS_AND_FOLLOWUP.md). Use the [review guide](REVIEW_GUIDE.md) for acceptance; no new review has been attributed to Suresh or Shradha here.
4. Follow [README.md](README.md) to run the portable offline validator. [The saved check](validation/MAPPING_CHECK.json) records the authoring-machine integrity comparison.

Task 5 is next in the approved sequence: assess dependency relevance and selected fixes in a separate environment. Task 6 reconciles teammate testing evidence and release binding; Task 7 reviews new outcomes; Task 9 verifies selected security changes and scientific compatibility. Larger datasets and a new mitigation research programme remain deferred. Task 4 changes no application code, model, scientific input, accepted label, original review or Desktop file.
