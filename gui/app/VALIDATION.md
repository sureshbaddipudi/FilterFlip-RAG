# v2.6 current validation

See ../VALIDATION_REPORT.md and ../validation/ for the new 49-test checks per Python mode, all-condition rendering/controls, browser checks and preservation proofs. Original validation below and under validation/ is retained historical evidence, not newly executed v2.6 live-model acceptance. No research inference was run to prepare this GUI.

## Historical validation

# v2.3 display validation — 29 October 2026

- JavaScript syntax: passed.
- `node validation/check_recorded_view.cjs`: passed for all 59 cases. Checks all saved answers/passages, joint-decision precedence, explicit missing checklists/dates, UCC applicability and literal-text insertion. This lightweight DOM test is not a browser layout test.
- Browser: Heather rendered all five sections, six saved answers and expandable PN1 copy with full passage/trace fields. Screenshot evidence is in validation/. Changing the question hides the previous record. The temporary preview server ended before the additional joint-case browser inspection; joint-case content is covered by the offline check, not claimed as newly browser-verified.
- All Python files, data/, evidence/, review_acceptance/ and native_profile.json retain v2.2 bytes; see validation/UNCHANGED_RESEARCH_FILES.json.
- New ZIP clean-extraction manifest verification: passed. See FilterFlip_Review_Demo_v2_3_Packaging_Validation.json beside the ZIP (outside the ZIP to avoid self-reference).
- No model loads, inference, research reruns or changes to the user's Desktop folder. The existing 42 backend tests were not rerun for this frontend-only update; the earlier run below remains historical.

## Prior v2.1 validation record

# v2.1 validation scope

This is a display/review-metadata revision of v2. No model calls or new scientific experiments are made for v2.1. Backend.py, policies.py, common.py and native_profile.json retain v2 hashes.

Developer checks: existing 42 offline tests normally and with optimized Python; JavaScript syntax; unchanged evidence audit (322 saved contexts / 1,288 mappings); browser inspection of C/BN1/PN1 labels, current recorded-case dates and joint acceptance text. Clean-ZIP extraction and manifest verification are recorded separately in the packaging validation folder.

Baseline v2 development evidence is preserved under evidence/ and BASELINE_V2_VALIDATION.md, including two interrupted challenge attempts. Those historical attempts are not rewritten. The separate reviewed teammate return under review_acceptance/original_return has three completed runs (12 answers) and one cancelled attempt (no saved answer). Its jointly agreed interpretation is review_acceptance/JOINT_ADJUDICATION.json and data/DEMO_JOINT_ADJUDICATION.json.

Shradha's independent tests apply to v2. This subsequent revision does not inherit a claim of independent code acceptance. Its unchanged model/backend is supported by the original checks; the new presentation/date layer has its own developer verification.

Run from the extracted release:

```bash
python3 -B verify_release.py
python3 -B -m unittest discover -s tests -v
python3 -B -O -m unittest discover -s tests -v
python3 -B validation/audit_evidence.py
```

The evidence audit describes preserved developer runs, not the distinct teammate-return total. Original machine snapshots retain pending semantic flags; the joint decision is an overlay keyed by exact run ID. Historical source records retain null values; current review summaries use known dates or “Not supplied”. No missing label is silently turned into a successful outcome.

Known limitations: open dependency advisories; partial Week-4 full answer rerun; R110 uncertainty; selected-case live coverage; missing later-confirmation date; actual presentation-machine rehearsal; uninspected security limits listed in the teammate return.
