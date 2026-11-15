# Disposition of the v2.7.2 SSE assessment

10 November 2026. The supplied assessment is preserved unchanged in `review_input/SHRADHA_V272_ASSESSMENT.md`. Its reported live runs and browser walkthrough are not relabeled as new v2.8 acceptance or semantic adjudication. No underlying research outcome is changed.

| Finding | v2.8 treatment |
|---|---|
| W1 Configuration protection | Startup and backend require a user-owned owner-only regular config file without links, outside the release; immediate parent must be user-owned and not group/other writable. The helper creates a new private work folder. This does not defend against compromise of the trusted account or arbitrary ancestor replacement. |
| W2 Dependencies | Remain open. `filterflip-core` and `filterflip-repro` inventories/scanner outputs are needed for an exact reconciliation. No dependency upgrades or profile substitution in this GUI release. See DEPENDENCY_RECONCILIATION.md. |
| W3 Security logging | Added private bounded event logging for POST requests and error responses. Only fixed route/method classes, status, time and validated run IDs are logged; no raw headers, tokens or bodies. Existing per-run research logs remain. Logging failures report degraded operation without exposing details to a browser. No authenticated human identity or tamper-proof audit claim. |
| W4 Local-host trust | Retained explicitly. Adding the existing obtainable token to GET routes would not create shared-host authentication. No public/multi-user deployment claim. |
| W5 Verification/load gap | Retrieval script is read once by the loader, hashed, compiled and executed from those same bytes. A mutation test replaces its disk contents after the read and confirms only the verified content executes. Other trusted-file load paths retain their documented local-account assumptions. |
| W6 Integrity authenticity | Application verification now rejects unexpected/missing files throughout the app and linked content. The full packet checker lists mismatches. Unsigned manifests remain consistency checks, not independent authenticity; an external ZIP checksum is supplied. |
| W7 Pins/port | Retained for scientific comparability. No arbitrary browser-selected versions or model ports. Shared-host isolation remains separate work. |
| W8 Run limit | Added explicit offline preview/apply archiving with a server lock, terminal-state checks and preservation receipts. No automatic deletion. |
| W9 Packet errors | Lists missing and unexpected file paths. |
| W10 Browser headers | Added Permissions-Policy and Cross-Origin-Opener-Policy. Loopback HTTP remains within the existing local deployment. |
| W11 Personal paths | Active launch instructions now use a placeholder. Original historical provenance is preserved and may contain local paths; a publicly redacted distribution would be a separate derived artifact. The config seen in the tester's extracted folder was not in the sealed source release. |
| W12 Permissions | Packaged ordinary files are 0644 and directories 0755; external configuration/run files are private. Extraction behavior remains platform-dependent. |
| W13 Model manipulation | Research limitation retained. The recorded nine instruction tests have zero followed instructions; merely containing a challenge does not establish successful injection. False-claim harms and uncertainty remain visible. |
| W14 Static findings | Reassessed on current production code with raw scanner output retained. Reviewed warnings are not suppressed just to obtain a clean score. |
| W15 Cancellation errors | Invalid/extra cancellation fields consistently return 400. Unknown routes still return 404. Percent-encoded aliases remain unsupported. |

## Scope clarifications for Q1–Q3

- Q1: The absence of live TrustRAG generation was intentional. v2.8 adds recorded per-case evidence only.
- Q2: The recorded project history does not establish a promise of full TrustRAG live generation. This update makes the completed stage-1 extension inspectable without changing that scope.
- Q3: The accepted stage-1 contexts, endpoints and exact saved answers are now explicitly included as derived display data. Source files, review references and transformations are retained in provenance. They were not part of the previous GUI's live-run scope.

## Corrections to assessment wording

The application already retained run evidence; missing security-request logging was the gap. Reduced-threshold timeout/output tests existed, and supplementary archive/disk admission checks existed separately. Full production-duration/size stress tests were not claimed. The 82-advisory and 81-cluster scans concern different environments and scopes. MITRE T1070 denotes deliberate indicator removal, not simply absent logs. Framework identifiers in the submitted draft still need a complete checked mapping before course submission.
