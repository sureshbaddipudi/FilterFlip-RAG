# Week 6 evaluation

The team compared the original filter with exact-copy and near-copy handling. On the 18-question benign panel, near-copy handling gained seven accepted core answers against the native filter and lost eight. One comparison was unresolved. On the nine false-claim challenges, two cases newly accepted a false claim and one avoided it.

- [Policies](policies/policies.py) implements the grouping rules. [Generation logging](generation-logging/generation_worker.py) preserves received responses for later review.
- [Audit tools](audit/) check saved filter records and run accounting. The audit package README also describes the original semester handover layout.
- [Analysis and result tables](../../reproduction/components/week06_analysis/) contains the offline analysis program and selected original outputs. Start with the [dataset tables](../../reproduction/components/week06_analysis/expected/DATASET_TABLES.md). The analysis of all 173 distinct answers and 324 conditions uses the sealed Week 6 handover inputs. R110 retains its uncertain judgment.

From the repository root, these two suites exercise the published code with temporary test data:

```bash
python3 -B -m unittest discover -s research/week06/audit/tests
python3 -B research/week06/generation-logging/tests/test_response_capture.py
```
