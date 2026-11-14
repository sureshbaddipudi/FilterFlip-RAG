"""Check answer coverage and exact-request reuse against the saved baseline counts."""
import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    filters = ROOT.parent / "filterflip_study_v1_filter/filter_indicators.csv"
    with filters.open(newline="") as stream:
        expected = {
            (row["case_id"], row["condition"], mode)
            for row in csv.DictReader(stream)
            for mode in ("filtered", "unfiltered")
        }

    seen = set()
    executions = Counter()
    requests = set()
    with (ROOT / "answer_request_ledger.csv").open(newline="") as stream:
        for row in csv.DictReader(stream):
            key = (row["case_id"], row["condition"], row["mode"])
            digest = row["request_sha256"]
            if key in seen or key not in expected:
                raise ValueError(f"Unexpected or repeated answer condition: {key}")
            if not re.fullmatch("[a-f0-9]{64}", digest) or row["status"] != "ok":
                raise ValueError(f"Invalid request identity or completion status: {key}")
            if row["response_reused"] not in {"0", "1"}:
                raise ValueError(f"Invalid reuse flag: {key}")
            seen.add(key)
            requests.add(digest)
            if row["response_reused"] == "0":
                executions[digest] += 1

    if seen != expected or any(executions[digest] != 1 for digest in requests):
        raise ValueError("Incomplete mode coverage or inconsistent request reuse")
    audit = json.loads((ROOT / "VALIDATION.json").read_text())
    summary = json.loads((ROOT / "results/answers_run1/summary.json").read_text())
    reused = len(seen) - len(requests)
    if (len(seen), len(requests), reused) != (
        audit["logical_conditions"], audit["distinct_requests"], audit["reused_logical_conditions"]
    ):
        raise ValueError("Totals differ from the archived audit")
    if summary["logical_status_counts"] != {"ok": len(seen)} or summary["unique_status_counts"] != {"ok": len(requests)}:
        raise ValueError("Completion counts differ from the original run summary")
    print(f"Verified {len(seen):,} answer conditions, {len(requests)} distinct requests and {reused} reused responses.")


if __name__ == "__main__":
    main()
