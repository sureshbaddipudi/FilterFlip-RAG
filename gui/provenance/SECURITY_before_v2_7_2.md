# v2.6 scope update

New fixed variants mode accepts only the nine original condition codes for existing 59 cases, with two planned U/N requests. Existing mitigation/challenge eligibility is unchanged. The saved /api/study route maps an exact case ID through the sealed catalog; browser input never becomes a file path. Source/reference/review content is rendered with textContent. Existing localhost, host/origin/token, framing, job/time/resource/process and integrity controls remain in use. No dependency upgrade or advisory rescan is claimed. See ../VALIDATION_REPORT.md for current checks and retained limits.

## Historical security record

# Security evidence and remaining risks — review demo v2

## Status and scope

This release is a **local, single-user classroom demonstration with documented residual risks**. It is not approved for public hosting, arbitrary uploads, arbitrary models, or untrusted local users. Development checks are not independent teammate acceptance. The frozen research environment has open dependency advisories; no claim of “all vulnerabilities fixed” or OWASP certification is made.

Trusted: the operating-system account, local configuration, pinned interpreter/vendor/model files and distributed checksum. Untrusted: browser requests, retrieved/generated text and incomplete backend responses. Assets: original evidence, reviewer attribution, local files, compute capacity and reproducible outcomes. Research attacker: one controlled corpus copy, or a separately approved fixed challenge fixture. The challenge’s evaluator metadata and human verdicts never enter the filter or generator request.

Data flow: browser -> guarded localhost API -> one owned worker group -> frozen text/index + native filter -> dedicated localhost Ollama -> bounded raw responses -> private run folder -> literal-text GUI/export. Recorded research remains a separate view.

## Threat / requirement / code / verification

| ID | STRIDE | Requirement and implementation | Evidence / limitation |
| --- | --- | --- | --- |
| SEC-01 | Spoofing | Bind 127.0.0.1; exact Host/Origin; reject cross-site fetches; mutation nonce (`server.Handler.guard`) | HTTP host/origin/nonce tests. Nonce is CSRF protection, not login; local processes remain trusted. |
| SEC-02 | Tampering | Strict JSON, duplicate/nonfinite rejection, exact fields and allowed case/mode/condition (`safety.check_selection`) | HTTP and selection tests; excluded challenge cases cannot launch. |
| SEC-03 | Tampering | Manifest before serving and before worker; pinned vendor, model, package, request and template identities | Manifest-tampering test; run identities; unchanged policies; offline 1,288-mapping parity. Hashes are not independently signed releases. |
| SEC-04 | Information disclosure | Only fixed routes/assets; validated run IDs; no arbitrary path, upload or browser-supplied URL | Traversal, file-disclosure and symlink tests; private run folder and atomic mode-0600 writes. Local export intentionally includes evidence and model metadata. |
| SEC-05 | Injection / elevation | DOM `textContent`; fixed subprocess argument lists; no shell evaluation; fixed loopback model endpoint, proxies disabled and redirects refused | Browser rendering inspection, redirect test, Bandit dispositions. Model instructions inside retrieved text remain a research risk. |
| SEC-06 | Denial of service | One job, eight HTTP workers, 1 KiB JSON bodies, 8 KiB parsed headers, 3-second sockets; four answer attempts, 590 seconds/request, 2,400 seconds/job | HTTP size/framing tests; second-job refusal; actual worker timeout tests. OS parser has its own prior header limits. |
| SEC-07 | Denial of service | 60-run / 1 GiB archive admission bounds, 1 GiB free-disk admission; stop at 128 MiB run output or <256 MiB free disk; 2 MiB model-response cap | Synthetic output-limit test. Poll-based disk limits are not atomic filesystem quotas; no hard memory/cgroup quota. Local compute can still cause pressure. |
| SEC-08 | Denial of service / integrity | Kill only owned worker process group, including descendants; retain partial evidence; overall job state is authoritative | Synthetic descendant/listener cleanup, cancellation, timeout and crash tests; real integration records. Shutdown under every native/Ollama failure is not proven. |
| SEC-09 | Repudiation | Unique run ID, timestamps, exact requests, raw model-response files and events; no automatic retry/resume | Integration audit joins requests/raw replies; changed/failed outputs preserved. Logs are local and mutable, not independently timestamped. |
| SEC-10 | Integrity | Preserve first-pass/individual/joint review records; current 59-case ledger is separate from historical assessments and new outputs | Copied source checksums; GUI recorded-case review; new-run semantic status remains pending. |
| SEC-11 | Exceptions / disclosure | Invalid/truncated answers stop and remain incomplete; retain primary backend error; safe public error text | Status/exception tests; retained raw bytes before JSON parsing. Detailed local console may contain local paths; export only to intended reviewers. |
| SEC-12 | Supply chain | Flat dependency SBOM, pinned hashes, advisory/static scans, secret-pattern scan; external audit tools isolated from research environment | `validation/` artifacts and open-advisory ledger. No patch was applied to the accepted environment; see below. |

## OWASP Web Top 10:2025 coverage

| Category | Treatment and status |
| --- | --- |
| A01 Broken Access Control | SEC-01/02/04. Local trusted-account boundary; multi-user ownership checks are not implemented. |
| A02 Security Misconfiguration | Loopback-only, strict CSP/no-store/no-sniff/frame denial, offline model flags, CPU profile. Public deployment unsupported. |
| A03 Software Supply Chain Failures | SEC-03/12. Inventory and scans completed; dependency advisories remain open. |
| A04 Cryptographic Failures | No passwords or remote session transport. Hashes used only for integrity; no TLS on loopback and no signing claim. |
| A05 Injection | SEC-02/05; text rendering, fixed arguments and no dynamic code execution of passage data. |
| A06 Insecure Design | Threat boundaries, approved fixtures, policy/output budgets, separate research labels. No general prompt-injection defense claim. |
| A07 Authentication Failures | No account system; local single-user deployment only. CSRF token is not authentication. |
| A08 Software or Data Integrity Failures | SEC-03/09/10; verified input/output identity and preserved review history. Mutable local records remain a limit. |
| A09 Security Logging and Alerting Failures | Run events, raw replies and failure logs. HTTP access/security-event monitoring and external alerting are not provided. |
| A10 Mishandling of Exceptional Conditions | SEC-06/07/08/11; partial states, strict parsing and stop-on-fault tests. |

## OWASP API Security Top 10:2023 coverage

| Category | Treatment and status |
| --- | --- |
| API1 Object-level authorization | Known cases and validated private run IDs; no multi-user ownership model. |
| API2 Authentication | Local boundary and request guards, not a remote authentication system. |
| API3 Object-property authorization | Exact mutation fields; browser cannot choose paths, endpoints, model settings or reviewer identity. |
| API4 Resource consumption | SEC-06/07/08; caps tested, hard OS memory/disk quotas remain absent. |
| API5 Function-level authorization | Fixed GET/POST inventory; other methods rejected; no admin/upload route. |
| API6 Sensitive business flows | Starting a compute job is one-at-a-time and bounded. No payment/account business flows. |
| API7 SSRF | Fixed localhost address, no redirects/proxies or browser-supplied fetch URL. |
| API8 Misconfiguration | Fixed loopback, security headers, restricted profile; no public deployment. |
| API9 Inventory management | GET `/`, `/app.js`, `/style.css`, `/api/bootstrap`, `/api/reference/<case>`, `/api/runs/<id>`; POST `/api/runs`, `/api/cancel`; HEAD mirrors GET. Ollama has a separate temporary localhost API. |
| API10 Unsafe API consumption | Response byte/schema/token bounds, model/version/template checks, raw failure capture; malformed-response tests. |

These are applicability and evidence mappings, not a declaration that all 20 categories are fully resolved. ASVS is used as a requirements reference; this package does not claim a completed ASVS level. Secure-development work includes requirements, design review, bounded coding, tests, dependency review, release integrity and a separate teammate acceptance step, consistent with NIST SSDF.

## Dependency audit: important remaining work

The pinned environment inventory contains 43 Python distributions. The first audit returned 73 advisory records, including duplicates, across six packages. Deduplication gives 63 advisory IDs. The local `torch==2.8.0+cpu` build was not recognized by the registry; a separate query for upstream `torch==2.8.0` returned eight more advisories. **71 unique component/advisory records remain open**, with the Torch normalization explicitly qualified. Version matching does not by itself establish reachability; some descriptions concern other versions/platforms or unused features. No finding is silently treated as fixed.

- **sentence-transformers:** local-model loading can bypass `trust_remote_code=False` below 5.6.0. This is relevant to model loading. The application hashes the frozen `modules.json`, configuration, weights and tokenizer before load. The observed module types are built-in Transformer/Pooling/Normalize, and the inspected snapshot contains only the expected non-Python assets. Users cannot upload/select models. These reduce exposure under the trusted-local-files assumption; they do not patch the dependency or protect against a compromised local account/race.
- **transformers / torch:** scanner findings include checkpoint/model loading, training/conversion and other operations. This demo uses fixed text inference and hash-verified safetensors; no checkpoint conversion, training, user model, image or arbitrary tensor API is exposed. Per-advisory exploitability is not fully established; the findings remain open.
- **Pillow:** image parsing/encoding advisories are reported. The application accepts no images or uploads and does not call image processing. Still retain the dependency findings.
- **filelock:** local lock-directory and platform-specific advisories are reported. No browser path selection is exposed; cache ownership/permissions are an operator responsibility.
- **certifi:** CA-store advisories matter for remote HTTPS. Research execution is local and offline, but this is not a reason to use the old environment for downloading/installing software.
- **setuptools:** an installation-path advisory is reported; the demo does not install wheels at runtime.

Do not upgrade the accepted environment in place. The remediation path is a separate application/runtime environment with patched dependencies, fresh hashes, and a bounded compatibility/sentinel check before claiming scientific equivalence. No such patched-runtime validation or independent risk acceptance is claimed here. Until then, keep the demo local, fixed-input and non-administrative; do not expose it publicly or add uploads/custom model directories.

Ollama, the OS, the Python interpreter and vendored RAGDefender are inventoried separately but not comprehensively covered by the PyPI audit. Their unreported vulnerabilities must not be interpreted as zero vulnerabilities.

## Static scan dispositions

Bandit reported seven low-severity findings: three subprocess imports, three subprocess invocations and one tokenizer `eos_token` reported as a possible password. Subprocesses use fixed argument lists and trusted local executable configuration, with no shell; this is intentional functionality. `<|im_end|>` is a model delimiter, not a credential. These are developer dispositions, pending teammate inspection. There were no medium/high findings in this bounded scan; that does not prove their absence.

## References

- [OWASP ASVS](https://asvs.owasp.org/)
- [OWASP Web Top 10:2025](https://top10.owasp.org/2025/)
- [OWASP API Top 10:2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- [NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final)
- [Sentence-transformers local-loading advisory](https://github.com/advisories/GHSA-jhr6-gm9c-rqjv)
