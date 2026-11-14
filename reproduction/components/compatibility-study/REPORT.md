# Task 9 — selected security fixes and research compatibility

Recorded 1 November 2026, Asia/Kolkata. **Task 9 verification is complete within the recorded bounded scope. The candidate passes the selected security and research-compatibility checks. It has not been adopted or deployed.** The accepted environment, Task 5 candidate, frozen evidence and Desktop remain unchanged.

## What was verified

The existing isolated candidate changes certifi 2026.7.22→2026.10.19, filelock 3.32.3→4.2.1, Pillow 12.3.0→13.0.0, setuptools 84.0.0→84.1.0 and Sentence Transformers 5.1.0→5.6.0 **plus the disclosed local loading guard v1**. Torch 2.8.0+cpu, Transformers 4.51.3 and the other frozen research settings remain unchanged. This is not a pristine upstream 5.6.0 installation.

A separate candidate application copy changes only its dependency profile, an explicit runtime guard-identity check and the corresponding manifest. The original app/profile still rejects the changed ST version and is unmodified. [CANDIDATE_BUILD_DIFF.json](CANDIDATE_BUILD_DIFF.json) binds the exact tested source hashes; [profiles/candidate.json](profiles/candidate.json) additionally requires the separate virtual environment and exact local-guard helper hash.

| Verification | Execution | Result |
|---|---|---|
| Targeted candidate security behavior | 17 distinct checks, normal and -O | PASS |
| Application regression | 42 tests, baseline and candidate, normal and -O | PASS in each run |
| Package requirements | pip check in both environments | PASS |
| Synthetic model-API transport | 7 checks per environment, normal and -O | PASS; local fixture only |
| Comparator boundary/regression controls | 5 tests; no inference | PASS |
| Encoder probes | 75 distinct texts ×384 dimensions; token IDs | Bit-identical embeddings and IDs |
| Retrieval/filter/request comparison | 72 retrieval contexts +3 challenge contexts per profile | Identical current baseline/candidate |
| Logical answer-request positions | 300 per profile; 146 distinct canonical requests | Bytes and Qwen token IDs identical |
| Environment preservation | 42,453 baseline +34,984 candidate file/link entries | Full before/after maps identical |

These rows have different units and repeated modes; they are not summed into a total vulnerability count, independent scientific trials or a whole-system security certificate. Full logs and synthetic captures are in validation/ and results/transport/.

## Security behavior

The local guard refuses non-builtin class references with trust_remote_code=False before either dynamic loading or fallback import. Tests cover an existing directory, a missing path and a namespace-prefix lookalike. A harmless explicit-trust stub still works, and the installed Pooling alias resolves. Crucially, **the actual SentenceTransformer constructor rejects a synthetic custom-module configuration before either stub loader runs**. Malformed module JSON also stops loading. No custom Python file, exploit model or scientific weight was loaded by these security rejection checks. Both normal and optimized Python preserve the refusals.

The candidate CA store lacks the affected emSign ECC G3 root present in the baseline. Benign exclusive-lock/release checks pass. Small synthetic PNG round-trip, malformed PNG rejection and a deliberately tiny fixture pixel-limit check pass. These are bounded behavior checks, not hostile filesystem race coverage, native decoder exploit coverage or proof of every loader/configuration path. [SECURITY_RESULTS.md](SECURITY_RESULTS.md) maps each observation to its retained limit.

All 42 existing application tests pass on both builds in normal and optimized modes. They check the local HTTP/input/control/lifecycle/partial-evidence boundaries with synthetic workers, not real Qwen outputs. The separate seven-check transport fixture uses actual serialization, response-status and redirect code over ephemeral loopback HTTP: transmitted canonical request bytes, raw fixture capture, valid stop, truncation, malformed response, redirect refusal and response-size bound. It never launches Ollama.

## Research compatibility

[VERIFICATION_PLAN.json](VERIFICATION_PLAN.json) was recorded before these compatibility measurements. Eight historically selected cases (four per dataset), all nine copy conditions and the three approved Heather challenge contexts give **75 paired contexts**. Selection covers accepted events, the one/two-copy reversal, core/mixed rules, surviving alternative support, absent frozen support and a material reproduction difference. It is deliberately small and non-random.

Both profiles use the same hash-verified MiniLM files, tokenizer, original corpus embedding index, vendor code, seeds and CPU settings. Query/copy embeddings are fresh; the full corpus is not re-embedded. The 75 fixed probe embeddings and token IDs are bit-identical. Fresh checks of 40 selected original corpus chunks differ from cached embeddings by at most **8.20×10⁻⁸** in both profiles, within the predeclared 10⁻⁶ maximum /10⁻⁷ mean embedding tolerances. These sampled checks do not certify every corpus embedding under a rebuilt index.

**Candidate versus fresh baseline:** all 75 retrieved ordered passage/text sequences, added chunks, passage token IDs, U/N/E/CN groups/representatives/survivors, similarity scores and request/token-ID records match. This covers **300 logical request positions /146 distinct canonical requests**, with no new answer generation. Request text/options, Qwen prompt token IDs and context budgets are unchanged. [COMPATIBILITY_MATRIX.md](COMPATIBILITY_MATRIX.md) lists every context; [raw paired results](results/research_comparison/CONTEXT_COMPARISONS.json) retain numeric and discrete comparisons.

**Fresh baseline versus archive:** only 67 of 72 retrieval contexts have identical ordered document IDs. In the other five, equal-text document instances appear in a different order; supplied text, native survivor positions and U/N request bytes remain identical in all 72. The candidate exhibits exactly the same five differences. Thus these are documented current-baseline/archive identity differences, not an observed upgrade effect. [ARCHIVAL_DIFFERENCES.md](ARCHIVAL_DIFFERENCES.md) retains both ID sequences and scores. No numerical tie tolerance was used to hide an upgrade-induced rank change; the candidate/current-baseline ID comparison is exact. No selected cutoff gap is within the frozen 10⁻⁸ near-tie screen; ties or near-ties elsewhere are not thereby excluded.

The two real encoder profile runs took 131.315 and 133.156 active seconds. Each used 373 encode calls and 225 native-filter calls, under the fixed 1,000-call /1,800-second per-profile bounds. The rejection constructors above used synthetic configurations without loading scientific weights. Research generation attempts: **zero**.

## Answers and remaining limits

No fresh Qwen service or semantic answer rerun was needed: candidate/current-baseline requests, options and token IDs are identical, and the selected changes do not replace the Ollama generator. This verifies answer-input and synthetic protocol compatibility. **It does not prove that a future generation will reproduce identical words or scientific judgments.** Historical/native model outputs and accepted reviews are retained, not relabelled as fresh candidate answers. TrustRAG's separate SimCSE stage-1 encoder and later stages were not rerun.

The Task 5 frozen 31-October candidate lookup still records **27 advisory clusters on retained Torch/Transformers**. This is dated evidence, not a fresh exhaustive 1-November scan. No finding is silently closed. The local guard is narrower than universal custom-code/weight/config safety; fixed local model hashes and no browser-selected models remain important assumptions. CPython/native/OS libraries, nested vendored tooling, public/multi-user deployment and malicious-model or hostile-race testing remain outside this verification. No full browser/XSS rehearsal was performed in Task 9; static UI/source bytes are unchanged, and Task 6 acceptance remains separately scoped.

The candidate logs a deprecation warning for the dimension-query API; it still returns the frozen 384 dimensions. One comparison-test harness initially failed before tests started because isolated Python omitted its code directory. The explicit import path was corrected; all five controls then pass. The initial log and correction are retained as a test setup issue, not a dependency incompatibility, model fault or model retry.

## Preservation and disposition

Full before/after file-content hashes and symlink targets match for both environments. The 332 named source snapshots/originals and 36 model/vendor/reference assets also match after execution. [PRESERVATION.md](PRESERVATION.md) records the scope. Temporary fixtures/caches and all new outputs stay inside Codex. No accepted release, model file, source selection, human judgment or Desktop deployment was edited.

The result supports the candidate **only for this bounded verification profile**. Adoption/deployment and human residual-risk acceptance remain unrecorded; the original accepted baseline remains the project baseline. This verification does not create a new human scientific sign-off. Task 7 remains the joint, purely human review by Shradha and Suresh without AI assistance in those reviews. Task 8's annotation differences remain unchanged. Accepted primary **8/51/0**, mixed Week-6 findings and **R110 uncertain** remain unchanged.

Task 10, literature positioning and novelty assessment, is next and has not begun. Larger datasets, a new mitigation programme, broad model sweeps and later TrustRAG work remain deferred.
