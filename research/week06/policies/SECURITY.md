# Week-06 runner threat model and security coverage

Scope: offline preparation and a local command-line research runner on a trusted single-user Linux/POSIX host. No web UI/API is exposed by the runner. Its optional owned model daemon binds loopback only. This is developer assessment, not independent certification. The existing demo's checks do not substitute for these controls.

## STRIDE

| Threat | Boundary and controls | Evidence / limitation |
|---|---|---|
| Spoofing | Independent reviewer declaration bound to exact draft; fixed local model/version/digest and binary hash | Pending/changed-draft tests pass. Reviewer name/role is a declaration, not cryptographically authenticated identity; inspect the actual teammate return. |
| Tampering | Original manifest checks; prepared/source/code hashes; output partitions; journal hash chain; fresh destinations | Altered-byte, duplicate-JSON, index and journal tests. Hashes need trusted manifests; a compromised local account can replace both. |
| Repudiation | Attempt reservation before execution, request hashes, cache mapping, failures and review attribution | Durable flushes; orderly-resume tests; faulted/uncertain sessions cannot silently retry. No external signed audit trail. |
| Information disclosure | Confined reference reads, no arbitrary URL input, no proxy/redirect, fixed loopback model service | Path/symlink and request-schema checks. All local benchmark data is accessible to the local account; no confidential multiuser service is claimed. |
| Denial of service | Per-call timeout, phase attempt/time limits, bounded JSON, sequential worker, owned process-group kill | Synthetic timeout/cap tests. Actual native/Ollama integration and descendant cleanup remain unverified in this increment. |
| Elevation of privilege | No shell interpolation or passage execution; fixed worker scripts; only verified local model assets; no remote-code trust | Hostile text treated as data, model/system settings fixed. Operator-supplied installed Ollama binary is trusted code and its hash is recorded. No OS sandbox against a malicious local executable. |

Trust boundaries: source files→preparer; drafts→independent review; reviewed inputs→policy; indices→evaluator; supervisor→native worker; answer queue→owned local model service. Policy functions receive texts/scores only; target IDs, poison flags, expected answers and judgments are attached by the evaluator after decisions.

## OWASP Web Top10:2025 and API Top10:2023

This register considers every category for this CLI architecture. Conditional applicability is not a passing security test. Every row still needs independent review; no vulnerability scan or full security audit is claimed.

| Category | Applicability and implementation evidence / gap |
|---|---|
| Web A01 Broken Access Control | Local filesystem trust; confined reads, protected output roots, no application roles. Shared/remote access would need a new authorization design. |
| Web A02 Security Misconfiguration | Offline native environment, fixed loopback generation, occupied-port refusal, no UI-triggered execution. Actual daemon configuration still needs integration testing. |
| Web A03 Software Supply Chain Failures | Vendor/model source hashes and original dependency versions; binary hash recorded. No dependency upgrade/download. OS/runtime CVE scanning and signed builds remain absent. |
| Web A04 Cryptographic Failures | SHA-256 integrity, no credentials introduced; HTTP limited to loopback. Hashes are neither signatures nor encryption. |
| Web A05 Injection | JSON parsing, no shell execution, literal corpus text and frozen system prompt; injection fixtures only reach an untrusted document field. This tests the model's behavior; it does not assume prompt-injection immunity. |
| Web A06 Insecure Design | Explicit STRIDE boundaries, blinded policy inputs, review gate, preserved negatives and bounded workload. Trusted-host scope is essential. |
| Web A07 Authentication Failures | No user account/session feature. Human-review provenance is declared, not identity-authenticated. Remote operation is outside scope. |
| Web A08 Software or Data Integrity Failures | Frozen/prepared/review/request hashes, startup checks, complete partitions, exact-request reuse and journal checks. Trust origin must be established separately. |
| Web A09 Security Logging and Alerting Failures | Durable local attempt/result/fault log and visible process errors. No central monitoring or tamper-proof external log. |
| Web A10 Mishandling of Exceptional Conditions | Stop on errors/truncation/token mismatch; no automatic retry or fail-open fault fallback. Explicit singleton bypass is a measured baseline behavior, never a safety guarantee. |
| API1 Broken Object Level Authorization | No remote case/run objects. Local output paths and run identities are confined/checked; local filesystem permissions apply. |
| API2 Broken Authentication | No authenticated remote API exposed. Loopback model endpoint is not authenticated against another local process; trusted-host assumption documented. |
| API3 Broken Object Property Level Authorization | Fixed worker/request schemas; policy has no evaluator fields. Review file is the explicit path for fixture approval; unrelated parameters cannot set verdicts. |
| API4 Unrestricted Resource Consumption | Input/output limits, attempt/time caps, sequential calls, cached requests and process cancellation. Limits persist on orderly resume, not across intentionally separate run folders; study accounting must include all runs. |
| API5 Broken Function Level Authorization | Fixed worker operations per phase; no shell/admin/review-write endpoint. Adding remote controls would need role enforcement. |
| API6 Unrestricted Access to Sensitive Business Flows | Exclusive lock, immutable run identity, no automatic retry after uncertain work. Research-owner oversight must prevent fresh directories evading total study caps. |
| API7 Server Side Request Forgery | No supplied URL; exact local endpoints version/tags/chat, no proxies/redirects or remote fetches. |
| API8 Security Misconfiguration | Strict settings/schema/model identity, local-only owned service and finite response reads. Owned service startup/cleanup still needs live verification. |
| API9 Improper Inventory Management | CLI commands and fixed internal operations documented in README; no public or obsolete API routes are added. |
| API10 Unsafe Consumption of APIs | Bounded JSON, response completion/length/token checks, saved raw response provenance and identity rechecks. Semantic correctness remains human review. |

## Review and recovery rules

Never turn a timeout, malformed response, missing record or unreviewed answer into a successful defense result. An ambiguous half-written journal, stale lock, changed code or uncertain attempt stops resumption. Preserve the original run, diagnose the issue, and create an attributed amendment with consumed budgets before any recovery. The user owns development; teammate review remains independent. All delivered review fields are pending.
