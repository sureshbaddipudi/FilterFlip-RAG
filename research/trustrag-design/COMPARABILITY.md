# Task 3 comparability and compatibility matrix

31 October 2026. PASS below means the named offline check passed; it does not mean the implementation or experiment has run.

| Dimension | Evidence/check | Status | Interpretation |
|---|---|---|---|
| Case selection | Component plan equals original secondary_case_ids: 12 IDs, 6 per dataset | PASS | All cases retained; reused selected sample |
| Retrieval | All 36 inputs equal saved main-study contexts, including text/order | PASS | A common retrieved-context basis |
| TrustRAG output mapping | Native indices, output text and chunk IDs agree; partitions valid | PASS | Preserve native order and three empty outputs |
| Frozen component provenance | Result/review manifests, runner/adapter files and pinned upstream input hashes match | PASS | Existing saved evidence can be reused |
| Prior component replay | Saved validation reports 36 matching embedding-only replays; separate rerun selected-field comparison has zero differences | Recorded prior evidence | No fresh filter replay performed in this design |
| Component algorithm/configuration | TrustRAG SimCSE + scaling/normalization/k-means/ROUGE versus RAGDefender MiniLM/native pipeline | Qualified | Configurations differ; no algorithm-only attribution |
| CPU adaptation | Original one-call CUDA-input substitution, CPU float32/eager attention, native function bodies retained | Documented limitation | GPU numerical equivalence untested |
| Native output order | Three T outputs differ from retrieval-index sorting | PASS, must preserve | Do not reorder for apparent comparability |
| Empty context | Three signal-transduction T positions share one empty-context request | PASS, retained | No fabricated abstention or case exclusion |
| Prompt and settings | Same main-study evidence-only system/user template and options | PASS | Controlled U/T answer protocol; not full TrustRAG stage 2 |
| Request identity | 72 logical positions → 60 full-request hashes; 44 historical matches, 16 novel | PASS | Primary plan generates all 60 fresh; same-run reuse only |
| Token accounting | Frozen Qwen assets reproduce 1,062 original estimates; new range 72–949 | PASS | Maximum reserved budget 1,141/4,096; no trimming needed |
| Local model assets | Binary/model-manifest/template hashes match; weight blob exists at expected size | Partial offline verification | Full weight rehash and served identity not claimed |
| Runtime/server preflight | No model loaded or service queried | PENDING stage 2 | Must verify identities, actual token counts and CPU request |
| Runner/recovery correctness | Acceptance checklist specified; no experiment runner written | PENDING stage 2 | Tests must precede study calls |
| Semantic support/answers | Earlier component review is assistant-authored; no new answers exist | PENDING task 7 | Preserve attribution; no automatic transfer of primary labels |
| Historical answer comparisons | Original and task-1 panels retained separately | Qualified | Cross-session/machine effects; no new primary arm filled from old cache |
| Generalization | Twelve selected questions, same historical subset | Limited by design | No population event rate, broad robustness or full-defense claim |

## Component settings retained as historical input provenance

TrustRAG commit `11dcea0262d14b0e38e22e1d7ddce4a151e82a61`; default kmeans_ngram with n_gram=True; SimCSE revision `2d82fab19ac3a73a20dd20333d27eb8a52d6e97f`. Single-sentence encoding, last-layer CLS, raw vectors, StandardScaler, row normalization, KMeans(2 clusters, n_init=10, max_iter=500, random_state=0), native ROUGE-L stemming and thresholds. Original component runtime: CPU float32, eager attention, four threads, seed 12. Its 82 unique passages had no recorded SimCSE truncation. These embeddings, clustering calls and thresholds are not rerun or tuned in this answer-extension design.

The proposed evidence-only Qwen path is an explicit hybrid extension. The published method also has LLM self-assessment, which is outside this approved experiment. [TrustRAG paper](https://arxiv.org/abs/2501.00879v3). Current scope follows the October 30 handover, even though the preserved older full-system proposal describes a different future experiment.

## Sources actually inspected

The check script and SOURCE_MANIFEST.json identify exact local records. Inspected records include the current handover and task-2 status; TrustRAG protocol, plan, runner, adapter, result/review manifests, raw outputs, summaries, environment, prior validation/trace and assistant support review; original retrieval/filter inputs; main-study answer request builder, full calls, model setup, frozen tokenizer assets and historical preflight; task-1 logical answers/runtime plan; and the pinned local model manifest/binary. The online arXiv abstract was checked for the two-stage claim. No new literature survey or claim of novelty was performed.
