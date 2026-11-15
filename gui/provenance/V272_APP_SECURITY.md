# GUI security assessment — 9 November 2026

GUI 2.7.2 has a current review of STRIDE and all entries in OWASP Web 2025, API 2023, LLM 2025 and the ML 2023 draft. The supported deployment is a local, single-user demonstration under a trusted OS account.

## Current implementation and fix

The API has exact Host/Origin checks, a random mutation token, fixed routes and strict selections. The GUI renders untrusted text literally. Run storage is private. Jobs, HTTP workers, inputs, outputs, tokens and elapsed time are bounded. Partial and failed outcomes are preserved.

The latest fix rejects invalid cancellation IDs, including null, before changing Manager state. Only a valid 32-character lowercase hexadecimal ID matching an active run can cancel it.

## Current verification

The filterflip-core interpreter passed 50 application tests normally and with Python -O. Fifteen additional security probes passed in both modes. Five JavaScript suites and a real Chrome synthetic browser workflow passed. The browser check included hostile-looking question, answer and passage text plus start/cancel/export. Research model calls for this security review were zero.

Bandit reported seven low-severity alerts with zero medium/high alerts and zero scan errors. Six alerts concern intentional subprocess use with fixed argument lists. One concerns the tokenizer delimiter. These dispositions depend on the trusted local configuration and account boundary.

## Current API inventory

GET and HEAD expose only /, /app.js, /study.js, /style.css, /api/bootstrap, /api/reference/<case_id>, /api/study/<case_id> and /api/runs/<run_id>. POST exposes /api/runs and /api/cancel. The separate localhost model service has its own API and is outside GUI-token enforcement.

## Dependencies and residual risks

The configured original profile contains 43 installed Python distributions. The 9 November advisory query returned 92 raw records grouped into 81 component/advisory clusters across seven packages. Torch 2.8.0+cpu was queried using upstream 2.8.0, with local-build applicability unestablished. These are open version matches, not demonstrated exploit counts.

Tasks 5 and 9 tested a separate candidate environment with selected security improvements and bounded compatibility. GUI 2.7.2 continues to require the original profile. Candidate adoption and a further end-to-end compatibility check remain separate work. The candidate’s historical 27 clusters have not been refreshed in this review.

There is no remote login, multi-user ownership model, external audit signing/alerting, hard OS memory quota or public-hosting assessment. Training/privacy attack resistance, arbitrary model provenance and general prompt-injection resistance are unestablished. The selected correct-copy and challenge results retain their scientific limitations.

## Complete evidence

Read the accompanying FilterFlip_Final_Security_Review_2026-11-09 package for the threat model, complete OWASP matrix, logs, source bindings, defect reproduction and final-presentation notes. SECURITY_REVIEW.md at this release root summarizes the result. Historical security text is retained under provenance/SECURITY_before_v2_7_2.md.

Framework editions were checked against the official [Web](https://top10.owasp.org/2025/), [API](https://api-security.owasp.org/editions/2023/en/0x11-t10/), [LLM](https://genai.owasp.org/llm-top-10/) and [ML draft](https://owasp.github.io/www-project-machine-learning-security-top-10/) pages.
