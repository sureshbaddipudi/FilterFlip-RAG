# Task 5 — candidate execution record and limits

The candidate environment contains a full copy of the 43 installed distribution trees. No baseline-package symlinks/hardlinks or system site-packages are used. A standard virtual environment still uses the original base Python standard library/native runtime, and the editable RAGDefender finder refers to the original frozen vendor source. This is package isolation, not an OS/container sandbox. Exact locations and design are in candidate/ENVIRONMENT_DESIGN.json.

Five official wheels were downloaded from the explicitly selected PyPI index with dependency resolution disabled, checked against official release SHA-256 metadata, and installed only in the candidate. Published requirements allow the retained Torch/Transformers versions; `pip check` also reports no broken requirements. Exact versions, filenames, hashes and URLs are in candidate/WHEEL_MANIFEST.json and PACKAGE_METADATA_INDEX.json. No wheel was yanked. An index/hash comparison is not a digital signature.

## Behavioral discrepancy and local patch

1. Upstream 5.6.0 helper check: seven of eight checks passed. The intended property “false trust flag blocks local dynamic loading” failed: the stub was called once and the helper warned, then returned its sentinel.
2. A candidate-only local guard was applied before the dynamic/fallback branch. Non-builtin class references now require explicit trust. Built-in namespace handling is retained.
3. The final candidate passed all eight checks. The false-trust case refuses with ValueError and records zero stub calls; the explicit-trust and built-in lookup cases still work.

See validation/CANDIDATE_CHECK_upstream_5_6.json and CANDIDATE_CHECK_local_guard.json, with their logs. No malicious Python file or model was executed. The mocks isolate a specific helper property; they do not show full model-loader exploitability or complete prevention of arbitrary execution. The patch’s exact before/after hashes and wheel binding are in candidate/LOCAL_GUARD.json. Original upstream distribution metadata still says 5.6.0; the local modification must always be disclosed beside it.

## Other checks

- Package paths for the six relevant imports resolve inside the candidate. Required SentenceTransformer and Qwen2Tokenizer APIs import; no model is constructed.
- The accepted certifi bundle contains the affected emSign ECC G3 root; the candidate bundle does not. This is a local certificate-store check, not a live network attack.
- Two file-lock objects respect a benign exclusive hold in a temporary workspace directory. No symlink/lease/oplock/journal exploit was executed.
- A synthetic 2×2 PNG round-trips. No vulnerable image corpus or native-code coverage claim follows.
- `pip check` passes. The version diff changes exactly five distributions; Torch/Transformers and other distribution versions are retained.

An initial import-check invocation stopped because the sandbox did not permit system temporary directories, before producing check results. The correction confined temporary storage to the Task-5 workspace. This is preserved in validation/INITIAL_CHECK_ENVIRONMENT_FAULT.json rather than labeled a dependency incompatibility. An earlier escalated tool request timed out in automatic permission review before its command started; the checks subsequently ran using the granted workspace permissions. No required check remains blocked by that timeout.

The fresh candidate lookup has 38 raw advisory IDs forming 27 component/advisory clusters, on retained Torch and Transformers. The version lookup alone omits the ST 5.6 behavioral problem; that is why the separate before/after evidence remains essential. No baseline finding is closed and no candidate is deployed by this record. Task 9 must establish the remaining security and scientific compatibility checks.

## Inventory enumeration qualification

Importing setuptools exposes bundled tool metadata on the import path. An unrestricted metadata listing initially appeared to add distributions and change duplicate packaging/wheel versions. The installed-tree comparison now explicitly enumerates only candidate purelib: exactly 43 top-level distributions with five version changes. The import-context listing is preserved separately, as is the bundled tool inventory. The 42-per-profile OSV requests were built from the original top-level baseline inventory and five replacements, so their bindings are unaffected. Nested setuptools tooling is not claimed covered by that top-level lookup. See validation/INVENTORY_ENUMERATION_NOTE.json.
