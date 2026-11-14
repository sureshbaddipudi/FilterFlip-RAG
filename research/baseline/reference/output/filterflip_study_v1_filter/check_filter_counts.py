"""Recount the saved filtering indicators and match each input to its retrieval record."""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = ("quote_before", "quote_after", "source_copy_before", "source_copy_after")


def indexed_rows(path):
    with path.open(newline="") as stream:
        records = {}
        for row in csv.DictReader(stream):
            key = row["case_id"], row["condition"]
            if key in records:
                raise ValueError(f"Duplicate record in {path.name}: {key}")
            records[key] = row
    return records


def main():
    retrieval = indexed_rows(ROOT.parent / "filterflip_study_v1_retrieval/retrieval_indicators.csv")
    filtering = indexed_rows(ROOT / "filter_indicators.csv")
    summary = json.loads((ROOT / "results/filter_run1/summary.json").read_text())
    if filtering.keys() != retrieval.keys() or len(filtering) != summary["completed"]:
        raise ValueError("Filtering and retrieval coverage differ")

    totals = defaultdict(Counter)
    for key, row in filtering.items():
        upstream = retrieval[key]
        if row["quote_before"] != upstream["quote_in_single_chunk"] or row["source_copy_before"] != upstream["original_or_source_copy_retrieved"]:
            raise ValueError(f"Filter input differs from retrieval for {key}")
        if any(row[field] not in {"0", "1"} for field in FIELDS):
            raise ValueError(f"Invalid binary indicator for {key}")
        flags = {field: int(row[field]) for field in FIELDS}
        if flags["quote_after"] > flags["quote_before"] or flags["source_copy_after"] > flags["source_copy_before"]:
            raise ValueError(f"Filtering introduced evidence for {key}")
        counts = totals[key[1]]
        counts.update(flags)
        counts["completed"] += 1
        counts["quote_removed"] += flags["quote_before"] - flags["quote_after"]

    if totals.keys() != summary["conditions"].keys():
        raise ValueError("Condition inventory differs from the archived summary")
    for condition, counts in totals.items():
        if any(summary["conditions"][condition][field] != value for field, value in counts.items()):
            raise ValueError(f"Totals differ for {condition}")
    print(f"Verified {len(filtering)} filter records against retrieval inputs and archived totals.")


if __name__ == "__main__":
    main()
