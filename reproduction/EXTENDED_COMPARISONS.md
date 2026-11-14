# Reproduction and extended comparisons

- [Answer reproduction](../research/answer-reproduction/) contains the semester recovery code and its tests for interrupted runs. The worker and pipeline tests use mock processes. Replaying the full recovery requires the archived request queues, manifests and predecessor records.
- [Copy-variant analysis](components/copy-variant-comparisons/expected/REPORT.md) covers one and two background or answer-source copies, including exact-copy conditions. The [condition tables](components/copy-variant-comparisons/expected/CONDITION_TABLES.json) supply the data for the included plotting script. The original case notes reference detailed records in the full handover.
- [TrustRAG comparison design](../research/trustrag-design/COMPARABILITY.md) and [implementation](../research/trustrag-stage1/) document how the study supplied the saved stage-1 selections to Qwen. The design files describe the proposal at the time it was written. The completed run covered 12 questions and 36 contexts, with 60 distinct fresh responses serving 72 answer positions. Later TrustRAG stages are outside this comparison.
- [Paired results](components/paired-results-analysis/RESULTS.md) and [limitations](components/paired-results-analysis/LIMITATIONS_AND_QUALITY.md) explain the review decisions and denominators. The full-packet validators and end-to-end analysis tests require the sealed handover inputs and their original layout.

From the repository root, run the self-contained recovery checks with Python 3:

```bash
python3 -B research/answer-reproduction/test_pipeline.py
python3 -B research/answer-reproduction/test_worker.py
```

To reproduce the copy-variant figure with Matplotlib installed, choose a fresh output directory:

```bash
component=reproduction/components/copy-variant-comparisons
python3 -B "$component/code/plot_analysis.py" --analysis "$component/expected" --out figures-copy-variants
```
