# Standalone saved-data reproduction

Use the pristine packet as input and a **new separate return folder** for all writes. The steps below need no original absolute paths, original-package extraction, model weights, encoder or Ollama. No script installs tools or downloads packages. Do not run old generation queues from the historical component READMEs.

## Existing tools

Python 3.11+ is recommended. Standard-library integrity, descriptive analyses, report-table generation and synthetic application checks work without model packages. The corrected numerical comparator additionally needs an existing Python with NumPy; the pinned baseline used NumPy 2.4.6. JavaScript syntax and the 59-case synthetic DOM check need an existing Node executable. Node may be outside the pinned Python environment. Do not install or upgrade tools in that environment for this return. Missing tools are NOT RUN with reasons, not failed scientific outcomes or invented passes.

## 1. Verify and prepare a return

From the handover root:

```bash
python3 -B tools/verify_handover.py
python3 -B tools/prepare_return.py --out /ABSOLUTE/NEW_Task13_Return \
  --received-zip /ABSOLUTE/THIS_Task13_v1_1_DELIVERY.zip
python3 -B tools/verify_handover.py --stage before > /ABSOLUTE/NEW_Task13_Return/pristine_before.json
```

Replace the absolute path with a new folder outside the handover. The preparer verifies integrity, copies blank forms and binds them to this packet’s manifest. With --received-zip it computes the received archive checksum without extracting or changing it. It also saves a phase-tagged before-integrity report. A received checksum is mandatory for a complete return; without that option, fill the exact checksum yourself. It fills no reviewer, date, assistance field or semantic decision. If a destination already exists, retain it and choose a new name; do not delete failed evidence to make a check pass.

## 2. Reproduce and test offline

```bash
python3 -B tools/reproduce_offline.py \
  --out /ABSOLUTE/NEW_Task13_Return/offline \
  --numpy-python /ABSOLUTE/PATH/TO/EXISTING_PYTHON_WITH_NUMPY \
  --node /ABSOLUTE/PATH/TO/EXISTING_NODE
```

Omit either optional executable argument only if the appropriate existing tool is already available to the selected interpreter/PATH. The output directory must be new. All temporary files and caches stay under it. The fixed driver invokes only reviewed offline analyses/validators, numerical saved-profile comparison and synthetic tests; it never calls a historical model runner, pip installer or asset downloader.

It checks unchanged component integrity; runs the 42 application tests normally and with `-O`; runs the handover/F2 return-completeness and five read-only-wrapper controls in each mode; runs Task-2 and Task-8 analysis tests in both modes; checks JS syntax and all 59 recorded-case renderings; reproduces the 11 Week-6 analysis outputs, Task-2 structural outputs and Task-8 reviewed aggregations; replays the corrected comparator’s 35 saved-data gates and 31 regression tests in both modes; recreates the 16 report data/LaTeX-table files; and audits all 20 saved rehearsal response/request bindings. It then verifies that the pristine packet is unchanged.

The v1.1 driver writes a schema-version-2 ledger, phase-tagged before/after integrity files, hashes for every executed-check log (including comparison logs), and generated-output bindings. It records all planned steps, including skipped comparisons after upstream failures and the documented missing-NumPy branch. There are 36 steps with NumPy available or 31 in the missing-NumPy branch.

Read `offline/EXECUTION.json` and its hash-bound logs. Exit 0 means all selected checks passed; exit 2 means a tool/check was NOT RUN and the limitation is recorded; exit 1 means at least one failed check. Matching outputs establish computational reproducibility, not independent scientific correctness. If something differs, retain the actual files/logs and record the discrepancy. The driver makes no automatic retry.

PDF recompilation is not part of the default check. The existing PDF is integrity-checked and remains pending Suresh’s review. If an existing LaTeX installation is available and a separate build is wanted, components/report/README.md gives the no-install builder with new output destinations. No presentation build is included.

## 3. Inspect the actual current GUI with models blocked

```bash
python3 -B tools/serve_readonly_gui.py \
  --work /ABSOLUTE/NEW_Task13_Return/readonly_gui \
  --port 8769
```

Open **http://127.0.0.1:8769**. This uses the unchanged v2.5 application code/data with a separate process wrapper. Its banner/badge explicitly say read-only/models disabled, and the server rejects generation/cancellation before any worker starts. It needs no existing original assets. It does not replay a saved answer as a new live response.

Inspect Findings and Evidence, then recorded Heather, targeted-victory and UCC cases as listed in the checklist. You may click Run once **in this model-disabled wrapper** to verify the explicit rejection. No answer is generated. Do not substitute the ordinary production launcher during these checks. Stop the helper with Ctrl+C; it also stops automatically after 30 minutes. If port 8769 is occupied, choose another free nonprivileged port; do not stop someone else’s service.

## 4. Review the saved new answers

Open review/TASK12_REVIEW_PACKET.md, then edit only `/ABSOLUTE/NEW_Task13_Return/TASK12_ANSWER_REVIEW.json`. The packet supplies all exact answer strings, supplied passages, policy survivor numbers, request hashes and raw response links for all 20 answers. Fill your actual name/date/assistance and the blank judgments. Preserve uncertainty with reasons; do not guess from string equality, a passage-ID removal or the old v2.4 decision. Review states and allowed values are listed in CHECKLIST_FOR_SHRADHA.md.

## 5. Verify preservation and return

```bash
python3 -B tools/verify_handover.py --stage after > /ABSOLUTE/NEW_Task13_Return/pristine_after.json
python3 -B tools/validate_review_return.py --return-dir /ABSOLUTE/NEW_Task13_Return
python3 -B tools/seal_return.py \
  --return-dir /ABSOLUTE/NEW_Task13_Return \
  --zip /ABSOLUTE/FilterFlip_Task13_Return_Shradha.zip
```

The validator returns 2 for pending fields, 1 for invalid identities/evidence/structure, and 0 for a structurally complete report. Such a report may have verification_result FAIL or PASS_WITH_NOT_RUN; COMPLETE_RETURN is not a successful-verification label. PASS checklist entries require real evidence references. The two integrity reports must carry the expected packet hash, inventory and distinct before/after stages. Offline evidence must cover the exact unique planned checks, declared log hashes and required generated files. It does not certify correctness or accept the handover for Suresh. At intake, compare the reported received_zip_sha256 against Suresh’s trusted delivery sidecar, for example with `--trusted-zip-sha256 ACTUAL_64_HEX_DELIVERY_DIGEST`; `--received-zip /ABSOLUTE/RECEIVED.zip` can additionally compare an explicitly supplied archive. These options also work on the seal helper. Without them, a syntactically valid checksum is only a declared receipt value. The packet’s own manifest does not independently authenticate its outer ZIP. Fill VERIFICATION_RETURN.json and DISCREPANCIES.json first. If blocked and intentionally returning incomplete evidence, use `--allow-incomplete` with the seal helper and explain the blocker; do not relabel pending checks PASS. Sealing creates a return manifest, ZIP and checksum outside the pristine source. Do not edit them afterward; add later comments separately.

## A later fresh model run

None is needed or authorized by the default verification. The v2.5 backend/policies/data are byte-identical to accepted v2.4; Task 12 already ran the five fresh jobs locally. This handover preserves that proof, while leaving new semantic interpretation open. The browser download action remains not retested by this model-free route. If Suresh later requests a fresh teammate-machine smoke check, record its exact job/attempt/time cap before execution, use existing verified assets in a new private run folder and stop on faults without retries. Do not reset completed Task-1/3/12 ledgers.
