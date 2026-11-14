# FilterFlip Week-06 filter-analysis tools v1

**Role: offline software development increment, 7 October 2026. This is not a Week-6 results handover.**

This separate tool checks future outputs from `FilterFlip_Week06_Implementation_Review_v1` and reports the filter-retention part of the planned mitigation comparison. It does not import that runner, load a model, contact a service, change evidence, or run an experiment. The runner release and its challenge-review packet remain unchanged.

The real readiness check included here found 295 saved contexts and ten draft challenge trios. Their files, the selected original sources, runner code and protocol match the preparation checksums. Independent challenge review remains pending. No teammate findings have been received. The original assessment remains **4 assistant-confirmed events, 47 comparisons outside the strict endpoint, and 8 unresolved cases**; this tool does not recalculate that endpoint.

## Contents

- `analyze.py`, `audit.py`: standalone standard-library CLI and read-only validators.
- `tests/test_analysis.py`: synthetic software fixtures, including a complete synthetic 295-context journal. They are not research observations or human reviews; all fixture review identities are explicitly synthetic and exist only in temporary directories.
- `validation/`: developer test logs and a read-only readiness check of the real preparation.
- `SECURITY.md`, `VALIDATION.md`: controls, evidence, and limitations.
- `RELEASE_SHA256.json`: file checksums for this release, excluding that manifest itself.

## Reproduce the software checks

Use Python 3.10 or newer; the recorded validation used Python 3.12. No third-party packages or network access are needed. Run from this package directory:

```bash
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
```

To reproduce the real read-only check, point these variables to your existing copies. Do not extract the original package again if it is already available. The output path must not already exist and must be outside all input and tool directories.

```bash
FF_RELEASES='/path/to/outputs'
FF_ORIGINAL='/path/to/FilterFlip_Reproduction_Package'
FF_RUNNER="$FF_RELEASES/FilterFlip_Week06_Implementation_Review_v1"

python analyze.py readiness \
  --prepared "$FF_RUNNER/prepared" \
  --runner "$FF_RUNNER" \
  --package "$FF_ORIGINAL" \
  --protocol "$FF_RELEASES/FilterFlip_Week6_Planning_v1/EVALUATION_PROTOCOL.md" \
  --review "$FF_RUNNER/prepared/review_TEMPLATE.json" \
  --out "$FF_RELEASES/teammate_readiness_01"
```

Expected now: preparation checks pass; review is `pending_or_invalid`; zero models loaded and zero research calls. A pending review is a valid readiness finding, so readiness mode exits successfully. A broken source checksum stops the command with exit code 2. The output folder contains `readiness.json` and its short explanation. Readiness does not inspect past experiment directories or prove backend readiness.

## Analyze a future stopped filter run

Use this only after independently reviewed challenge decisions exist and the separately authorized bounded runner has produced a stopped run. The analysis command itself never starts that runner. Supply the exact resolved review used by that run. All ten trios must be approved or excluded with the required attribution and rationale; do not fill these fields on someone else's behalf.

```bash
python analyze.py filter \
  --prepared "$FF_RUNNER/prepared" \
  --runner "$FF_RUNNER" \
  --package "$FF_ORIGINAL" \
  --protocol "$FF_RELEASES/FilterFlip_Week6_Planning_v1/EVALUATION_PROTOCOL.md" \
  --review '/path/to/returned_challenge_review.json' \
  --filter-run '/path/to/stopped_filter_run' \
  --out "$FF_RELEASES/filter_analysis_01"
```

Keep the source run stopped while reading it. An existing `RUN.lock` stops the audit; do not delete a lock blindly. A truncated or broken hash chain also stops it. Preserve the original files for investigation. An intact journal with faults or an unfinished session can be reported as partial evidence once it is no longer active. Nothing is resumed or retried.

The output contains:

1. `REPORT.md`: per-dataset, per-track, per-condition retention counts and paired gains/losses for E versus N, CN versus N, and CN versus O.
2. `analysis.json`: exact identities, missing context keys, denominators, physical attempts, faults, uncertain attempts, recorded time, and budget flags.
3. `support_review_TEMPLATE.json`: blank semantic-support fields for each completed context/policy, bound to the evidence. Save reviewer work in a separate copy.
4. `support_review_packet.txt`: original question/passages and retained indices for each arm, as plain text. Passage text is untrusted evidence, never an instruction to execute.

U means all passages; N native filtering; E exact duplicate collapse then native; CN the fixed 0.95 near-duplicate collapse then native; O sorted native without collapse, an ordering diagnostic. The checker independently repeats grouping arithmetic from recorded numeric scores and checks matching earlier native calls. It never recomputes embeddings.

## What the numbers mean

A designated passage being retained is only an automatic screen. It does not prove that the remaining passages support the answer. Retaining a harmful passage does not prove the generator followed it. Those judgments require separate semantic and answer review.

Missing contexts stay missing; they are not zero-success cases. Forced six-passage challenges are separated from the saved five-passage panel. Faults and uncertain calls remain visible. Physical calls are counted from attempt records, so cache reuse is not charged twice. Closed-session time is a lower bound when a session is unfinished; timing excludes separately unrecorded grouping overhead. No production latency claim is supported.

The hash chain and checksums detect inconsistency relative to supplied trusted files. They are not signatures and do not authenticate a reviewer. The support-review template is intentionally unfilled and has no importer in this version. Generator-answer joining, outcome-review import, adjudication, statistical interpretation and final novelty positioning remain later work. This package adds no attack rate and no human-verified finding.

## Teammate return

Return the release checksum, Python version, test output, readiness output and any discrepancies. Continue the earlier Week-4 review and Week-6 challenge-review handovers separately. A pass here verifies software behavior; it does not accept the Week-6 scientific milestone.
