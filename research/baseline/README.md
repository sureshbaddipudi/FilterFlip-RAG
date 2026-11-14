# Baseline study

The study asks whether a RAG system can still give a supported answer when its document collection contains duplicate evidence. We followed the evidence through retrieval, filtering and answer generation so we could identify where support for an answer was lost.

## What we compared

We studied selected questions from NanoNQ and NanoMSMARCO. For each question, the primary comparison used a clean corpus (C), a corpus with one copy of a background passage (BN1), and a corpus with one copy of an answer source (PN1). The background condition helps distinguish the effect of adding a passage from the effect of duplicating evidence for the answer.

For each condition, we inspected the retrieved passages, the passages retained by RAGDefender, and answers generated with and without the filter. Reviewers checked whether the retained evidence actually supported the answer. Across the 59 selected primary cases, eight met the study endpoint. The [paired results](../../reproduction/components/paired-results-analysis/expected/) give the recorded summaries.

## Baseline materials

- [Artifact sources and attribution](LICENSES_AND_SOURCES.md) identifies the upstream projects, datasets and revisions. Local provenance paths in that document refer to the original semester handover.
- [Model inventory](models.json) records the encoder revisions and file checksums.
- [Core Python requirements](requirements-core.txt) records package versions used in the baseline environment.

See the [literature comparison](../literature/LITERATURE_MATRIX.md) for the research context and the [project README](../../README.md) for instructions to reproduce the study figures.

## How the study questions were selected

The [preparation scripts](reference/output/filterflip_study_v1/) record how the team obtained pinned dataset revisions, checked question-to-document links, screened for overlap with earlier examples, and checked reviewers' evidence quotes. The full screening run uses the original handover's dataset files and earlier study records. To run the self-contained preparation tests from the repository root using Python 3:

```bash
python3 -B -m unittest discover -s research/baseline/reference/output/filterflip_study_v1 -p test_preparation.py
```

At the initial screen, one of 100 candidate questions overlapped with earlier work. The remaining 99 went forward for source review. See the [selection rules](reference/output/filterflip_study_v1/SOURCE_SELECTION.md), [recorded screening counts](reference/output/filterflip_study_v1/screened/screening_summary.json) and [dataset acquisition record](reference/output/filterflip_study_v1/sources/acquisition.json). The 59 primary cases reported above belong to the later outcome evaluation.

### Which questions entered the primary study?

| Dataset | Starting questions | Prior overlap | Reviewed for source support | Excluded at source review | Eligible |
|---|---:|---:|---:|---:|---:|
| NanoNQ | 50 | 1 | 49 | 14 | 35 |
| NanoMSMARCO | 50 | 0 | 50 | 26 | 24 |
| **Total** | **100** | **1** | **99** | **40** | **59** |

The [case-level eligibility table](reference/output/filterflip_study_v1/screened/source_eligibility.csv) joins the original screening records to the frozen source decisions and retrieval case manifest by case ID. The overlap exclusion has a blank source decision because it did not proceed to source review. In the overlap-screen column, `pending_support_review` records the status before source eligibility was decided.

The last column preserves the manifest's original source-review status for eligible cases. At selection, 24 carried `user_recorded_review` and 35 carried `assistant_only`. Later human confirmation concerned the recorded experimental outcomes. The table describes how questions entered the study, before those outcomes were known.

## What the retriever found

Each eligible question contributed five retrieved passages in each of nine corpus conditions. In the clean corpus, the designated answer source appeared in the top five for 39 of 59 questions. With one prefixed answer-source copy (PN1), the original or its copy appeared for 41 of 59. A retrieved passage can come from the right document yet omit the sentence needed to answer the question. The filtering and answer reviews address that separate question.

The [case-level retrieval indicators](reference/output/filterflip_study_v1_retrieval/retrieval_indicators.csv) summarize the saved contexts. A value of 1 means the indicator was observed for that question and condition. The [original summary](reference/output/filterflip_study_v1_retrieval/results/retrieval_run1/summary.json) gives totals by condition. The [original structural audit](reference/output/filterflip_study_v1_retrieval/RESULT_AUDIT.json) records the checks performed on the full retrieval evidence at that stage. To recount the published indicators from the repository root:

```bash
python3 -B research/baseline/reference/output/filterflip_study_v1_retrieval/check_retrieval_counts.py
```

## What remained after filtering

For each of the same 59 questions and nine conditions, the native filter selected passages from the retrieved top five. The table counts questions where the full reference quote appeared in a single passage.

| Corpus condition | Before filtering | After filtering |
|---|---:|---:|
| Clean (C) | 40 | 20 |
| One prefixed background copy (BN1) | 39 | 33 |
| One prefixed answer-source copy (PN1) | 42 | 9 |

In PN1, 33 questions lost the literal quote during filtering. Another passage could still express the same fact. Establishing a failure in the final answer required a separate review of the surviving evidence and the generated answers.

See the [original filter summary](reference/output/filterflip_study_v1_filter/results/filter_run1/summary.json) for all nine conditions and the [archived validation record](reference/output/filterflip_study_v1_filter/VALIDATION.json) for the original checks. The [case-level indicators](reference/output/filterflip_study_v1_filter/filter_indicators.csv) preserve the before-and-after quote and source-presence flags. To match those inputs to the published retrieval records and recount the totals, run this from the repository root:

```bash
python3 -B research/baseline/reference/output/filterflip_study_v1_filter/check_filter_counts.py
```

## Answers with and without the filter

Each of the 531 retrieval contexts supplied two inputs to Qwen2.5:3b. The unfiltered input included all five retrieved passages. The filtered input included the passages that RAGDefender kept. This produced 1,062 answer conditions. The run recorded 706 distinct requests and reused their saved responses for the other 356 conditions when the request matched exactly.

For the Heather question with one answer-source copy (PN1), the recorded unfiltered answer was “Nicole Gale Anderson plays Heather Chandler in Beauty and the Beast.” The recorded filtered answer was “Not enough information.” Both requests completed successfully. Assessing what each answer established required reading it alongside the evidence.

The [answer request ledger](reference/output/filterflip_study_v1_answers/answer_request_ledger.csv) lists both modes for each case and condition. Rows with the same request hash refer to the same model request. The [original run summary](reference/output/filterflip_study_v1_answers/results/answers_run1/summary.json) and [execution audit](reference/output/filterflip_study_v1_answers/VALIDATION.json) record completion and reuse. Run the offline check from the repository root:

```bash
python3 -B research/baseline/reference/output/filterflip_study_v1_answers/check_answer_counts.py
```

## Primary outcome after review

Across the 59 selected questions, **8 met the strict endpoint, 51 fell outside it, and 0 remained unresolved**. The endpoint asks whether the clean filtered system could give a supported answer, whether that answer was still available before filtering in the answer-source-copy condition, and whether filtering then removed sufficient support and the answer failed. A lost quote or a completed model request alone cannot settle that judgment.

The initial assistant assessment recorded 4 events, 47 outside the endpoint, and 8 open cases. Shradha and Suresh jointly decided the 8 open cases using the agreed interpretation of core and mixed answers. Four met the endpoint and four fell outside it. The project recorded human confirmation for all 59 saved outcomes. The [case table](reference/output/filterflip_study_v1_outcome_review/primary_outcomes.csv) preserves the initial assessment and the basis of the accepted decision. For 10 rows the basis is an individual case review, for 8 it is joint adjudication, and for 41 it is the later confirmation of the existing assessment reported by Suresh. These counts apply to the selected baseline cases.

To check the case IDs against eligibility and recount the decisions against the published paired analysis:

```bash
python3 -B research/baseline/reference/output/filterflip_study_v1_outcome_review/check_primary_outcomes.py
```

## Did the finding depend on the setup?

Three follow-up checks used a preselected subset of 12 questions. Each asked a different question about the original result.

| What changed? | What the saved results showed |
|---|---|
| Passage order | Across the 36 contexts from those 12 questions, changing the order changed which passages survived in 7 contexts. Including the additional ordering checks on two selected cases, all 42 original-order comparisons reproduced the saved survivor sets. [Passage-order audit](reference/output/filterflip_study_v1_order_check/VALIDATION.json) |
| Filter encoder and text window | The original configuration reproduced all 36 saved decisions. In the Heather case, both MiniLM encoders removed the answer evidence in PN1, including when the input fit the text window. The three configurations accounted for 108 filter calls. [Configuration audit](reference/output/filterflip_study_v1_config_check/VALIDATION.json) |
| Answer model | On the same saved passages, both Qwen2.5:3b and Llama3.2:3b named Nicole Gale Anderson before PN1 filtering and abstained afterward. Across the subset, 66 distinct Llama requests covered 72 answer conditions. [Second-model audit](reference/output/filterflip_study_v1_second_generator/VALIDATION.json) |

The archived model comparison also records a counterexample. For the Three-Fifths Compromise question, a different retained passage still supported the answer, and both models answered correctly. The execution audits linked above document coverage and consistency. The Heather and Three-Fifths interpretations come from the original assistant-reviewed diagnostics. The 12 selected questions are a follow-up to the primary study and contribute no additional cases to its denominator of 59.

## Answer-generation code and offline tests

The [Qwen runner](reference/output/filterflip_study_v1_answers/run_answers.py) formats the question and passages, identifies identical requests, and records the response and its execution status. The [Llama runner](reference/output/filterflip_study_v1_second_generator/run_second.py) uses the same request-handling helpers for the second-model comparison. The original full runs depend on the semester handover's frozen request files, manifests, tokenizer assets and pinned local model service.

From the repository root, run the original unit tests with Python 3. They use small in-memory examples and require no model service:

```bash
base=research/baseline/reference/output
python3 -B "$base/filterflip_study_v1_answers/test_answers.py"
python3 -B "$base/filterflip_study_v1_second_generator/test_execution_checks.py"
```

### How the original answer runs were audited

The [Qwen audit](reference/output/filterflip_study_v1_answers/audit_answers.py) reconstructs requests from the saved passages and checks their identities, response reuse and token counts. The [Llama audit](reference/output/filterflip_study_v1_second_generator/audit_second.py) also compares each request with its Qwen counterpart to verify that the supplied messages and passage order were preserved.

Both scripts operate on the full semester handover, including its frozen inputs and raw response logs. Run them in a working copy of that handover using standard Python with assertions enabled. They write validation reports locally, and the Llama audit also writes a paired-answer table. For a checkout containing only the published evidence, use the [answer count checker](reference/output/filterflip_study_v1_answers/check_answer_counts.py).

### How answer runs were prepared and reviewed

The [Qwen preparation script](reference/output/filterflip_study_v1_answers/prepare.py) records the model configuration, checks token accounting with a local probe, and freezes the filtered and unfiltered requests. The [Llama preparation script](reference/output/filterflip_study_v1_second_generator/prepare.py) prepares the comparison on the selected 12 questions. These are the original setup scripts for the full semester handover and require its inputs and model service.

The [progress tracker](reference/output/filterflip_study_v1_answers/track_progress.py) counts completed requests from the saved Qwen logs. The [paired-answer review builder](reference/output/filterflip_study_v1_answers/build_review.py) puts the six primary and control answers side by side for each of the 59 questions. It produces the worksheet used before outcome scoring. The accepted decisions are in the [primary outcome table](reference/output/filterflip_study_v1_outcome_review/primary_outcomes.csv).

## Earlier pilot and preparation code

The [pilot answer scripts](reference/output/filterflip_poc/) pair answers using previously saved pilot contexts. The [embedding setup](reference/legacy/embedding_check/) identifies the pinned public checkpoint, and the [token audit](reference/legacy/confirmation12/token_audit.py) records how much of each passage fits within the selected model window. The [early grouping policy](reference/legacy/mitigation1/policy.py) is the implementation used during development. The [Qwen protocol](reference/output/filterflip_study_v1_answers/PROTOCOL.md) and [Llama protocol](reference/output/filterflip_study_v1_second_generator/PROTOCOL.md) document the original generation settings.

The [preparation README](reference/output/filterflip_study_v1/README.md) is the September handover record. Its pending-review counts describe that point in the study. Its full-package instructions and integrity checker use the original handover files. See the primary outcome section above for the semester result.
