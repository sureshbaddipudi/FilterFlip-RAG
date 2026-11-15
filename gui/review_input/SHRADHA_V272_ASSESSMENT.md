# Secure Software Engineering Assessment: FilterFlip-RAG GUI v2.7.2

*Functional verification and security review using OWASP, MITRE and STRIDE*

- **System assessed:** FilterFlip_GUI_v2_7_2_Security_2026-11-09 (FilterFlip-RAG GUI 2.7.2, released 9 November 2026)
- **Assessment date:** 10 November 2026
- **Prepared by:** Shradha, with AI-assisted code review and testing (Claude Code)
- **Frameworks:** STRIDE threat model; OWASP Top 10 and OWASP Top 10 for LLM Applications; MITRE ATT&CK and MITRE ATLAS
- **Status:** Draft for course submission. Technique and category IDs should be checked against the current framework tables before submission (see Limitations).

## 1. Executive summary

FilterFlip-RAG GUI 2.7.2 is a local, single-user web application that demonstrates a research study on retrieval-corpus poisoning and filter defences in a RAG pipeline. It was assessed for functionality and for secure software engineering (SSE) practice.

**Overall result.** All functions that were exercised worked as specified. The application shows strong secure-by-design practice for a local tool: loopback-only binding, strict input validation, text-only rendering, a restrictive Content-Security-Policy, hash-verified inputs, bounded jobs and private file permissions. No High or Critical weakness was found. Static analysis found no medium or high issues. Fifteen findings are recorded (4 Medium, 8 Low or Low-Medium, 3 Informational), and most are consequences of the stated trust model (one trusted local user).

| Area | Result |
|---|---|
| Functional testing | Pass. 50/50 bundled unit tests; all 4 live modes completed; cancel works; guided UI walkthrough (sections A to F) reported as passing by the tester. |
| Input and API fuzzing | Pass. Over 35 malformed or hostile requests were rejected with 4xx and no data leaked; server stayed healthy after a 30-connection flood. |
| Static analysis (Bandit) | 0 high, 0 medium, 8 low (all reviewed: accepted risk or false positive). |
| Secret scan | No credentials found. Personal paths and usernames appear in 5 shipped files. |
| Dependency scan (pip-audit) | 82 known advisories across 5 packages (Pillow 39, transformers 28, filelock 12, certifi 2, sentence-transformers 1). Open; reachability judged low but not proven. |
| Findings | 0 Critical, 0 High, 4 Medium, 8 Low-Medium or Low, 3 Informational (Section 7). |

**Most important recommendations.** (1) Make the config file owner-only and have the launcher refuse a writable config, because it decides which binaries are executed (W1). (2) Close or formally risk-accept the open dependency advisories (W2). (3) Add an audit log of state-changing requests (W3). (4) Require the run token on read routes if the tool is ever run on a shared host (W4).

## 2. Scope, method and limitations

### 2.1 Scope

In scope: the release folder FilterFlip_GUI_v2_7_2_Security_2026-11-09, namely the Python server (server.py), the job backend (backend.py), the input and integrity layer (safety.py), the policy code (policies.py), the saved-study loader (study.py), the static front end (index.html, app.js, study.js), the bundled tests, and the release and integrity tooling.

Out of scope: the research claims themselves (whether the attack or defence works scientifically), TrustRAG (not present in this GUI; see Section 4.3), the operating system, the Ollama binary and the pretrained model weights, the vendored RAGDefender library, and any public or multi-user deployment.

### 2.2 Method

- **Orientation:** read the documentation, change log and release manifests; mapped the code.
- **Functional testing:** ran the bundled test suite; launched the server with a throwaway configuration outside the release; exercised the API; ran live generations in all four modes; cancelled a running job; and a guided browser walkthrough (checks A to F).
- **Dynamic security testing:** hand-written fuzzing of every route (body, header, framing, path, method) plus connection-level checks.
- **Manual code review:** all of server.py, backend.py, safety.py, policies.py, study.py, common.py, configure.py, launch.py and the three front-end files, read in full.
- **Automated analysis:** Bandit 1.9.4 (SAST), pip-audit 2.10.1 against the real runtime environment, and a regex secret scan.
- **Threat modelling:** STRIDE applied to a data-flow description of the system, mapped to OWASP, MITRE ATT&CK and MITRE ATLAS.

### 2.3 Limitations (read before relying on this report)

- **The browser walkthrough (A to F) was performed by the tester, who reported all checks as passing. No screenshots were captured**, so those UI results are tester-reported and not independently evidenced.
- The 2400-second job timeout, the 128 MB output cap, the disk-space guards and the 60-run archive cap were reviewed in code but **not exercised**.
- pip-audit was run with the Python environment named filterflip-repro (41 packages). The authors audited filterflip-core (43 packages) and also report Torch and setuptools advisories that this audit did not show. The two environments differ and the results have not been reconciled.
- The secret scan used regular expressions, not an entropy-based scanner such as Gitleaks, so it can miss unusual secrets.
- The authors' own security documents (THREAT_MODEL_AND_CONTROLS.md, OWASP_COVERAGE.md) are referenced in their SECURITY_REVIEW.md but sit in a separate ZIP; they were not available for this review. SECURITY_REVIEW.md itself was read.
- OWASP, ATT&CK and ATLAS identifiers were written from the assessor's knowledge and were not checked online. OWASP Top 10 numbering follows the 2025 edition and the LLM list follows the 2025 edition; verify all identifiers before submission.
- A configuration file (app/config.local.json) appeared inside the release folder at 09:24 on 10 November 2026, was not part of the sealed manifest, and was not created by the assessor. The tester moved it out before the UI walkthrough. It is recorded as finding W1.
- Model answers were not judged for correctness. Passing execution status does not mean a model answer is right.
- **TrustRAG is not part of this GUI** (Section 4.3). Whether that omission is intentional has been put to the project team and the answer is pending; the TrustRAG details in this report come from a separate handover folder that is outside the assessed release.

## 3. System overview

The application is a Python standard-library HTTP server (http.server, no web framework) with a vanilla-JavaScript front end. It listens on 127.0.0.1:8767. For a live comparison it starts a child process (backend.py) that loads a frozen retrieval index and an encoder, applies RAG-defence filter policies, starts a dedicated Ollama service on 127.0.0.1:11437, and asks the qwen2.5:3b model for answers. Results are written to a private run folder and polled by the browser.

### 3.1 Data-flow diagram (text form)

```text
  [Browser]  --1. GET page, /api/bootstrap (token)-->  [server.py  127.0.0.1:8767]
     |                                                      |  2. POST /api/runs, /api/cancel (token)
     |<--- 6. poll /api/runs/<id> (JSON, no token) ---------|
     |                                                      v
     |                                           [Manager: one job, locks, limits]
     |                                                      | 3. spawn (own process group)
     |                                                      v
     |                                             [backend.py child process]
     |                                              | 4a. read, hash-check, load
     |                                              |     frozen package, encoder, vendor code
     |                                              | 4b. start dedicated Ollama (127.0.0.1:11437)
     |                                              v
     |                                       [Ollama + qwen2.5:3b]
     |                                              | 5. results, logs
     |                                              v
     |                                  [run folder (0700), JSON files (0600)]

  Trust boundaries:  TB1 browser/local network <-> server
                     TB2 server <-> child process and filesystem
                     TB3 child <-> Ollama service
                     TB4 frozen package/config files <-> code that executes them
```

### 3.2 Assets

- Integrity of the study evidence, review records and run results (research validity).
- Integrity of the executed code, config and vendored libraries.
- Availability of the local machine (CPU, disk) during a demonstration.
- Confidentiality is of low importance: no user data, credentials or personal data are processed.

## 4. Functional verification

### 4.1 Feature inventory and results

| ID | Feature | Method | Result |
|---|---|---|---|
| F1 | Bootstrap, token, 59 cases | API request | Pass |
| F2 | Live run, original mode | API, full run | Pass (45 s, 4 answers ok) |
| F2 | Live run, variants mode (condition C) | API, full run | Pass (about 1 minute, 2 answers ok) |
| F2 | Live run, mitigation mode | API, full run | Pass (35 s, 4 answers ok) |
| F2 | Live run, challenge mode | API, full run | Pass (55 s, 4 answers ok) |
| F3 | Single-job lock (second start gives 409) | API | Pass |
| F4 | Run status and event polling | API and UI | Pass |
| F5 | Cancel running job (kills model child, frees port 11437, keeps partial evidence) | API | Pass |
| F5 | Cancel with null, malformed, unknown or finished run ID | API | Pass (400) |
| F6 | Timeout, size and disk limits, 60-run cap | Code review | Reviewed, not exercised |
| F7 | Saved nine-condition viewer, walkthrough, source toggle | API; UI checks B1 to B10 | Pass (UI tester-reported) |
| F8 | Recorded-case viewer (59 cases) | API; UI check E1 | Pass (UI tester-reported) |
| F9 | Presentation and Detailed view toggle | UI checks E3, E4 | Pass (tester-reported) |
| F10 | JSON export (live and saved) | UI checks B9, D5 | Pass (tester-reported) |
| F11 | Reconnect to an active job after reload | UI check D8 | Pass (tester-reported) |
| F12 | TrustRAG run or per-case view | Code, page text and release notes searched | Not available in this GUI (see 4.3) |
| Unit | Bundled test suite (5 files) | unittest | 50 of 50 pass |

### 4.2 Release integrity

The application-level hash check (safety.verify_release) passed for all 279 listed files. The packet-level check tools/verify_packet.py initially failed with the unhelpful message "unlisted or missing files" because app/config.local.json (not in the manifest) was present inside the release; after the file was moved out, the tester proceeded with the walkthrough. This is recorded as W1 and W9.

### 4.3 TrustRAG coverage

TrustRAG is not available in the GUI. This was checked in three places and they agree:

- **Code:** the only live modes are original, variants (all nine conditions), mitigation and challenge. The only filter in backend.py is RAGDefender (ragdefender.RAGDefender, task type single_hop), which the UI and the study call the native filter. The exact-copy (E) and near-copy (CN) policies group copies first and then run the same RAGDefender filter. The four policies offered are U (no filter), N (native), E and CN.
- **Page text:** the Findings and Evidence tab states "There is no TrustRAG answer-generation mode in this GUI."
- **Release notes:** GUI_GUIDE.md lists TrustRAG live generation among the items outside this release.

TrustRAG appears in the GUI only as one summary paragraph on the Findings and Evidence tab: a separate 12-case, stage-1 comparison with 60 fresh study responses for 72 logical records, strict endpoint 5 met, 6 not met and 1 uncertain, background-qualified endpoint 3 met, 8 not met and 1 uncertain. The tab itself says this is not full TrustRAG and not a matched defence ranking. There is no per-case TrustRAG view.

**Assessment.** The omission is consistent with the release's stated scope, so it is recorded as a scope note, not as a defect. It would become a gap only if the course or project requirements expect TrustRAG to be demonstrable in the GUI. That question is listed in Section 12 (Q1 and Q2).

### 4.4 Worked example: NanoMSMARCO:1028652

The question "who invented corn flakes" is one of the 59 cases in the GUI and is available in all four live modes, the saved nine-condition viewer and the recorded-case viewer, always with the native filter. The TrustRAG results for this case exist only in the study's TRUSTRAG_CASES.md (Task 13 handover, components/task08), not in the assessed release. In that table T is the TrustRAG stage-1 selection and U is the unfiltered context.

| Condition | U support | T support | U core usable | T core usable | T kept (of 5) | Native kept (of 5) |
|---|---|---|---|---|---|---|
| C (clean) | sufficient | sufficient | yes | yes | 5 | 3 |
| BN1 (background copy) | sufficient | sufficient | yes | yes | 3 | 4 |
| PN1 (answer-source copy) | sufficient | partial | yes | no | 1 | 4 |

- **Recorded endpoint:** strict endpoint met for TrustRAG and not met for the native filter.
- **Why:** in PN1, TrustRAG removed the answer passage and its inserted copy and kept one weaker passage, so the TrustRAG answer abstained. The native filter kept 4 of 5 passages.
- **Source caveat:** the answer rests on one archived passage whose dates and allocation of invention credit were not independently verified.
- **Authors' flag:** the authors flagged this case because TrustRAG produced a strict event where the native filter did not.
- **How to read it:** the native and TrustRAG results come from different studies. The authors note a generation-history difference, so this is not a controlled comparison and does not support a general ranking of the two defences.

## 5. Security controls observed

These are strengths that were confirmed by code reading, tests, or live probes.

| Control | Evidence |
|---|---|
| Loopback-only binding, exact Host and Origin allowlist (blocks DNS rebinding), cross-site fetch rejection | Verified: forged Host and Sec-Fetch-Site: cross-site both returned 403 |
| Per-launch random token (43 characters) with constant-time comparison for all state-changing requests | Verified: missing, wrong and non-ASCII tokens returned 403; code uses hmac.compare_digest |
| Strict input validation: fixed case, mode and condition whitelists; no browser-supplied paths, commands or URLs; unknown fields rejected; duplicate JSON keys and NaN rejected | Verified: 11 malformed-body cases all returned 400; unit tests cover duplicate keys and non-finite values |
| Request hardening: header, path and body size caps, Transfer-Encoding and duplicate Content-Length rejected, 3-second socket timeout, 8 connection slots, methods other than GET/HEAD/POST return 405 | Verified: 431, 400, 405 responses; idle socket closed after 3.0 s; 30-connection flood did not stop the server |
| Text-only rendering: front end builds the DOM with textContent; no innerHTML, eval or document.write found | Read: pattern search of all JavaScript found no such sink |
| Strict response headers: Content-Security-Policy (default-src 'none', script-src 'self'), X-Frame-Options DENY, nosniff, no-referrer, no-store, CORP same-origin | Verified on the live server |
| Safe file handling: atomic private writes, symlink refusal, size limits, run folders 0700 and files 0600, path confinement | Verified: file modes observed; unit tests cover symlink and oversized input |
| Hash-verified inputs: release files, retrieval script, vendored defence code and encoder files are hash-checked before use; allow_pickle=False; trust_remote_code=False; HTTP redirects refused; proxies disabled | Read in backend.py |
| Bounded execution: one job at a time, 2400 s timeout, 128 MB output cap, disk-space guard, 60-run cap, dedicated Ollama on a fixed port, process-group kill on cancel | Cancel verified; limits read, not exercised |
| Honest evidence handling: execution status is separated from correctness; disagreements between human reviews are preserved and displayed rather than overwritten | Seen in UI and code (study.js) |
| Static analysis clean at medium and high severity | Bandit: 0 high, 0 medium, 8 low |

## 6. STRIDE threat model

STRIDE was applied to each trust boundary in Section 3.1. The system's stated trust model is a single trusted local user on a private machine, not a public or multi-user service. Ratings below are judged against that model and against what changes if it were broken.

| STRIDE | Threat | Where | Existing mitigation | Residual risk / finding |
|---|---|---|---|---|
| Spoofing | Another local user or process on the same host obtains the token and acts as the operator | TB1: GET /api/bootstrap returns the token without authentication | Host and Origin allowlist; loopback binding | Medium on a shared host (W4) |
| Spoofing | A web page in the user's browser attacks the local server (CSRF, DNS rebinding) | TB1 | Origin and Host checks, Sec-Fetch-Site, token, JSON-only content type | Low: all probes rejected |
| Tampering | Modify config or code so a different Python or Ollama binary runs | TB4: config.local.json mode 664 inside release; paths executed without ownership or permission check | Hash check on .py files at startup | Medium (W1) |
| Tampering | Replace the retrieval script between hash check and load | TB4: backend.py hashes then loads from path | Hash-verified manifest | Low to Medium (W5) |
| Tampering | Alter the release manifest and the code together | TB4: manifest lives beside the code, checked only at startup | SHA256 manifests | Low to Medium (W6) |
| Tampering | Inject data via malformed API input | TB1 | Strict validation, whitelists | Low: all fuzz cases rejected |
| Repudiation | No record of who started or cancelled which run | server.py: log_message is a no-op | Per-run state, events and request fingerprints | Medium (W3). Rejected requests are not recorded at all. |
| Information disclosure | Another local user reads run results via GET routes (no token) | TB1 | 128-bit random run IDs; loopback | Low to Medium (W4) |
| Information disclosure | Usernames and directory layout leak through shipped files | 5 shipped files contain /home/... paths | None | Low (W11) |
| Information disclosure | Secrets in code or config | Entire release | n/a | None found |
| Denial of service | Exhaust CPU, disk or the run quota | TB1, TB2 | One job, timeouts, size and disk caps, 8 slots, 3 s socket timeout | Low. Archive cap blocks use until runs are cleared (W8). |
| Elevation of privilege | Config controls executed binaries; a writable config yields code execution as the user | TB4 | None beyond file ownership | Medium (W1) |
| Elevation of privilege | Application token does not protect the dedicated Ollama port 11437 | TB3 | Loopback, owned service, identity checks | Low to Medium (W4, W7) |
| Elevation of privilege | Vulnerable dependency exploited via model or tokenizer loading | TB4: pretrained files parsed by transformers, sentence-transformers | Offline mode, hash-verified model files | Low in context; 82 advisories open (W2) |

## 7. Findings register

Severity is the assessor's judgement for the stated deployment (one trusted local user, loopback). "Basis" says whether the finding was verified by running something, read in code, or both.

| ID | Sev. | Finding and evidence | Mapping | Recommended fix |
|---|---|---|---|---|
| W1 | Medium | Config file controls executed binaries and is unprotected. app/config.local.json lists the python and ollama_binary that are executed. It was group-writable (mode 664) and sat inside the sealed release; nothing checks its owner or permissions. A writer gains code execution as the user. Basis: verified. | OWASP A02 Security Misconfiguration; A01 Broken Access Control. STRIDE T, E. ATT&CK T1574 Hijack Execution Flow. | Keep config outside the release; at startup refuse a config that is not owned by the user or is writable by group or others; resolve and log the executed paths. |
| W2 | Medium | Open dependency advisories. pip-audit reports 82 advisories in 5 packages in the runtime environment (Pillow 39, transformers 28, filelock 12, certifi 2, sentence-transformers 1). The authors list 81 clusters and also Torch and setuptools; environments differ. Pillow and filelock are not imported by the application code. Basis: verified (scan); reachability is inferred, not tested. | OWASP A03 Software Supply Chain Failures (LLM03 Supply Chain). ATT&CK T1195. | Test a bounded upgrade (Pillow 13, transformers 4.53+, certifi 2026.10.18) and re-run the suite; otherwise record a dated risk acceptance with reachability analysis. |
| W3 | Medium | No audit trail. server.py disables all request logging (log_message does nothing). There is no record of which request started or cancelled a run, and rejected or hostile requests leave no trace. Basis: read. | OWASP A09 Security Logging and Alerting Failures. STRIDE R. ATT&CK T1070 Indicator Removal (absence of logs). | Log method, path class, status and run ID to a private file; log rejected requests; rotate. |
| W4 | Medium | Local trust only. The run token is issued by an unauthenticated GET, GET routes for run results need no token, and the dedicated Ollama port 11437 has no authentication. On a shared host another user could start jobs or read results. Verified: bootstrap returned the token to a plain curl call. Basis: verified. Documented by the authors as a residual risk. | OWASP A01 Broken Access Control. STRIDE S, I, E. | State the single-user assumption prominently; for shared hosts use a Unix-domain socket or a session cookie, require the token on GET run routes and use filesystem permissions for the Ollama socket. |
| W5 | Low-Med | Check-then-use gap. backend.py hashes run_retrieval.py then loads it from the file path, so a swap between the two steps would not be detected. Basis: read. | OWASP A08 Software or Data Integrity Failures; CWE-367. STRIDE T. | Read the bytes once, hash them, then compile and exec those same bytes. |
| W6 | Low-Med | Self-attesting integrity. RELEASE_MANIFEST.json lives beside the code it protects and is checked only at startup. verify_release only flags unlisted *.py files. Basis: read. | OWASP A08. STRIDE T. | Publish the manifest hash out of band or sign it; check the full file list. |
| W7 | Low | Hardcoded versions and port. Ollama version 0.34.2, the model digest and port 11437 are hardcoded, and the port check is racy (probe, then start). Pinning is good for reproducibility but makes upgrades brittle. Basis: read. | OWASP A06 Insecure Design. CWE-367. | Bind to an OS-assigned port or a Unix socket; make version pins configuration. |
| W8 | Low | Archive cap becomes a self-inflicted denial of service. After 60 runs the tool refuses new runs until a person clears the folder. No retention policy. Basis: read. | STRIDE D. LLM10 Unbounded Consumption (inverse). | Add a documented cleanup command or age-based retention. |
| W9 | Low | Poor error reporting in the packet check. tools/verify_packet.py prints only "FAIL: unlisted or missing files" and not which file. Basis: verified. | SSE: maintainability and usability of security tooling. | Print the offending paths. |
| W10 | Low | Missing hardening header and plain HTTP. No Permissions-Policy header; HTTP not TLS. Acceptable on loopback. Basis: verified. | OWASP A02. | Add Permissions-Policy and Cross-Origin-Opener-Policy; document that TLS is required if bound beyond loopback. |
| W11 | Low | Personal paths and usernames shipped in documents and data (START_HERE.md, app/config.local.json, acceptance/SOURCE_BINDINGS.json, app/data/SOURCE_PROVENANCE.json, provenance/SOURCE_BINDINGS.json). Basis: verified. | OWASP A01 (information exposure); LLM02 Sensitive Information Disclosure (minor). | Replace with placeholders before distribution. |
| W12 | Low | Group-writable files. All 385 files in the extracted release were mode 664 (umask 0002). Probably an extraction artefact, but it weakens the sealed-release claim. Basis: verified. | OWASP A02; A08. | Ship and extract with 0644/0755 and document it. |
| W13 | Info | Prompt injection and RAG poisoning remain only measured, not solved. The system prompt tells a 3B model to treat the document as untrusted, which the model cannot enforce; the instruction_append challenge shows this. This is the research subject, and the authors state that general mitigation is unproven. Basis: design analysis. | OWASP LLM01 Prompt Injection; LLM04 Data and Model Poisoning; LLM08 Vector and Embedding Weaknesses. ATLAS AML.T0051; AML.T0070 RAG Poisoning. | Keep the claim bounded (as the authors do); add provenance or approval gating for any corpus that feeds a real deployment. |
| W14 | Info | Bandit low findings: 5 x B404 (subprocess imported), 2 x B603 (subprocess without shell; arguments come from config and constants, not from the browser) and 1 x B106 (false positive: a tokenizer special token). Basis: verified. | CWE-78 (not exploitable here, but see W1). | Accept; add a nosec comment with the reason. |
| W15 | Info | Inconsistent error status. A cancel request containing extra fields returns 404 "Unknown operation" while other bad cancel requests return 400. Also, the server does not URL-decode paths (a percent-encoded case ID returns 404). Both are harmless and arguably safer. Basis: verified. | Input handling consistency. | Return 400 consistently. |

## 8. Framework mapping

### 8.1 OWASP Top 10 (web) and OWASP Top 10 for LLM Applications

| Category | Assessment | Findings |
|---|---|---|
| Broken Access Control | Partial. Token plus Host checks suit the local model; no access control for other local users. | W4, W11 |
| Security Misconfiguration | Good defaults and headers; config handling is weak. | W1, W10, W12 |
| Software Supply Chain Failures | Hash-verified model, vendor and retrieval files; dependencies not updated. | W2 |
| Cryptographic Failures | Not applicable. SHA-256 is used for integrity only; no secrets are stored or transmitted. | None |
| Injection | Strong. Whitelists, no shell with browser input, no database, text-only DOM. | W14 (accepted) |
| Insecure Design | Strong. Deliberate local-only design with documented limits. | W7 |
| Authentication Failures | Single token per launch; no user accounts by design. | W4 |
| Software or Data Integrity Failures | Good, but self-attesting. | W5, W6 |
| Security Logging and Alerting Failures | Weak. No request logging or alerting. | W3 |
| Mishandling of Exceptional Conditions | Good. Errors are generic; partial results preserved; null cancel ID fixed in 2.7.2. | W15 |
| LLM01 Prompt Injection | By nature unsolved; this is the research subject. | W13 |
| LLM03 Supply Chain | Hashed model files; dependencies outdated. | W2 |
| LLM04 Data and Model Poisoning | The study measures corpus poisoning; fixed corpus and approved fixtures only. | W13 |
| LLM05 Improper Output Handling | Strong. Model output is rendered as text only. | None |
| LLM08 Vector and Embedding Weaknesses | Studied by the project; embeddings are frozen and hash-verified. | W13 |
| LLM10 Unbounded Consumption | Good. Tokens, time, size and one-job limits. | W8 |

### 8.2 MITRE ATT&CK and ATLAS

| Technique | Relevance to this system | Findings |
|---|---|---|
| ATT&CK T1574 Hijack Execution Flow | Editing config or the loaded retrieval script changes what runs. | W1, W5 |
| ATT&CK T1195 Supply Chain Compromise | Vulnerable or malicious dependencies and model files. | W2 |
| ATT&CK T1070 Indicator Removal / lack of logging | No trace of local misuse. | W3 |
| ATT&CK T1499 Endpoint Denial of Service | Job and connection limits mitigate; archive cap is self-inflicted. | W8 |
| ATLAS AML.T0051 LLM Prompt Injection | Instruction-containing passages (instruction_append challenge). | W13 |
| ATLAS AML.T0070 RAG Poisoning | Inserted answer-preserving copies change which evidence a filter removes (the study's subject). | W13 |

## 9. Secure development practice scorecard

| SDLC phase | Rating | Evidence |
|---|---|---|
| Requirements and threat modelling | Strong | Documented threat model, OWASP coverage and trust assumptions are referenced in the authors' security review; the stated limits are explicit. |
| Secure design | Strong | Loopback only, fixed routes, no user-supplied paths, process isolation, private directories, text-only UI. |
| Secure implementation | Good | Strict parsing and validation, atomic private writes, hash-checked inputs. Gaps: config handling (W1), check-then-use (W5). |
| Verification and testing | Strong | 50 unit tests plus security probes, browser checks, SAST and dependency audit in the release record; independent fuzzing here found no bypass. |
| Release and integrity | Partial | Manifests and hashes are good practice, but they are self-attesting (W6), the release was extracted writable (W12) and the packet check failed once a stray file appeared (W1, W9). |
| Operations and monitoring | Weak | No request logging or alerting (W3). |
| Maintenance and dependencies | Weak | 82 open advisories at the time of testing (W2); the authors treat these as open. |
| Incident learning | Good | The null-cancel-ID defect was found, fixed in 2.7.2 and given a regression test. Failed attempts are kept in the logs rather than hidden. |

## 10. Comparison with the authors' own review

The release includes its own SECURITY_REVIEW.md (9 November 2026). The two reviews agree on the main points and each found things the other did not.

| Topic | Authors' review | This review |
|---|---|---|
| Overall judgement | Implemented and tested controls; residual dependency and deployment risks remain; not certified for public use | Agrees |
| Bandit | 7 low, 0 medium or high | 8 low, 0 medium or high (this scan also covered the tools/ folder, which probably explains the extra one); agrees |
| Dependencies | 81 clusters across 7 packages including Torch and setuptools | 82 advisories across 5 packages in a different environment; same conclusion: open |
| Other local users, Ollama port, logging, quotas | Listed as residual risks | Agrees and rates them as W3, W4, W7, W8 |
| Config file protection | Not mentioned | New finding W1 |
| Check-then-use and self-attesting manifest | Not mentioned | New findings W5, W6 |
| Personal paths in shipped files; file permissions | Not mentioned | New findings W11, W12 |
| Independent fuzzing of all routes | 15 additional security tests | Over 35 hand-written probes; no bypass found |

## 11. Prioritised recommendations

| Priority | Action | Closes |
|---|---|---|
| 1 | Keep configuration outside the release; make the launcher refuse a config that is not owner-only; log the resolved executable paths. | W1 |
| 2 | Test and apply a bounded dependency upgrade, or record a dated risk acceptance with reachability analysis for each of the 82 advisories. | W2 |
| 3 | Add a private audit log (method, route class, status, run ID, time) including rejected requests. | W3 |
| 4 | If the tool might ever run on a shared host: require the token on GET run routes, use a Unix socket or cookie, and protect the Ollama port. | W4, W7 |
| 5 | Hash and load the retrieval script from the same in-memory bytes; sign or externally publish the release manifest. | W5, W6 |
| 6 | Clean personal paths, ship with correct file modes, improve verify_packet.py messages, add a run-cleanup command and the extra headers. | W8 to W12 |
| 7 | Exercise the timeout, size and disk limits in a test harness so they are evidenced, not only read. | Limitations |

## 12. Open questions for the project team

These points could not be settled from the release folder alone. Each needs an answer from the project team before the related wording in this report is final.

| # | Question | Why it matters | Answer |
|---|---|---|---|
| Q1 | Is leaving TrustRAG out of the GUI intentional? The live modes use only RAGDefender (the native filter), and the Findings tab says there is no TrustRAG answer-generation mode. | If intentional, Section 4.3 stands as a scope note. If not, it becomes a functional gap. | [pending] |
| Q2 | Is there a course or project requirement that TrustRAG be demonstrable in the GUI (run live or shown per case)? | Decides whether the TrustRAG omission is reported as a gap against a requirement or only as a scope note. | [pending] |
| Q3 | Should the per-case TrustRAG results (TRUSTRAG_CASES.md, Task 13 handover, components/task08) be treated as part of the assessed release? Example: NanoMSMARCO:1028652. | They sit outside the assessed folder. Section 4.4 cites them as background only. | [pending] |



## 13. Appendix

### A. Environment and tools

- Linux 6.8.0-65-generic; base interpreter Python 3.14.7 for the server and tests; runtime environment filterflip-repro (Python 3.11) for the backend.
- Model service: Ollama with qwen2.5:3b (digest 357c53fb659c) on CPU.
- Bandit 1.9.4; pip-audit 2.10.1; python-docx for this report. Scanner tools were installed in a temporary virtual environment outside the release.
- A throwaway configuration and run folder outside the release were used. The release folder itself was not modified by the assessor.

### B. Reproduction commands

```text
# integrity (after moving app/config.local.json out of the release)
python3 -B tools/verify_packet.py

# unit tests
cd app && python3 -B -m unittest discover -s tests

# static analysis and dependency audit
bandit -q -r app/*.py tools/*.py
pip-audit -r requirements_of_runtime_env.txt --no-deps --disable-pip

# create a clean work area and launch
python3 -B app/configure.py --from-config <existing config.local.json> --work <new empty folder>
python3 -B app/launch.py <new folder>/config.local.json
# then open http://127.0.0.1:8767
```

### C. Browser walkthrough (tester-reported)

| Section | Checks | Result |
|---|---|---|
| A Page load and navigation | A1 to A6 | Pass (tester-reported) |
| B Saved evidence | B1 to B10 | Pass (tester-reported) |
| C Live setup and validation | C1 to C4 | Pass (tester-reported) |
| D Live run, cancel, reconnect, concurrency | D1 to D11 | Pass (tester-reported) |
| E Recorded case and display modes | E1 to E4 | Pass (tester-reported) |
| F Browser security observations | F1 to F8 | Pass (tester-reported); F8 confirms the token is returned by bootstrap (W4) |

No screenshots were captured for this walkthrough (see Section 2.3). If time allows, re-capture B6 (the preserved-discrepancy warning), D3 (finished live run), D7 (cancelled state) and F1 (response headers) as supporting evidence.
