# FilterFlip Week-4 review return: Shradha, 2026-10-14

| Item (checklist Section 7) | File |
|---|---|
| 1. Completed checklist | `FilterFlip_Review_Shradha_2026-10-14.md` |
| 2. Human-review workbook (rows 2–19 filled) and per-case notes | `FilterFlip_Week4_Review_Shradha_2026-10-14.xlsx`, `FilterFlip_Review_Shradha_2026-10-14_case_reviews.md` |
| 3. ZIP verification, demo release check, normal/optimized test output | `logs/verify_release.txt`, `logs/tests-normal.txt`, `logs/tests-optimized.txt`, `logs/server.txt`, `logs/server2.txt` (ZIP hashes are recorded in checklist Section 2) |
| 4. Inspected exported case JSON | `FilterFlip_NanoMSMARCO_1045374.json` |
| 5. Issue reports and evidence | Checklist Section 6 (ISSUE-01 to ISSUE-03); `logs/s6_security_checks.txt`, `logs/s6_server.txt` |
| 6. Fresh-run records | `runs/` — RUN.json, EXIT.json, COMPARISON.json (where generated), console.log and answer-stage unique_results.jsonl for each run; `logs/s5_*.txt` for replay, regeneration, setup and fresh runs |

Runs: 2026-10-01 smoke, study-retrieval, study-filter, two study-answers attempts (stopped early); 2026-10-14 fresh extraction study-filter and study-answers (stopped at request 128). Failed answer stages have no COMPARISON.json because the runner does not write one for a failed stage; no substitute was created.
