# GUI v2.9 security boundary

Local single-user research demonstration. Read the release-root SECURITY_REVIEW.md, THREAT_MODEL_AND_CONTROLS.md, OWASP_COVERAGE.md and VALIDATION_REPORT.md for controls, current tests and residual risks.

GET/HEAD: /, /app.js, /study.js, /findings.js, /project.js, /style.css, /api/bootstrap, /api/findings, /api/project, /semester-report.pdf, /api/reference/<case_id>, /api/study/<case_id>, /api/runs/<run_id>. POST: /api/runs and /api/cancel. No browser archive or arbitrary file endpoint. The separate local model API is outside GUI-token enforcement.

New TrustRAG mode: 12 fixed cases × C/BN1/PN1; original saved contexts/embeddings; fresh stage-1 decision and two Qwen requests. No labels or saved outputs in filtering/generation. Native order is preserved, with unique mapped indices and empty context allowed. Text budgets bound the known stemmer-input risk. Verified legacy support libraries have open advisory matches; see the root review. Existing native modes retain their request protocol and filtering body.

Config and runs must stay outside the release. Python -B is required to avoid extra bytecode. The accepted-history records remain separate from unreviewed new answers. Public/multi-user security, complete dependency closure and general mitigation effectiveness are not established.
