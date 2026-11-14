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
