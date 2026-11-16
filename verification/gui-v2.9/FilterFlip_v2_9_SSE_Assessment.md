# Secure Software Engineering Assessment: FilterFlip-RAG GUI v2.7.2, v2.8 and v2.9

*Functional verification and security review using OWASP, MITRE and STRIDE*

- **System assessed:** FilterFlip_GUI_v2_7_2_Security_2026-11-09 (FilterFlip-RAG GUI 2.7.2, released 9 November 2026)
- **Assessment date:** 10 and 11 November 2026
- **Prepared by:** Shradha Sanjaykant Suryawanshi
- **Frameworks:** STRIDE threat model; OWASP Top 10 and OWASP Top 10 for LLM Applications; MITRE ATT&CK and MITRE ATLAS
- **Releases:** v2.7.2 (full assessment, Sections 1 to 12), v2.8 (re-test of the fixes, Section 13) and v2.9 (new live TrustRAG mode, Section 14)
- **Status:** Draft for course submission. Framework identifiers were checked online on 10 November 2026 (see Appendix D). The tester reports that all v2.8 and v2.9 browser acceptance checks passed (Sections 13.5 and 14.3).

## 1. Executive summary

FilterFlip-RAG GUI 2.7.2 is a local, single-user web application that demonstrates a research study on retrieval-corpus poisoning and filter defences in a RAG pipeline. It was assessed for functionality and for secure software engineering (SSE) practice.

**Overall result.** All functions that were exercised worked as specified. The application shows strong secure-by-design practice for a local tool: loopback-only binding, strict input validation, text-only rendering, a restrictive Content-Security-Policy, hash-verified inputs, bounded jobs and private file permissions. **No remotely exploitable vulnerability was found**, and static analysis found no medium or high issues. Six findings are recorded (1 Medium, the open dependency advisories; 5 Low) together with 8 informational observations. Most of these are hardening points that follow from the stated trust model (one trusted local user), not defects.

| Area | Result |
|---|---|
| Functional testing | Pass. 50/50 bundled unit tests; all 4 live modes completed; cancel works; guided UI walkthrough (sections A to F) reported as passing by the tester. |
| Input and API fuzzing | Pass. Over 35 malformed or hostile requests were rejected with 4xx and no data leaked; server stayed healthy after a 30-connection flood. |
| Static analysis (Bandit) | 0 high, 0 medium, 8 low (all reviewed: accepted risk or false positive). |
| Secret scan | No credentials found. Personal paths and usernames appear in 4 shipped files. |
| Dependency scan (pip-audit) | 82 known advisories across 5 packages (Pillow 39, transformers 28, filelock 12, certifi 2, sentence-transformers 1). Open; reachability judged low but not proven. |
| Findings | 0 Critical, 0 High, 1 Medium (dependency advisories), 5 Low, plus 8 informational observations (Section 7). |

**Version 2.8.** The project team released v2.8 in response. Of the six findings, three (W1, W3, W5) were fixed and verified by the assessor, W6 was improved, W4 was accepted by the authors as a design limit and W2 (dependencies) remains open. Of the eight observations, W8 and W10 were fixed and verified, W12 was improved, W7 and W13 were accepted, W9 and W11 were not re-tested and W14 is covered by one new scanner note (N1, the deliberate execution of verified bytes). A minor cancel-error inconsistency was also fixed and verified. See Section 13.

**Version 2.9.** The team then released v2.9, which adds a live TrustRAG stage-1 mode (12 fixed cases, conditions C, BN1 and PN1, fresh filtering and fresh Qwen answers on saved contexts and embeddings) and a Project work and security tab. The assessor retest found no new vulnerability: the packet check, 81 unit tests (normal and optimised), 15 additional security probes and the 36-context filter-equivalence check all passed, and 18 of 18 hostile requests to the new mode were rejected without starting a run. One new informational observation (N4: the vendored TrustRAG runtime is hash-checked, then loaded from disk) and one documentation mismatch (N5) were recorded. W2 (dependencies) remains open and now also covers the vendored NLTK runtime. See Section 14.

**Most important recommendations.** (1) Close or formally risk-accept the open dependency advisories (W2), which is the only substantive open item. (2) Keep the config outside the release and have the launcher refuse a writable config (W1, fixed in v2.8). (3) Add an audit log of state-changing requests (W3, fixed in v2.8). (4) Require the run token on read routes if the tool is ever run on a shared host (W4).

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
- Framework identifiers were checked on 10 November 2026 against OWASP, MITRE ATT&CK and a MITRE D3FEND mirror of ATLAS (the atlas.mitre.org technique pages returned 404 to the checking tool, so the ATLAS names rest on the D3FEND mirror and secondary sources). OWASP Top 10 numbering follows the 2025 edition and the LLM list follows the 2025 edition. See Appendix D.
- A configuration file (app/config.local.json) was created by the tester at 09:24 on 10 November 2026 (confirmed, Q5) when setting up the app, and it was placed inside the release folder, which START_HERE.md says to avoid. It was not part of the sealed manifest, so it made the packet integrity check fail. The tester moved it out before the UI walkthrough. The file is not a shipped defect; the underlying weakness (an unprotected config that controls executed binaries) is recorded as finding W1.
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

The application-level hash check (safety.verify_release) passed for all 279 listed files. The packet-level check tools/verify_packet.py initially failed with the unhelpful message "unlisted or missing files" because app/config.local.json (created by the tester, not in the manifest) was present inside the release; after the file was moved out, the tester proceeded with the walkthrough. The unhelpful message is recorded as W9, and the unprotected-config weakness as W1.

### 4.3 TrustRAG coverage

TrustRAG is not available in the GUI. This was checked in three places and they agree:

- **Code:** the only live modes are original, variants (all nine conditions), mitigation and challenge. The only filter in backend.py is RAGDefender (ragdefender.RAGDefender, task type single_hop), which the UI and the study call the native filter. The exact-copy (E) and near-copy (CN) policies group copies first and then run the same RAGDefender filter. The four policies offered are U (no filter), N (native), E and CN.
- **Page text:** the Findings and Evidence tab states "There is no TrustRAG answer-generation mode in this GUI."
- **Release notes:** GUI_GUIDE.md lists TrustRAG live generation among the items outside this release.

TrustRAG appears in the GUI only as one summary paragraph on the Findings and Evidence tab: a separate 12-case, stage-1 comparison with 60 fresh study responses for 72 logical records, strict endpoint 5 met, 6 not met and 1 uncertain, background-qualified endpoint 3 met, 8 not met and 1 uncertain. The tab itself says this is not full TrustRAG and not a matched defence ranking. There is no per-case TrustRAG view.

**Assessment.** The omission is consistent with the release's stated scope, so it is recorded as a scope note, not as a defect. It would become a gap only if the course or project requirements expect TrustRAG to be demonstrable in the GUI. That question is listed in Section 12 (Q1 and Q2). **Update:** the project team has since answered that the omission was intentional, and v2.8 adds a recorded per-case TrustRAG explorer (no live mode); see Section 13.

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
| Spoofing | Another local user or process on the same host obtains the token and acts as the operator | TB1: GET /api/bootstrap returns the token without authentication | Host and Origin allowlist; loopback binding | Low on a single-user host; higher on a shared host (W4) |
| Spoofing | A web page in the user's browser attacks the local server (CSRF, DNS rebinding) | TB1 | Origin and Host checks, Sec-Fetch-Site, token, JSON-only content type | Low: all probes rejected |
| Tampering | Modify config or code so a different Python or Ollama binary runs | TB4: config.local.json mode 664 inside release; paths executed without ownership or permission check | Hash check on .py files at startup | Low (W1) |
| Tampering | Replace the retrieval script between hash check and load | TB4: backend.py hashes then loads from path | Hash-verified manifest | Low (W5) |
| Tampering | Alter the release manifest and the code together | TB4: manifest lives beside the code, checked only at startup | SHA256 manifests | Low (W6) |
| Tampering | Inject data via malformed API input | TB1 | Strict validation, whitelists | Low: all fuzz cases rejected |
| Repudiation | No record of who started or cancelled which run | server.py: log_message is a no-op | Per-run state, events and request fingerprints | Low (W3). Rejected requests were not recorded at all in v2.7.2. |
| Information disclosure | Another local user reads run results via GET routes (no token) | TB1 | 128-bit random run IDs; loopback | Low (W4) |
| Information disclosure | Usernames and directory layout leak through shipped files | 4 shipped files contain /home/... paths | None | Info (W11) |
| Information disclosure | Secrets in code or config | Entire release | n/a | None found |
| Denial of service | Exhaust CPU, disk or the run quota | TB1, TB2 | One job, timeouts, size and disk caps, 8 slots, 3 s socket timeout | Low. Archive cap blocks use until runs are cleared (W8, informational). |
| Elevation of privilege | Config controls executed binaries; a writable config yields code execution as the user | TB4 | None beyond file ownership | Low (W1) |
| Elevation of privilege | Application token does not protect the dedicated Ollama port 11437 | TB3 | Loopback, owned service, identity checks | Low (W4); W7 is informational |
| Elevation of privilege | Vulnerable dependency exploited via model or tokenizer loading | TB4: pretrained files parsed by transformers, sentence-transformers | Offline mode, hash-verified model files | Medium rating (W2): 82 advisories open, low practical risk in this context |

## 7. Findings and observations

Severity is the assessor's judgement for the stated deployment: one trusted local user on a private machine, loopback only. Issues that would need prior write access to the user's own files are rated Low, because an attacker with that access has already compromised the account. **No remotely exploitable vulnerability was found.** Items that are design choices, usability points or research limits are listed as observations, not findings. "Basis" says whether the item was verified by running something, read in code, or both.

### 7.1 Findings (W1 to W6)

| ID | Sev. | Finding and evidence | Mapping | Recommended fix |
|---|---|---|---|---|
| W1 | Low | Config file controls executed binaries and is unprotected. app/config.local.json lists the python and ollama_binary that are executed. In this test it was group-writable (mode 664) and sat inside the release (the tester created it there); nothing checks a config's location, owner or permissions, so the same would happen to any config. A writer gains code execution as the user. Rated Low because exploiting it needs prior write access to the user's own files, at which point the account is already compromised. Basis: verified. | OWASP A02 Security Misconfiguration; A01 Broken Access Control. STRIDE T, E. ATT&CK T1574 Hijack Execution Flow. | Keep config outside the release; at startup refuse a config that is not owned by the user or is writable by group or others; resolve and log the executed paths. |
| W2 | Medium | Open dependency advisories. pip-audit reports 82 advisories in 5 packages in the runtime environment (Pillow 39, transformers 28, filelock 12, certifi 2, sentence-transformers 1). The authors list 81 clusters and also Torch and setuptools; environments differ. Pillow and filelock are not imported by the application code. Basis: verified (scan); reachability is inferred, not tested. Rated Medium because it is the one open item with a known external fix path, not because exploitation is likely here. | OWASP A03 Software Supply Chain Failures (LLM03 Supply Chain). ATT&CK T1195. | Test a bounded upgrade (Pillow 13, transformers 4.53+, certifi 2026.10.18) and re-run the suite; otherwise record a dated risk acceptance with reachability analysis. |
| W3 | Low | No audit trail. server.py disables all request logging (log_message does nothing). There is no record of which request started or cancelled a run, and rejected or hostile requests leave no trace. Basis: read. | OWASP A09 Security Logging and Alerting Failures. STRIDE R. No ATT&CK technique describes absent logging itself; T1070 Indicator Removal covers only deliberate deletion, which missing logs would make undetectable. | Log method, path class, status and run ID to a private file; log rejected requests; rotate. |
| W4 | Low | Local trust only. The run token is issued by an unauthenticated GET, GET routes for run results need no token, and the dedicated Ollama port 11437 has no authentication. On a shared host another user could start jobs or read results. Verified: bootstrap returned the token to a plain curl call. Basis: verified. Documented by the authors as a residual risk. | OWASP A01 Broken Access Control. STRIDE S, I, E. | State the single-user assumption prominently; for shared hosts use a Unix-domain socket or a session cookie, require the token on GET run routes and use filesystem permissions for the Ollama socket. |
| W5 | Low | Check-then-use gap. backend.py hashes run_retrieval.py then loads it from the file path, so a swap between the two steps would not be detected. Basis: read. | OWASP A08 Software or Data Integrity Failures; CWE-367. STRIDE T. | Read the bytes once, hash them, then compile and exec those same bytes. |
| W6 | Low | Self-attesting integrity. RELEASE_MANIFEST.json lives beside the code it protects and is checked only at startup. verify_release only flags unlisted *.py files. Basis: read. | OWASP A08. STRIDE T. | Publish the manifest hash out of band or sign it; check the full file list. |

### 7.2 Observations (W7 to W14)

These are hardening suggestions, design choices and research limits. None is a security defect by itself.

| ID | Sev. | Observation and evidence | Mapping | Suggestion |
|---|---|---|---|---|
| W7 | Info | Hardcoded versions and port. Ollama version 0.34.2, the model digest and port 11437 are hardcoded, and the port check is racy (probe, then start). Pinning is good for reproducibility but makes upgrades brittle. Basis: read. | OWASP A06 Insecure Design. CWE-367. | Bind to an OS-assigned port or a Unix socket; make version pins configuration. |
| W8 | Info | Archive cap becomes a self-inflicted denial of service. After 60 runs the tool refuses new runs until a person clears the folder. No retention policy. Basis: read. | STRIDE D. LLM10 Unbounded Consumption (inverse). | Add a documented cleanup command or age-based retention. |
| W9 | Info | Poor error reporting in the packet check. tools/verify_packet.py prints only "FAIL: unlisted or missing files" and not which file. Basis: verified. | SSE: maintainability and usability of security tooling. | Print the offending paths. |
| W10 | Info | Missing hardening header and plain HTTP. No Permissions-Policy header; HTTP not TLS. Acceptable on loopback. Basis: verified. | OWASP A02. | Add Permissions-Policy and Cross-Origin-Opener-Policy; document that TLS is required if bound beyond loopback. |
| W11 | Info | Personal paths and usernames shipped in documents and data (START_HERE.md, acceptance/SOURCE_BINDINGS.json, app/data/SOURCE_PROVENANCE.json, provenance/SOURCE_BINDINGS.json). Basis: verified. | OWASP A01 (information exposure); LLM02 Sensitive Information Disclosure (minor). | Replace with placeholders before distribution. |
| W12 | Info | Group-writable files. All 385 files in the extracted release at the time of testing (including the tester's config file) were mode 664 (umask 0002). Probably an extraction artefact, but it weakens the sealed-release claim. Basis: verified. | OWASP A02; A08. | Ship and extract with 0644/0755 and document it. |
| W13 | Info | Prompt injection and RAG poisoning remain only measured, not solved. The system prompt tells a 3B model to treat the document as untrusted, which the model cannot enforce; the instruction_append challenge shows this. This is the research subject, and the authors state that general mitigation is unproven. Basis: design analysis. | OWASP LLM01 Prompt Injection; LLM04 Data and Model Poisoning; LLM08 Vector and Embedding Weaknesses. ATLAS AML.T0051; AML.T0070 RAG Poisoning. | Keep the claim bounded (as the authors do); add provenance or approval gating for any corpus that feeds a real deployment. |
| W14 | Info | Bandit low findings: 5 x B404 (subprocess imported), 2 x B603 (subprocess without shell; arguments come from config and constants, not from the browser) and 1 x B106 (false positive: a tokenizer special token). Basis: verified. | CWE-78 (not exploitable here, but see W1). | Accept; add a nosec comment with the reason. |

**Also noted, not rated.** A cancel request with extra fields returned 404 "Unknown operation" while other malformed cancel requests returned 400, and the server does not URL-decode paths (a percent-encoded case ID returns 404). Both are harmless and arguably safer. The project team made the cancel responses consistent in v2.8 (Section 13). This was labelled W15 in earlier drafts.

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
| Mishandling of Exceptional Conditions | Good. Errors are generic; partial results preserved; null cancel ID fixed in 2.7.2. | None |
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
| ATT&CK T1070 Indicator Removal (related, not a direct mapping) | Covers deliberate deletion or alteration of an attacker's own traces. Without an audit log, such deletion on this system would leave nothing to compare against. Missing logging is not itself a T1070 technique. | W3 |
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
| Config file protection | Not mentioned | New finding W1 (rated Low) |
| Check-then-use and self-attesting manifest | Not mentioned | New findings W5, W6 |
| Personal paths in shipped files; file permissions | Not mentioned | New observations W11, W12 |
| Independent fuzzing of all routes | 15 additional security tests | Over 35 hand-written probes; no bypass found |

## 11. Prioritised recommendations

| Priority | Action | Closes | Status after v2.8 |
|---|---|---|---|
| 1 | Test and apply a bounded dependency upgrade, or record a dated risk acceptance with reachability analysis for each of the 82 advisories. | W2 | Open |
| 2 | Keep configuration outside the release; make the launcher refuse a config that is not owner-only; log the resolved executable paths. | W1 | Fixed and verified |
| 3 | Add a private audit log (method, route class, status, run ID, time) including rejected requests. | W3 | Fixed and verified |
| 4 | Hash and load the retrieval script from the same in-memory bytes; sign or externally publish the release manifest. | W5, W6 | W5 fixed and verified; W6 improved, manifest still unsigned |
| 5 | If the tool might ever run on a shared host: require the token on GET run routes, use a Unix socket or cookie, and protect the Ollama port. | W4, W7 | Accepted as a design limit |
| 6 | Housekeeping: clean personal paths, ship with correct file modes, improve verify_packet.py messages, add a run-cleanup command and the extra headers. | W8 to W12 | W8, W10 fixed; W12 improved; W9, W11 not re-tested |
| 7 | Exercise the timeout, size and disk limits in a test harness so they are evidenced, not only read. | Limitations | Not done at production scale |

## 12. Open questions for the project team

These points could not be settled from the release folder alone. Each needs an answer from the project team before the related wording in this report is final.

| # | Question | Why it matters | Answer |
|---|---|---|---|
| Q1 | Is leaving TrustRAG out of live generation intentional? The live modes use only RAGDefender (the native filter), and the Findings tab says there is no TrustRAG answer-generation mode. | If intentional, Section 4.3 stands as a scope note. If not, it becomes a functional gap. | Answered (REVIEW_DISPOSITION.md): intentional. v2.8 adds recorded per-case evidence only. |
| Q2 | Is there a course or project requirement that TrustRAG be demonstrable in the GUI (run live or shown per case)? | Decides whether the TrustRAG omission is reported as a gap against a requirement or only as a scope note. | Answered (REVIEW_DISPOSITION.md): recorded project history does not establish a promise of full TrustRAG live generation. Reported as a scope note. |
| Q3 | Should the per-case TrustRAG results (TRUSTRAG_CASES.md, Task 13 handover, components/task08) be treated as part of the assessed release? Example: NanoMSMARCO:1028652. | They sit outside the assessed folder. Section 4.4 cites them as background only. | Answered (REVIEW_DISPOSITION.md): the accepted stage-1 contexts, endpoints and saved answers are included in v2.8 as derived display data. |
| Q4 | Which dependency environment is authoritative for the GUI: filterflip-core (audited by the authors) or filterflip-repro (audited here)? | The two audits differ (Torch and setuptools appear only in the authors' list), so W2 cannot be reconciled until this is known. | All tests in this report, for v2.7.2 and v2.8, ran in filterflip-repro, the only environment on this machine. Confirmed by the tester on 11 November 2026: filterflip-repro is the only environment on this machine and is the one used; the v2.9 documents still name filterflip-core, which does not exist here (N5). The authors' filterflip-core scan is still needed to reconcile W2 (see DEPENDENCY_RECONCILIATION.md). |
| Q5 | Who created app/config.local.json inside the release folder at 09:24 on 10 November 2026, and was it intended to be there? | It is outside the sealed manifest and made the packet integrity check fail (W1, W9). | Answered: created by the tester when setting up the app. Not a shipped file. |

## 13. Version 2.8 re-assessment

The project team released v2.8 on 10 November 2026 as their response to this assessment (REVIEW_DISPOSITION.md). The assessor re-tested each fix that could be tested. The v2.8 release folder was not modified. All tests used a throwaway configuration and run folder outside the release. These results are separate from the v2.7.2 results above and do not change them.

### 13.1 What changed in v2.8

- A "Findings and Evidence" tab with seven expandable sections, including a recorded explorer for all 12 TrustRAG stage-1 cases (C, BN1, PN1). TrustRAG remains a recorded evidence view, not a live mode.
- Configuration protection, verified-bytes loading of the retrieval script, private rotating security-event logs, an exclusive run-archive lock with an offline archive command, stricter release verification, extra browser headers and consistent cancel errors.
- No dependency upgrades and no change to the live modes or scientific settings.

### 13.2 Retest of the findings

| Finding | v2.8 treatment | Assessor's test | Status |
|---|---|---|---|
| W1 Config protection | Config must be a user-owned, owner-only regular file outside the release, in a parent folder that is user-owned and not group or other writable | 11 negative cases on disposable copies (0660, 0640, 0644, symlink, hard link, group-writable parent, FIFO, inside release, missing, 9 MB, duplicate keys): all refused. The configure.py output was accepted. | Fixed, verified |
| W2 Dependencies | Left open; reconciliation needs data | Raw pip-audit JSON and package list saved for filterflip-repro (82 advisories, 41 packages). filterflip-core scan not available here. | Open |
| W3 Logging | Private bounded event log of POSTs and error responses | 16 rows after fuzzing, including 403, 404, 405 and 431 responses; 0 occurrences of the token, host or body strings; file mode 600; run start and cancel recorded with run IDs. | Fixed, verified. No human identity and not tamper-proof (stated by the authors). |
| W4 Local-host trust | Retained explicitly | Not tested (design decision) | Accepted by the authors |
| W5 Check-then-use | Script read once, hashed, compiled and executed from the same bytes | Mutation test: file swapped on disk after the verified read, only the verified content ran; tampering before the read was refused. | Fixed, verified |
| W6 Manifest authenticity | Rejects unexpected and missing files throughout the app; external ZIP checksum supplied | Packet check passed (441 files, version 2.8). Manifest remains unsigned. | Improved; authenticity not added (stated by the authors) |
| W7 Pins and port | Retained for scientific comparability | Not tested (design decision) | Accepted by the authors |
| W8 Run limit | Explicit offline archive with preview, apply, lock and receipt | Preview wrote nothing. Apply moved 2 completed or cancelled runs with a receipt (mode 700). Refused: running state, symlink inside a run, duplicate IDs, malformed ID, existing destination, destination inside the run folder or release, and archiving while a server held the lock. | Fixed, verified |
| W9 Packet error messages | Lists mismatched paths | Not re-tested (the packet check passed) | Not run |
| W10 Headers | Added Permissions-Policy and Cross-Origin-Opener-Policy | Both present; CSP unchanged | Fixed, verified |
| W11 Personal paths | Active instructions use placeholders; historical provenance keeps original paths | Not re-tested | Not run |
| W12 Permissions | Packaged files 0644, directories 0755 | No group-writable files; the top-level folder and two subfolders were 775 after extraction | Mostly fixed (extraction effect) |
| W13 Model manipulation | Research limitation retained | Not tested (research limit) | Accepted by the authors |
| W14 Static findings | Reassessed with raw scanner output retained | Bandit 1.9.4 on app and tools: 0 high, 1 medium, 9 low | See N1 |
| W15 Cancel errors | Invalid or extra fields return 400 | 5 malformed cancel requests all returned 400 | Fixed, verified |

### 13.3 Regression and functional results (v2.8)

- **Unit tests:** 68 of 68 pass (50 in v2.7.2).
- **Endpoint fuzzing repeated:** bad JSON, duplicate keys, extra fields, an excluded challenge case, missing token, forged Host, cross-site fetch, chunked encoding, PUT, oversized header and run-ID traversal were all rejected with 4xx.
- **Live runs:** a PN1 run for NanoMSMARCO:1028652 completed (native filter kept 4 of 5 passages, 2 answers ok); a second run was cancelled, the model subprocess was killed and port 11437 was freed.
- **Single-instance lock:** a second server on the same run folder was refused.
- **New TrustRAG data:** app/data/findings.json holds 12 cases with strict endpoints 5 met, 6 not met, 1 uncertain, and cornflakes (NanoMSMARCO:1028652) as met; this matches the earlier study's TRUSTRAG_CASES.md.
- **Packet verification:** passed, 441 files, version 2.8.

### 13.4 New observation

| ID | Sev. | Observation | Treatment |
|---|---|---|---|
| N1 | Medium (scanner rating) | Bandit B102 flags exec(compile(...)) in safety.verified_module, introduced by the W5 fix. It is deliberate: the bytes that were hashed are the bytes that run. The mutation test in 13.2 confirms this, and the authors document it in SECURITY_REVIEW.md. | Accepted, intended and mitigated. The authors state they do not suppress reviewed warnings. |
| N2 | Info | Release verification now requires the application folder to match the manifest exactly, so any extra file in it (for example bytecode or an editor temporary file) stops startup. This is stricter and safer but less forgiving. Read from the code; not tested with an extra file. | The authors require python3 -B for this reason (START_HERE.md). |
| N3 | Info | The security log records POSTs and error responses only, with fixed route classes, status, time and validated run IDs. Successful reads are not logged. | Matches the authors' stated scope. |

### 13.5 Browser acceptance of v2.8 (tester-performed)

The tester ran the v2.8 acceptance checklist in a browser on 10 November 2026 and reported that all checks passed. These results are tester-reported: no screenshots or exported logs are attached to this report, and the assessor did not observe the browser session. An operational pass is not a semantic judgment of any model answer, and the checklist does not assume any sign-off or joint adjudication.

| Checklist step | Check | Result |
|---|---|---|
| 1 | Packet verification output and environment details saved | Pass (tester-reported) |
| 2 | External work folder created; configuration kept outside the release | Pass (tester-reported) |
| 3 | All seven Findings and Evidence sections match the accepted records (8/59 primary, nine conditions, reproduction caveats, mitigation gains and losses, challenge harms) | Pass (tester-reported) |
| 4 | Recorded TrustRAG explorer: Heather, cornflakes and the uncertain case; C/BN1/PN1, answers, support judgments, passages; no model launched | Pass (tester-reported) |
| 5 | Primary-case link to the nine-condition explorer; reference and reproduction answers; uncertainty and truncation visible | Pass (tester-reported) |
| 6 | Live modes (original, variants, mitigation, challenge) with exports | Pass (tester-reported) |
| 7 | Security-event log and archive procedure | Covered by the assessor's test in 13.2 (W3, W8), not repeated by hand |
| 8 | Offline checks from VALIDATION_REPORT.md | Optional; not reported |

### 13.6 Remaining open points

- **W2 dependencies** remain open. Reconciling the authors' 81 clusters (filterflip-core, 43 packages) with this assessment's 82 advisories (filterflip-repro, 41 packages) needs a scan of filterflip-core with raw JSON, scan date, tool version and arguments. The assessor's equivalent data for filterflip-repro is in v28_retest_evidence/.
- **W4 and W7** are accepted design limits and the tool remains a local single-user research tool.
- **Unexercised limits:** the production-size timeout, output cap and disk guards were not run at full scale in either release; reduced-threshold tests exist (as the authors note).
- **W9 and W11** were not re-tested.

### 13.7 Corrections accepted from the project team

- The application already retained per-run research evidence; the gap was security-request logging, which v2.8 adds.
- The 82-advisory and 81-cluster scans describe different environments and scopes and must not be compared as an improvement or regression.
- MITRE ATT&CK T1070 denotes deliberate indicator removal, not simply absent logging. The report's mapping was corrected (W3 and Section 8.2).
- Full production-duration and production-size stress tests were not claimed by the authors, and this report does not claim them either.

## 14. Version 2.9 assessment

Release assessed: GUI_v2.9/FilterFlip_GUI_v2_9_All_Work_2026-11-10 (RELEASE_STATUS.json: version 2.9, based on 2.8, 10 November 2026). ZIP SHA-256 as computed by the assessor: 0835e80aede792641ffd02b70995186596ccc2609e9213d082a12915ec25906b. The release contains no checksum file, so this value still has to be confirmed against one supplied by the project team:completed.

### 14.1 What changed in v2.9

- **New live mode:** TrustRAG stage 1 on 12 fixed questions with conditions C, BN1 and PN1. Contexts and SimCSE embeddings are saved and hash-verified. The original clustering and n-gram filter and two Qwen answers (U without filter, T with TrustRAG stage 1) are computed fresh in each run. Retrieval and embedding generation are not rerun, and later TrustRAG stages are not implemented.
- **New tab:** Project work and security (13 tasks, dated records, STRIDE and OWASP mappings, dependency work, report draft and a PDF served at /semester-report.pdf).
- **Code changed:** backend.py (about 150 lines, new trust branch), server.py and safety.py (6 lines each: new routes, trust allow-list), new trust.py, trust_native.py and trust_profile.json, a vendored trust_runtime (504 files, 7.6 MB: nltk 3.9.2, rouge-score, absl-py, click), new data files and static/project.js. operations.py, archive_runs.py, launch.py and configure.py are unchanged from v2.8.
- **Stated scope limits (RELEASE_STATUS.json):** independent v2.9 acceptance pending; new answers not human-reviewed; dependency candidate not adopted; research outcomes unchanged.

### 14.2 Assessor retest

| Check | Result | Notes |
|---|---|---|
| Packet integrity (verify_packet.py) | Pass | 1,036 files, version 2.9, 0 model calls; repeated after the tests. |
| Unit tests, normal and -O | Pass | 81 tests in each mode. |
| Additional security probes, normal and -O | Pass | 15 tests in each mode (tools/check_additional_security.py). |
| Filter equivalence (check_trust_filter.py) | Pass | 36 of 36 contexts give the saved selection and order; no encoder or answer model loaded. |
| Vendored runtime coverage | Pass | All 504 files under trust_runtime are listed in trust_profile.json; none unlisted or missing. |
| Hostile requests to the new mode (18) | Pass | Case outside the panel, BN2, lowercase pn1, list condition, extra field, traversal and 900-character case IDs, unknown mode, missing and wrong token, wrong content type, oversize body, invalid JSON, JSON array, null bytes, bad Origin, bad Host, cross-site Sec-Fetch-Site: all 400 or 403; no run started. |
| Routes and headers | Pass | Bootstrap flags exactly 12 of 59 cases as TrustRAG. /api/project, /semester-report.pdf and /project.js return the standard headers. Traversal and direct requests for trust_profile.json and data/trust_contexts.json return 404. |
| Audit log | Pass | Every probe was logged with time, method, route class, status and no run ID; none of the hostile strings were written. |

The probes ran against a separate test server on port 8772, built from a scratch copy of the release. Raw output is in v29_retest_evidence/. A valid TrustRAG start was not sent to the test server, to avoid a clash with the tester's model service; valid runs were performed by the tester in the browser (Section 14.3).

### 14.3 Browser acceptance of v2.9 (tester-performed)

| Item | What was checked | Result |
|---|---|---|
| B1 | Four tabs; 13 tasks, pending report and presentation, dated records, report-draft link; read-only navigation starts no model | Pass (tester-reported) |
| B2 | TrustRAG selected: exactly 12 questions; only C, BN1, PN1; explanation names fixed contexts and fresh filtering and answers | Pass (tester-reported) |
| B3 | Cornflakes C and PN1 run and exported; passages, order and U/T answers compared | Pass (tester-reported). The C result showed T order 1, 4, 5, 2, 3 against U order 1 to 5, matching the developer's expected selection (screenshot seen by the assessor; passage text and export JSON not checked). |
| B4a | Signal-transduction C: empty T selection | Pass. Export read by the assessor: T kept [] (0 of 5), the T request contains an empty document, a real Qwen response (qwen2.5:3b, 5 tokens) was returned and both answers were Not enough information. |
| B4b | Recorded reordered context (cornflakes C) | Pass on the displayed order; export field policies.T.kept not checked. |
| B5 | Inspect recorded case opens the TrustRAG record; cancel, reconnect, export; partial output kept | Pass (tester-reported) |
| B6 | The four older modes retain selection and behaviour | Pass (tester-reported) |
| B7.1 | Response headers in DevTools | Pass (screenshot seen): CSP, COOP same-origin, CORP same-origin, Permissions-Policy, Referrer-Policy no-referrer, nosniff, X-Frame-Options DENY, Cache-Control no-store. |
| B7.2 | A second job while one runs is refused | Pass. Audit log: a POST /api/runs accepted (202) and 4 seconds later a second one refused (409); no second run folder. |
| B7.3 | Audit log content | Pass. security-events.jsonl is owner-only and holds only time, method, route class, status and run ID. |

Checklist items 7 and 8 (offline reproduction and the return table) are covered by Section 14.2 and this table. The tester's own run folders and exports are kept outside this report and were not included in the return ZIP.

### 14.4 Findings and observations for v2.9

| ID | Sev. | Item | Detail |
|---|---|---|---|
| W2 | Medium | Dependency advisories (open) | Unchanged and still the only open Medium item. v2.9 adds the vendored NLTK 3.9.2: the team reports 73 raw rows and 41 advisory groups, which the assessor did not re-scan. No package was upgraded. The team's mitigation is a bounded input path: exactly five passages, at most 32 KiB each, no stemmer token over 256 characters, and only allow-listed fixed contexts reach NLTK. The assessor confirmed these bounds in trust.py and that the request fields (case, condition) are allow-listed. This limits exposure; it is not remediation. |
| N4 | Info | Vendored TrustRAG runtime is hash-checked, then imported from disk | trust.engine() hashes the 504 runtime files and trust_native.py, then imports them from disk afterwards. This is the check-then-use gap shown as W5 in v2.7.2; the v2.8 fix (verified_module) covers only run_retrieval.py. It matters only if another party can write to the release folder, which the local-account assumption already excludes. Found by reading the code; not demonstrated by a mutation test. Same mapping as W5 (OWASP A08, ATT&CK T1574). |
| N5 | Info | Environment name in the documents | START_HERE.md and VALIDATION_REPORT.md say conda activate filterflip-core. On the tester's machine only filterflip-repro exists, so the documented command fails at the first line (without the environment, the base interpreter ran verify_packet.py and configure.py; the saved config pins the filterflip-repro interpreter for the backend). Relates to Q4. |
| N6 | Info | Fresh answers need interpretation | In the signal-transduction C run, both U and T answered Not enough information, although the unfiltered context contains a pathway description (the photon example). This is model behaviour under the fixed prompt, shown with raw responses and request hashes, not a GUI defect. Semantic review is marked pending by the application, as intended. |

### 14.5 Functionality, scientific interpretation and residual risk

- **Functionality:** the new mode, the Project tab, the older modes, cancel, reconnect, export, the one-job lock and the audit log behaved as specified in every check above.
- **Scientific interpretation:** not assessed. The new answers are fresh and unreviewed; their meaning, and any comparison with the saved TrustRAG record, need human review.
- **Residual risk:** open W2 (including NLTK), accepted local-trust limits W4 and W7, and the informational items N4 to N6. No remotely exploitable vulnerability was found in v2.9.

### 14.6 Not done in the v2.9 retest

- No new Bandit or pip-audit scan of v2.9 and no scan of the vendored runtime; the team's 73 rows and 41 groups are quoted, not reproduced.
- The Node and Playwright suites (checklist step 7) were not run; they need tools not installed here.
- N4 was not demonstrated by a mutation test, and no valid TrustRAG run was started through the API by the assessor.
- The ZIP checksum was computed by the assessor, not confirmed against a team-supplied value.

### 14.7 Recommendations for the project team

- Load the TrustRAG runtime and trust_native.py from the same bytes that were hashed (the verified_module approach), or document the local-account assumption beside it (N4).
- Correct the environment name in START_HERE.md and VALIDATION_REPORT.md, or state both environment names and which one is authoritative (N5, Q4).

## 15. Appendix

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


### D. Framework identifiers checked

Checked on 10 November 2026. OWASP Top 10 2025: A01 Broken Access Control, A02 Security Misconfiguration, A03 Software Supply Chain Failures, A04 Cryptographic Failures, A05 Injection, A06 Insecure Design, A07 Authentication Failures, A08 Software or Data Integrity Failures, A09 Security Logging and Alerting Failures, A10 Mishandling of Exceptional Conditions (top10.owasp.org/2025). OWASP Top 10 for LLM Applications 2025: LLM01 Prompt Injection through LLM10 Unbounded Consumption (genai.owasp.org/llm-top-10). MITRE ATT&CK: T1574 Hijack Execution Flow, T1195 Supply Chain Compromise, T1070 Indicator Removal (deliberate removal only), T1499 Endpoint Denial of Service (attack.mitre.org). MITRE ATLAS: AML.T0051 LLM Prompt Injection and AML.T0070 RAG Poisoning, confirmed through the MITRE D3FEND mirror (d3fend.mitre.org/offensive-technique/attack/AML.T0051 and AML.T0070); the atlas.mitre.org pages themselves could not be fetched, and one secondary source disagrees on the tactic under which AML.T0070 is filed, which this report does not rely on.

### E. v2.8 retest evidence files

- v28_retest_evidence/pip-audit_filterflip-repro_raw.json, pip-freeze_filterflip-repro.txt and SCAN_METADATA.txt (pip-audit 2.10.1, Bandit 1.9.4, 10 November 2026).
- v28_retest_evidence/cfgtest.py (W1 configuration tests) and w5test.py (W5 mutation test).

### F. v2.9 retest evidence files

- v29_retest_evidence/offline_checks_log.txt (packet check, 81 unit tests twice, 15 probes twice, filter equivalence 36 of 36).
- v29_retest_evidence/dynamic_probes.py and dynamic_probes_output.txt (18 hostile requests and route checks) with probe_server_security-events.jsonl (the test server's audit log).
