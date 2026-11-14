"""Check the published retrieval indicators against the eligible cases and saved totals."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = (
    "original_source_retrieved",
    "original_or_source_copy_retrieved",
    "quote_in_single_chunk",
    "contexts_with_additions",
)


def main():
    eligibility = ROOT.parent / "filterflip_study_v1/screened/source_eligibility.csv"
    with eligibility.open(newline="") as stream:
        cases = {row["case_id"] for row in csv.DictReader(stream) if row["source_decision"] == "eligible"}
    summary = json.loads((ROOT / "results/retrieval_run1/summary.json").read_text())
    conditions = summary["conditions"]
    expected = {(case, condition) for case in cases for condition in conditions}
    seen = set()
    totals = {condition: dict.fromkeys(FIELDS, 0) for condition in conditions}
    with (ROOT / "retrieval_indicators.csv").open(newline="") as stream:
        for row in csv.DictReader(stream):
            key = (row["case_id"], row["condition"])
            if key not in expected or key in seen:
                raise ValueError(f"Unexpected or repeated case and condition: {key}")
            seen.add(key)
            for field in FIELDS:
                if row[field] not in {"0", "1"}:
                    raise ValueError(f"Invalid indicator for {key}: {field}")
                totals[row["condition"]][field] += int(row[field])
    if seen != expected or len(seen) != summary["completed_contexts"] or len(cases) != summary["planned_questions"]:
        raise ValueError("Case coverage differs from the saved study")
    for condition, counts in totals.items():
        if conditions[condition]["completed"] != len(cases) or any(counts[f] != conditions[condition][f] for f in FIELDS):
            raise ValueError(f"Totals differ from the saved study for {condition}")
    print(f"Verified {len(cases)} questions across {len(conditions)} conditions ({len(seen)} retrieval records).")


if __name__ == "__main__":
    main()
