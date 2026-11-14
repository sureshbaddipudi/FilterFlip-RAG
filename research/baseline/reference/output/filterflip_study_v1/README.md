# FilterFlip study v1 — start here

Prepared 24–25 September 2026. This package starts the new study after choosing FilterFlip. It is **data preparation, not another attack-result report**.

## What has already been done

- Downloaded pinned public NanoNQ and NanoMSMARCO releases: 5,035 and 5,043 documents, respectively, with 50 candidate questions each.
- Converted their native Parquet files to JSONL without changing the texts. The included converted files need no extra library to read.
- Screened against a conservative catalog of 200 prior questions and 229 prior source/chunk texts. One NQ question overlaps; **99 remain pending answer-support review**.
- Prepared a saved protocol, source-review page, annotation checks and source hashes.
- Confirmed that the existing RAGDefender version and tracked checkout remain unchanged; both earlier MiniLM snapshots exist locally.
- Inspected the independent TrustRAG component's integration requirements. It has not been run.

No embeddings, filtering or LLM answers have been generated on the new candidates. There are no new attack success rates. All prior pilot data remains development data.

## What to do now — no installation or terminal required

1. Open `screened/REVIEW.html` in your browser. It works locally without a server or network.
2. Start with the first question. Read the question and its displayed reference passage(s).
3. Enter your name. If a source clearly answers the question, choose **One source supports a clear answer**.
4. Copy the document ID from its heading. Enter the short expected answer and copy the exact sentence(s) supporting it. Add historical or other qualifications where necessary.
5. If the references do not provide a clear single-source answer, choose **Unsuitable or insufficient source support** and state why. Never invent an answer to keep a case.
6. Click Next. Work in batches of about ten rather than trying to finish everything at once.
7. Click **Download labels** regularly. Save the JSON file. To continue later, open the same page and import that file. Refreshing without downloading loses unsaved edits.

Keep separate reviewer files if both teammates work independently. Do not overwrite each other's labels. The page contains no filter results, so reviewers can make source-based decisions without seeing attack outcomes. The same file with unfinished rows is a valid partial review.

### Worked example: the first review row

For `NanoNQ:test1009`, the question is “who plays heather in beauty and the beast”. The displayed reference identifies **Nicole Gale Anderson** as playing Heather Chandler in the CW series. An appropriate answer is `Nicole Gale Anderson`, with the qualification `The question is interpreted as the CW television series, as stated in this reference.` Copy the actual source sentence(s) from the page and the displayed document ID; do not guess the ID. This is an assistant-provided example, not a completed independent human review.

## Optional label-file check

Run from wherever you extract this folder:

```bash
conda activate filterflip-core
python check_labels.py /absolute/path/to/support_labels.json
```

This checks IDs, required fields and whether the quoted text occurs in the selected source. It does **not** determine semantic correctness. `--require-complete` additionally fails while any row remains pending.

The all-pending template is expected to pass structural checking and fail completeness checking. No command in this package treats it as validated research data.

## Files

- `PROTOCOL.md`: primary question, conditions, metrics, exclusions and scope amendment.
- `screened/REVIEW.html`: simple source-review interface.
- `screened/SOURCE_REVIEW.md`: the same sources as a readable document, including excluded candidates.
- `screened/candidates.json`: all 100 candidates, overlap reasons and relevance-linked sources.
- `screened/support_labels_TEMPLATE.json`: all 99 pending annotation rows.
- `screened/screening_summary.json`: counts and limitations.
- `screened/prior_exclusion_catalog.json`: conservative prior-source catalog and input hashes.
- `sources/`: pinned dataset cards, native Parquet and converted JSONL; data source URLs and hashes are in `acquisition.json`.
- `environment_audit.json`: existing package versions and cached model availability.
- `COMPARATOR_AUDIT.md`: independent-filter integration findings.
- `verify_package.py`, `test_preparation.py`: integrity and annotation-validation checks.
- `FROZEN_MANIFEST.json`: hashes of the shipped preparation record; this does not yet freeze completed answer labels or an executable experiment runner.

Only if rebuilding the downloads from scratch: `prepare_sources.py` needs PyArrow and network access; it refuses an existing output directory. The prepared package already contains everything needed for source review. `build_study.py` needs the original local project to reconstruct the prior-exposure catalog, and refuses an existing screening output directory.

## Limits to remember

NanoBEIR is a compact public sample, not the full benchmark. The two corpora are separate, about 5,000 documents each. Relevance labels are not answer-support labels. Lexical overlap screening cannot guarantee semantic/article independence or absence from model training. The final eligible count can be lower than 99 after review, and later clean failures/retrieval misses must not be dropped from the experiment record.

The next stage is to seal source labels and prepare retrieval-only evaluation. There is no need to repeat the old DocGuard or FilterFlip pilots.
