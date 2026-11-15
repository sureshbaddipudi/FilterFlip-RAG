# Intake of Shradha's v2.8 SSE review

10 November 2026. Read-only assessment of the submitted review, supporting files and existing project records. No GUI code, sealed release, Desktop files, research outcomes or dependency versions changed. No models or supplied test scripts were executed. The original return is preserved unchanged.

## Recommendation

The return supports accepting the v2.8 operational/security improvements for the stated local, single-user demonstration, with the limitations below. This is a recommendation, not a newly recorded joint acceptance by Suresh and Shradha. Research answer correctness is outside this review.

## What Shradha reports

Section 13 is the v2.8 re-assessment; Sections 1–12 largely describe v2.7.2. Do not use the old executive-summary counts or unfixed wording as the current v2.8 status.

- W1, W3, W5, W8, W10 and W15: fixes verified (private config, security logging, verified-byte code loading, archiving, headers and cancellation shape).
- W6 improved: complete inventory checking; unsigned hashes do not establish independent authenticity.
- W12 improved: ordinary files are no longer group writable; the extracted top-level folder and two subfolders reportedly remain 0775.
- W2 dependency findings remain open. W4/W7/W13 remain documented local-host, fixed-runtime and model-security limitations.
- W9 diagnostic messages and W11 historical personal paths were not independently re-tested.
- 68/68 unit tests passed; malformed endpoint probes were rejected; a second server using the same run folder was refused.
- A cornflakes PN1 variants run completed with two operationally successful responses; another run was cancelled and the model port was freed.
- Browser checks reportedly passed for seven findings sections, saved TrustRAG cases, the nine-condition view and the four live modes. These are functional reports, not new semantic judgments.
- The new medium Bandit B102 finding is deliberate verified-code execution, already documented in the release. Her scan includes app and tools (one medium, nine low); ours covered production app code (one medium, seven low). The broader scope can explain the count difference, but her raw Bandit output is absent, so the exact two additional warnings cannot be reconciled from this ZIP.

## Supporting evidence actually supplied

The ZIP passes its CRC check and includes six files: the assessment, two test scripts, dependency JSON, a freeze list and scan metadata. Its SHA-256 is recorded in INTAKE_STATUS.json. No sender checksum was supplied for external comparison.

The dependency data can be independently recalculated from this return. Browser screenshots, test execution logs, security-event logs, archive receipts, Bandit JSON and fresh live-run exports are not included. Treat the corresponding results as reviewer-reported. This does not dismiss the review; it identifies the available level of supporting evidence.

The supplied configuration test script prints PASS/FAIL rather than failing its process on every failed assertion, and temporarily creates/removes cfg_inside.json in the target release's parent application folder. Consequently, the report's statement that the release folder was never modified needs qualification (temporary test file created and removed, if that script was used as written). Neither supplied script was run during this intake. Existing developer regression tests and evidence remain separately available in v2.8 validation/v28.

## Dependency counts reconciled without a new scan

| Package | Supplied raw rows | Distinct package/advisory groups | Earlier core groups |
|---|---:|---:|---:|
| certifi | 2 | 1 | 1 |
| filelock | 12 | 12 | 12 |
| Pillow | 39 | 39 | 39 |
| sentence-transformers | 1 | 1 | 1 |
| transformers | 28 | 19 | 19 |
| Torch | Skipped | Not assessed | 8 |
| setuptools | Absent | Not assessed | 1 |
| Total | 82 | 72 | 81 |

Method: within each package, merge advisory records sharing an ID or alias. All 72 derived groups overlap the earlier core groups by package and advisory identity. The earlier core total is 72 shared + 8 Torch + 1 setuptools = 81. Repeated IDs and aliases explain the ten excess raw rows. This is count reconciliation, not remediation or confirmation of exploitability.

The supplied freeze list has 40 non-comment requirement entries, and the audit JSON has 40 dependency records, including two skipped records. The report's 41-package figure is not supported by those files alone; it could reflect an unprovided installed-package inventory. Relative to the earlier 43-distribution core inventory, pip, setuptools and wheel are absent from the freeze list. The other explicit version pins match; the editable RAGDefender version appears only in a freeze comment. The editable vendor requirement and Torch 2.8.0+cpu were skipped by the submitted scanner. Our earlier Torch lookup normalized to upstream 2.8.0; CPU-build applicability remains unestablished.

The earlier core raw JSON, inventory, scanner versions and arguments already exist in FilterFlip_Final_Security_Review_2026-11-09. The return's request for those records can be met with existing evidence; a new scan is not needed merely to explain these counts. Do not apply the draft's suggested upgrade versions without separate applicability and compatibility work.

## Small corrections before course submission

1. Separate the historical v2.7.2 summary from a clearly labeled current v2.8 summary. Old claims of zero medium scanner findings, absent request logging and missing per-case TrustRAG do not describe v2.8.
2. Replace “82 known advisories” with “82 raw advisory rows, representing 72 distinct package/advisory groups in the supplied scan.” Explain skipped Torch and editable vendor code, and qualify the package count.
3. Record the browser checks as reviewer-reported and link exports/logs if available. Optional offline checks and full-size resource stress were not reported as run.
4. Describe W4/W7/W13 as retained, documented limitations unless explicit human risk acceptance is separately recorded. This intake does not infer joint adjudication from a report submission.
5. Qualify “no personal data”: historical source paths and review names are present. Preserve originals; a public redacted copy would be a separate derived package.
6. The instruction challenge's existence does not show successful prompt injection. The recorded nine instruction tests had zero observed successes, which also does not establish general resistance.
7. The report's mapping covers Web and selected LLM categories, with STRIDE/MITRE additions. It does not itself provide the complete API and ML mapping requested for the coursework; attach/reference the bundled OWASP_COVERAGE.md and explain partial/out-of-scope entries. No new framework-ID validation was performed in this intake.
8. Explain the extraction permission effect. Three reported directories remain group writable; 0644 files alone do not prevent directory-entry replacement by a writer. On the local demo machine, removal of group/other write permission from release directories is a reasonable operational follow-up. No permission changes were made here.
9. Qualify “release not modified” as above if the supplied config script was used as written. Preserve the original submitted report and issue corrections separately.

## Next bounded action

Keep v2.8 as the current demo candidate. Finalize the review wording and acceptance record with these limitations; retain the missing-evidence distinction. Additional model experiments or a new GUI version are not required by this return. If stronger reproducibility of the acceptance is needed, collect the already-produced run exports and logs rather than repeating all model runs. Dependency remediation and public/multi-user deployment remain separate tasks.
