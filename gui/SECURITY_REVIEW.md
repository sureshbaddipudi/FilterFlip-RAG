# GUI v2.9 security review

10 November 2026. Local single-user demonstration under a trusted OS account. This is developer verification; independent v2.9 acceptance remains pending.

## Retained controls and new boundaries

All v2.8 protections remain: private external configuration, exact Host/Origin checks, mutation token, fixed routes/choices, text-only rendering, CSP, bounded jobs/requests/output/time, owned-process cancellation, private rotating security events, verified-byte retrieval loading, full application inventory and explicit offline archive operations. No browser upload, path, URL, command or model choice was added.

The new TrustRAG mode accepts only 12 fixed cases and C/BN1/PN1. Context text, cached SimCSE embeddings, filter functions and support-library files are hash-verified. Reviewed answers, support labels and historical kept masks are excluded from live computation. The six native filter functions are unchanged; their source hashes are retained. Current decisions preserve native ordering, including empty outputs. The existing fixed Qwen request protocol is reused. No later TrustRAG stages or fresh retrieval/embedding generation are claimed.

The additional read-only routes are /api/project, /project.js and /semester-report.pdf. They serve fixed packaged material only. Project records render as literal text; the PDF is the unchanged semester draft. Project documents and old provenance may contain historical paths and review attribution. They are not public-redacted artifacts.

## Dependency findings: bounded, not closed

The TrustRAG process imports the recorded supporting runtime (NLTK 3.9.2, rouge-score 0.1.2, absl-py 2.3.1 and click 8.1.8) from verified local copies. The user's installed environment is not modified. This is newly included runtime surface in the GUI, so it must be disclosed separately from the unchanged native-filter environment.

The dated four-package scan returned **73 raw NLTK advisory rows representing 41 ID/alias groups**; the other three queried packages had no matches in that query. This is not a full dependency-tree or exploitability audit. Raw JSON and scan metadata are retained in validation/v29. Baseline core findings remain open; their earlier 81-group count is not a new whole-v2.9 scan.

ROUGE uses the NLTK Porter stemmer, so a stemmer complexity advisory concerns an active call path. The application restricts this path to exactly five hash-verified study passages, at most 32 KiB per passage and at most 256 ASCII alphanumeric characters per normalized token. Browser-selected free text cannot reach it. Tests reject overlong tokens/passages; all 36 original contexts pass. This bounds the demonstrated input surface without changing the recorded filtering function. It does not patch NLTK or close all advisory matches. Downloaders, corpus-loading services and arbitrary NLTK parsing are not exposed as GUI operations; library-wide reachability and compatible upgrades remain future work.

The installed candidate environment evaluated in Task 9 is still not deployed. No general claim of safe dependencies, general prompt-injection resistance, a successful mitigation or public-service readiness is made.

## Verification and static analysis

81 application tests pass normally and with optimized Python; 15 additional security checks pass in both modes. Five existing JavaScript suites and 14 real-browser synthetic checks pass. The original stage-1 outputs match for all 36 contexts. Three bounded real integration runs completed with six fresh Qwen responses, including reordered and empty contexts; these responses remain unreviewed semantically.

The production-code Bandit scan (excluding tests and the separately inventoried vendored runtime) reports one medium and seven low findings, zero scan errors. B102 concerns the retained deliberate execution of verified retrieval-script bytes. Six subprocess alerts are reviewed against fixed argument lists; B106 is the tokenizer delimiter, not a secret. This scan is not a clean bill of health for all bundled upstream source. Raw findings remain unsuppressed.

## Remaining limits

No shared-host authentication, hard OS memory/filesystem quota, signed external audit anchoring, public hosting assessment, full-scale stress testing, broad model privacy/training attack analysis or complete dependency remediation. The owner can alter both local code and unsigned manifests. Successful model execution does not establish answer correctness. See VALIDATION_REPORT.md and ACCEPTANCE_CHECKLIST.md; earlier acceptance is scoped to earlier artifacts.
