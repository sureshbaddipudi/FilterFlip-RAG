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
