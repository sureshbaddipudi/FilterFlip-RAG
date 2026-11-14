# FilterFlip-RAG Task 5 — dependency assessment and isolated candidate fixes

31 October 2026 · assistant-prepared assessment for Suresh’s review

**Assessment and candidate preparation are complete.** All 71 preserved component/advisory records have individual relevance assessments, and the fresh lookup adds 12 advisory clusters (nine filelock, three Pillow). Five package upgrades and one explicitly documented local loading guard are staged in a separate candidate environment. The accepted baseline is unchanged. Candidate adoption, scientific compatibility and human acceptance remain unrecorded; selected-change verification belongs to Task 9.

## Main finding: the advisory fix version was insufficient for one guard

The [Sentence Transformers advisory](https://github.com/advisories/GHSA-jhr6-gm9c-rqjv) lists 5.6.0 as patched. In the exact official 5.6.0 wheel downloaded here, the local-module helper still treats an existing local path as implicit trust and emits a deprecation warning. Our harmless stub check reached the dynamic loader once with `trust_remote_code=False`. No custom Python file, model weight, or malicious artifact was loaded. This is an observed helper-level behavior, not an attempted full model exploit.

The isolated candidate adds **local guard v1**: built-in `sentence_transformers.*` classes retain their existing lookup; other module classes require explicit trust before the dynamic loader or fallback import. The same stub check then records zero dynamic-loader calls and a clear refusal. Explicit-trust and built-in class lookup checks pass. This local patch is not attributed to upstream, is not represented as a pristine 5.6.0 installation, and does not establish safety of every configuration/checkpoint path. See [the before/after record](CANDIDATE_RESULTS.md), [diff](candidate/sentence_transformers_local_guard_v1.patch) and [patch identity](candidate/LOCAL_GUARD.json).

## Selected candidate changes

| Component | Accepted baseline | Candidate | Why selected / limit |
|---|---|---|---|
| certifi | 2026.7.22 | 2026.10.19 | Removes the affected emSign ECC G3 root; confirmed against both local CA bundles. Online TLS tooling is a distinct boundary from loopback inference |
| filelock | 3.32.3 | 4.2.1 | Covers the preserved and additional lock-protocol matches; benign exclusion check passes, hostile filesystem races untested |
| Pillow | 12.3.0 | 13.0.0 | Known decoder/processing findings reduced by version; current research path is text-only. Benign PNG check is not parser exploit coverage |
| setuptools | 84.0.0 | 84.1.0 | Packaging hygiene; cited Windows legacy install path is outside this Linux runtime |
| sentence-transformers | 5.1.0 | 5.6.0 + local guard v1 | Direct local-loader boundary; upstream version alone did not enforce our intended trust flag |

Torch stays **2.8.0+cpu** and Transformers **4.51.3**. Their 27 advisory clusters remain in the candidate lookup. Named conversion/training/processor/artifact triggers are not identified in the reviewed BERT/Qwen worker paths, but static absence of an exposed trigger is not proof against every transitive/native path. Major-stack changes require a coherent compatibility assessment; no empty fix list has been filled with an invented version.

## Reconciled counts

| Evidence set | Unit | Count / interpretation |
|---|---|---|
| Preserved ledger | Component/advisory records | 71: certifi 1, filelock 3, Pillow 38, sentence-transformers 1, setuptools 1, Transformers 19, Torch 8 |
| Fresh baseline OSV lookup | Raw IDs / alias-connected component-advisory clusters | 114 / 83 |
| Fresh candidate OSV lookup | Raw IDs / alias-connected component-advisory clusters | 38 / 27 |
| New clusters beyond preserved ledger | Component/advisory clusters | 12, separately assessed; no old finding overwritten |
| Inventory | Installed distribution metadata | 43, including editable vendored RAGDefender; only 42 queried as PyPI packages |

Counts use explicit ID/alias connections separately per component. They are not exploit counts, severity scores or the teammate report’s still-unreconciled scanner totals. CPU Torch queries normalize `2.8.0+cpu` to upstream `2.8.0`; neither lookup is a CPU-build-specific attestation. No findings were suppressed by ignoring IDs. The candidate's local patch is invisible to version-based matching, which is why the behavioral check is retained separately. In particular, a scanner count dropping does not justify claiming every selected risk solved.

Sources: [original frozen scanner records](sources/validation/DEPENDENCY_AUDIT.json), [preserved ledger](sources/validation/OPEN_DEPENDENCY_FINDINGS.json), [fresh query and binding](validation/OSV_QUERY.json), [raw response](validation/OSV_QUERY_RESPONSE.json), [alias reconciliation](validation/ALIAS_RECONCILIATION.json). The online source is [OSV](https://osv.dev/); full cited advisory snapshots and retrieval hashes are included. Three CVE lookups returned 404; their explicit GHSA aliases supplied the records. No missing response was silently treated as no risk.

## Evidence and remaining work

The final candidate passes eight installation/API/helper checks and `pip check`. The checks cover package isolation, required imports, the affected CA removal, benign locking/PNG operations and the narrowly defined trust guard. They do not construct an encoder, generate embeddings, start Ollama or produce an answer. [Preservation checks](validation/PRESERVATION_CHECK.json) compare the full accepted environment tree and all 156 app release entries. The separate candidate uses copied distribution files, not system site-packages or package hardlinks; its base Python standard library/native runtime and editable vendor source remain shared read-only assumptions.

The original native version guard will reject the candidate’s changed Sentence Transformers version. That is expected: this assessment does not edit the release profile or silently bypass its checks. Task 9 must use a separately versioned compatibility profile, verify the selected security behavior and compare numerical/retrieval/filter/answer behavior before any adoption decision. Task 6 separately reconciles application-testing claims and UI release binding.

The 42 queried top-level distributions do not cover nested vendored tooling metadata, operating-system libraries, the CPython interpreter, all native bundled libraries, Ollama/service management, provenance/backdoors in pretrained weights, or the vendored RAGDefender source. Their inventory/trust limits remain explicit; no clean whole-system bill of health is issued. No Desktop file, frozen source, raw review, accepted result or model setting was modified. Primary **8/51/0**, mixed Week-6 findings and **R110 uncertain** remain unchanged. No new scientific label or reviewer decision is inferred.

## Packet navigation

- [Individual preserved assessments](FINDING_ASSESSMENTS.md) and [12 fresh additions](FRESH_ADDITIONAL_ASSESSMENTS.md).
- [Reviewed call paths and scope](REACHABILITY_SCOPE.md), including the difference between transitive import and reaching a vulnerable operation.
- [Candidate checks and local guard](CANDIDATE_RESULTS.md), [reproduction guide](REPRODUCTION_GUIDE.md), and [Task-9 verification handoff](TASK09_HANDOFF.md).
- [Status record](TASK05_STATUS.json), [source hashes](SOURCE_MANIFEST.json), and [offline validation](validation/PACKET_CHECK.json).
