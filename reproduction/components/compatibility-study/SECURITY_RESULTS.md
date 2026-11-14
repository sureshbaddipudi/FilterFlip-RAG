# Task 9 selected security behavior

| Check | Normal | Optimized | Scope / observed detail |
|---|---|---|---|
| candidate_package_isolation | True | True | {"certifi": "<author-home>/Documents/Codex/2026-09-28/we-are-continuing-our-m-tech/work/task05_dependencies/candidate-env/lib/python3.11/site-packages/certifi/__init__.py", "filelock": "<author-home>/Documents/Codex/2026-09-28/we-are-continuing-our-m-tech/work/task05_dependencies/candidate-env/lib/python3.11/site-packages/filelock/__init__.py", "PIL": "<author-home>/Documents/Codex/2026-09-28/we-are-continuing-our-m-tech/work/task05_dependencies/candidate-env/lib/python3.11/site-packages/PIL/__init__.py", "torch": "<author-home>/Documents/Codex/2026-09-28/we-are-continuing-our-m-tech/work/task05_dependencies/candidate-env/lib/python3.11/site-packages/torch/__init__.py", "transformers": "<author-home>/Documents/Codex/2026-09-28/we-are-continuing-our-m-tech/work/task05_dependencies/candidate-env/lib/python3.11/site-packages/transformers/__init__.py", "sentence_transformers": "<author-home>/Documents/Codex/2026-09-28/we-are-continuing-our-m-tech/work/task05_dependencies/candidate-env/lib/python3.11/site-packages/sentence_transformers/__init__.py"} |
| candidate_profile_and_guard_identity | True | True | {"profile": "FilterFlip Task09 ST5.6 local guard v1", "versions": {"ragdefender": "0.2.0", "sentence-transformers": "5.6.0", "transformers": "4.51.3", "torch": "2.8.0+cpu", "numpy": "2.4.6", "scikit-learn": "1.9.1"}, "local_guard_sha256": "2012543e3832281d3fada834e25cd085b007bb028099c1d90d9362a5c582d162"} |
| original_version_profile_refuses_candidate | True | True | {"type": "ValueError", "message": "Dependency mismatch: sentence-transformers"} |
| candidate_profile_refuses_wrong_guard_hash | True | True | {"type": "ValueError", "message": "Candidate local guard mismatch"} |
| affected_CA_root_removed | True | True | {"baseline_has_root": true, "candidate_has_root": false, "scope": "Local bundle membership only"} |
| false_trust_existing_local | True | True | {"loader_calls": [], "error": {"type": "ValueError", "message": "Custom module classes require explicit trust_remote_code=True"}} |
| false_trust_missing_path | True | True | {"loader_calls": [], "error": {"type": "ValueError", "message": "Custom module classes require explicit trust_remote_code=True"}} |
| namespace_prefix_confusable | True | True | {"loader_calls": [], "error": {"type": "ValueError", "message": "Custom module classes require explicit trust_remote_code=True"}} |
| explicit_trust_stub_preserved | True | True | "Harmless in-process stub; no custom file executed" |
| installed_builtin_alias_resolves | True | True | "Installed class lookup, no model weights" |
| actual_constructor_rejects_custom_module_before_loader | True | True | {"loader_calls": [], "error": {"type": "ValueError", "message": "Custom module classes require explicit trust_remote_code=True"}, "weights_loaded": false} |
| malformed_module_config_fails_closed | True | True | {"type": "JSONDecodeError", "message": "Expecting value: line 1 column 11 (char 10)"} |
| benign_exclusive_file_lock | True | True | "Two instances; not hostile-filesystem race coverage" |
| lock_reacquirable_after_release | True | True | "Same workspace file" |
| synthetic_PNG_roundtrip | True | True | "3x3 RGB image only" |
| truncated_synthetic_PNG_rejected | True | True | {"type": "UnidentifiedImageError", "message": "cannot identify image file <_io.BytesIO object at 0x7596e19e9e90>"} |
| synthetic_image_pixel_limit_active | True | True | {"type": "DecompressionBombError", "message": "Image size (9 pixels) exceeds limit of 4 pixels, could be decompression bomb DOS attack."} |

No custom code file or adversarial exploit was executed. Existing fixed local model loading and the real encoder comparison complement these synthetic rejection checks but do not establish all-checkpoint or full attack prevention. Candidate metadata still says upstream 5.6.0; local guard v1 is always part of its identity.

The five version selections and residual 27 advisory clusters are the frozen Task 5 assessment, not a refreshed vulnerability census. See inputs/task05/REPORT.md, candidate/LOCAL_GUARD.json inside that input snapshot, and the unchanged advisory records. File-lock, image and CA checks establish only their stated benign/local properties; no global risk closure follows.
