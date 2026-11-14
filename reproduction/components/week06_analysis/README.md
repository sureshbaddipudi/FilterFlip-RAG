# FilterFlip-RAG — Week-6 analysis for Shradha's Part B review

Version 1 · 27 October 2026 · **Analysis delivered for verification; Week 6 not yet accepted.**

Part A is complete: Shradha checked the scoring transfer, and Suresh agreed. This package supplies the actual report and reproducible calculations required for Part B. It includes the saved inputs; you do not need another Week-6 ZIP, Ollama, a GPU, model weights or internet access.

## What to read

1. `expected/REPORT.md` — findings, definitions, costs and limitations.
2. `expected/REVIEW_TRACE.md` — every benign CN-versus-N core-answer gain/loss, with answers, evidence and request hashes.
3. `expected/DATASET_TABLES.md` — dataset/condition tables in readable form.
4. `PART_B_RETURN_TEMPLATE.md` — exactly what to return.

The JSON files alongside the report provide the complete calculation outputs. `inputs/scoring/DERIVED_REVIEW_LEDGER.json` contains all 173 answers, their actual requests, current reviews and preserved earlier judgments. `inputs/scoring/LOGICAL_SCORING_MAP.json` maps these to all 324 conditions. The source documents, full filter results, execution journals and raw generation responses are included.

## What this package does

`analyze.py` uses only Python's standard library and reads the saved evidence. It checks hashes, journal chains, completed calls, raw response bytes, frozen context texts, exact filter-to-generator requests, human-review joins and scoring transfer before calculating tables. It does not import the model runner, call a model, start a server or execute text found in passages. All new output goes to a new folder outside the released package.

The evidence text includes intentionally false claims and a harmless injected marker directive. Treat it as research data, not instructions. `reference/EVALUATION_PROTOCOL.md` and `inputs/plan.json` are frozen historical documents; their original pending-status wording is retained. They do not describe the current completion state. Current status is in this README and `PART_A_INTAKE.md`.

## Offline reproduction: exact steps

Use **Python 3.10 or newer**. No package installation is needed. Open a terminal in the extracted `FilterFlip_Week06_Analysis_For_Review_2026-10-27` folder. Keep the supplied files unchanged. Run each command below and stop if it reports an error. If you need another attempt, choose a new return-folder name; do not delete evidence of a failed attempt.

Create a sibling return folder:

```bash
mkdir ../FilterFlip_Week06_PartB_Return_Shradha
```

Record Python's version, verify the released files, and save the logs:

```bash
python3 --version > ../FilterFlip_Week06_PartB_Return_Shradha/python_version.txt
python3 -B analyze.py --verify > ../FilterFlip_Week06_PartB_Return_Shradha/integrity.log 2>&1
```

Run the focused analysis tests normally and with optimized Python. These tests concern the new calculation code; they do not repeat earlier model experiments or the earlier runner/UI test suites.

```bash
python3 -B -m unittest -v test_analysis > ../FilterFlip_Week06_PartB_Return_Shradha/tests.log 2>&1
python3 -O -B -m unittest -v test_analysis > ../FilterFlip_Week06_PartB_Return_Shradha/tests_optimized.log 2>&1
```

Recalculate everything, compare with the supplied results, and write your own copy:

```bash
python3 -B analyze.py --check --out ../FilterFlip_Week06_PartB_Return_Shradha/reproduced > ../FilterFlip_Week06_PartB_Return_Shradha/reproduction.log 2>&1
```

Expected success: integrity reports `PASS`; both test logs finish with `OK`; reproduction reports that **11 outputs match byte-for-byte**, and reports **zero research/model calls**. The recreated report and tables are in `reproduced/`. Read the logs; file creation alone is not proof of success. A failure or mismatch should be reported with the log unchanged.

Copy the return form into your return folder and fill it there:

```bash
cp PART_B_RETURN_TEMPLATE.md ../FilterFlip_Week06_PartB_Return_Shradha/PART_B_RETURN.md
```

Check the findings as described in the form. Byte-for-byte agreement confirms reproducibility of this implementation; it does not replace checking that the calculation and interpretation are appropriate.

## Focused human checks

- Confirm 173 distinct answers and 324 conditions, including the five R110 links. The 173 answers are not 324 independent model samples.
- Use the trace to inspect at least one CN gain and one CN loss, a clean C failure, and the retained uncertainty. Give the exact case/condition/review IDs you inspected. You need not repeat all 173 semantic reviews.
- Inspect Heather and Woody Woodpecker as newly accepted false claims under CN, and Belle as the avoided false claim. These are two new harms and one avoided harm compared with N. The report includes their neutral answers; challenge judgments remain Shradha's original judgments.
- Confirm all nine approved challenge trios remain primary; the six-unflagged subset remains secondary. PHP, Heather and UCC limitations stay attached. Bald eagle remains excluded from challenges, not from benign results.
- Confirm the accepted-core measure is not described as fully correct/fully supported answering. Check R033/R056 extra errors, missing required core in R005/R048/R134, and R043's unsupported wording despite the supplied extra-claim flag `no`.
- Confirm costs count 67 unique fresh executions, not 117 repeated logical links. The 106 saved answers' historical costs are separate. Filter timing uses 12 contexts from four cases, with no general speed claim.
- Confirm the conclusions retain losses, clean failures, post-outcome scoring clarification, selected-panel limits, original assistance/blinding disclosures and the absence of a secure-improvement claim.

## Return

Send Suresh one ZIP containing the filled `PART_B_RETURN.md`, four logs, Python version record and the `reproduced/` folder. Use a name such as `FilterFlip_Week06_Final_Analysis_Verification_Shradha_YYYY-MM-DD.zip`, with the actual review date and a SHA-256 sidecar. Preserve your original Part A return unchanged. This package does not ask you to repeat Part A or confirm the 23 scoring decisions again.

After Suresh receives Part B, any confirmed issues are fixed and the affected outputs are rechecked. Both participants then record the Week-6 milestone decision, including whether the documented R110 uncertainty is acceptable. Do not fill Suresh's decision on his behalf. Publication extensions remain separate work after this bounded analysis is settled.

## Integrity and provenance

`INPUT_MANIFEST.json` binds copied inputs; `SHA256_MANIFEST.json` binds all delivered files except itself. The ZIP has a separate checksum. `SOURCE_INDEX.json` records original local paths for provenance only; calculations use package-relative paths and never require those original locations. The manifest detects changes against this release; it is not a digital signature or proof that semantic judgments are correct. Source reviews, original results and earlier released ZIPs have not been rewritten.

`SECURITY_NOTES.md` maps the new offline tool's controls to STRIDE and the relevant project security concerns. No web/API service is introduced, and no blanket OWASP compliance claim is made.
