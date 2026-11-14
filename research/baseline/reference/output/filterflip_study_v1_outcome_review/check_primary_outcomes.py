"""Check case coverage and recount published baseline decisions without rescoring."""
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    with (HERE.parent / "filterflip_study_v1/screened/source_eligibility.csv").open(newline="") as stream:
        eligible = {r["case_id"] for r in csv.DictReader(stream) if r["source_decision"] == "eligible"}
    with (HERE / "primary_outcomes.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != len(eligible) or {r["case_id"] for r in rows} != eligible:
        raise ValueError("Outcome rows do not match the eligible question set")

    initial = Counter(r["initial_assistant_assessment"] for r in rows)
    if initial != {"Assistant-confirmed event": 4, "Not a strict event": 47, "Needs adjudication": 8}:
        raise ValueError("Historical baseline counts differ")
    joint = [r for r in rows if r["review_basis"] == "prior_joint_adjudication"]
    if {r["case_id"] for r in joint} != {r["case_id"] for r in rows if r["initial_assistant_assessment"] == "Needs adjudication"}:
        raise ValueError("Joint decisions do not cover the eight formerly open cases")
    if Counter(r["accepted_endpoint"] for r in joint) != {"met": 4, "not_met": 4}:
        raise ValueError("Joint decision totals differ")
    summary = HERE.parents[4] / "reproduction/components/paired-results-analysis/expected/PRIMARY_SUMMARY.json"
    accepted = Counter(r["accepted_endpoint"] for r in rows)
    if dict(accepted) != json.loads(summary.read_text())["accepted_original"]:
        raise ValueError("Accepted counts differ from the published paired analysis")
    print(f"Verified {len(rows)} primary cases: {accepted['met']} met the endpoint, {accepted['not_met']} did not, 0 unresolved.")


if __name__ == "__main__":
    main()
