# Validation and release boundary — 28 October 2026

## Decision

**Original and mitigation modes have completed developer live rehearsals for Heather.** Independent acceptance of this new v2 release is pending. Challenge mode is implemented and its filter/policy outputs were produced, but a complete four-answer challenge run has not been obtained in this rehearsal. Keep it outside the compulsory 15–20 minute demonstration.

The accepted Week-6 scientific analysis and earlier teammate acceptance remain unchanged. This release does not turn selected demonstrations into new independent research cases or human-reviewed verdicts.

## Tests and inspection

- 42 offline application/security/lifecycle tests passed normally and under `-O`. Earlier two failures came from an empty test mock configuration, were corrected, and their original logs remain in validation. No production behavior was changed to hide those failures.
- The same unchanged Week-6 policies reproduce 1,288 adapter mappings across 322 saved contexts. Native decisions and scores are supplied from the accepted records; this is offline adapter parity, not a new native-model experiment.
- Browser checks: original/mitigation panels inspected during live development; synthetic HTML/script payload remained literal text, with zero injected image elements and no execution marker; recorded human attribution remained separate; restart showed the partial challenge as interrupted; its downloaded JSON matched the saved result exactly. JavaScript syntax checked.
- A real second-job request was refused while mitigation was active. Synthetic tests cover cancellation, deadline, output bounds, descendant cleanup and crash states. Real-model cancellation across all faults is not claimed.
- Bandit: seven low findings, zero medium/high within the scanned application scope; developer dispositions in SECURITY. Limited secret-pattern scan found no matches in scoped application/test source. Neither scan is a security guarantee.
- Dependency inventory/SBOM and advisory outputs are supplied. Open advisories remain; see SECURITY. Application controls do not erase vulnerable dependency findings.

## Complete attempt ledger

| Run prefix | Mode | Attempts begun | Saved responses | Status and observation |
| --- | --- | ---: | ---: | --- |
| b130eb82 | Original Heather C/PN1 | 4 | 4 | Completed, 305.025 seconds. Clean answers and copied unfiltered answer name Nicole Gale Anderson; copied native-filter answer abstains. |
| adda87f4 | Mitigation Heather PN1 | 4 | 4 | Completed, 212.883 seconds. U and CN name Nicole Gale Anderson; N and E abstain. |
| 7bb2c075 | Heather false-claim challenge | 1 | 0 | Interrupted execution session; request outcome unknown. Raw state retained. |
| 8bdd72c0 | One replacement of the same challenge | 2 | 1 | Interrupted execution session; U names Nicole Gale Anderson, N has no saved response, E/CN not attempted. Raw state retained. |

Total: **11 answer attempts begun, nine saved responses, two completed runs, two interrupted runs**. The original bound was 12 attempts for three modes. A written interruption amendment allowed one replacement, raising the cap to 13 including uncertain attempts; actual usage remained 11. No further replacement was launched. Exact external interruption causes and times are not established. These interruptions are not negative semantic findings and are not hidden as completed runs.

Raw logs, requests, responses, model identities and first snapshots are copied without rewriting under evidence/. The two interruption records separately explain stale `running` values. A restarted server exposes `effective_status=interrupted` while preserving the last worker snapshot. Evidence audit uses saved responses, exact request hashes and policy inputs; it does not prove a clean shutdown or human correctness.

## Reproduce the offline validation

From the extracted release:

```bash
python3 -B verify_release.py
python3 -B -m unittest discover -s tests -v
python3 -B -O -m unittest discover -s tests -v
python3 -B validation/audit_evidence.py
```

The audit should report 322 contexts / 1,288 mappings, 11 begun attempts and nine saved responses. The included POLICY_PARITY_INPUT.json is a byte-identical copy of the accepted filter output; its old review flags remain historical and do not supersede the accepted analysis/ledger. The audit loads no research model and makes no network calls.

`SOURCE_PROVENANCE.json` identifies original sources. Its backend.py hash is the v1 source from which the new backend was developed, not a claim that v2 is unchanged. Policies, common helper, frozen profile, copied inputs, accepted reports and reviewer records retain their source bytes. RELEASE_MANIFEST.json binds final release bytes; run identities bind the backend used at computation time. Later UI/documentation edits do not retroactively change those identities.

## Pending before claiming full readiness

1. Suresh rehearses the core sequence on the actual presentation machine/projector; Shradha returns the narrow v2 checklist where available.
2. Challenge mode requires a separately budgeted complete live check if it will be demonstrated; do not promise it in the core review.
3. Review and remediate dependency advisories in a separate application environment, then establish compatibility without modifying accepted research records.
4. Comprehensive penetration testing, hard OS resource quotas, public deployment authentication and external security monitoring are not included. This is a local classroom application.

The synthetic browser fixture on localhost port 8781 was used only for inert-text verification, with no model calls. Automatic approval review rejected tool attempts to stop its execution session; it may remain until the host/session cleans it up. Do not confuse it with the real application at port 8767. The packaged fixture is not started by the application. No real model service was listening at the final interruption check; the application was subsequently restarted without launching a model.
