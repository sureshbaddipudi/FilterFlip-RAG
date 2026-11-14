# Security evidence and reproduction handover

## Where to start

| Question | Evidence |
|---|---|
| Which threats and controls were mapped? | [Threat model](components/security-mapping/THREAT_MODEL.md), [STRIDE and OWASP mapping](components/security-mapping/RISK_MAPPING.md), [residual risks](components/security-mapping/RESIDUAL_RISKS_AND_FOLLOWUP.md) |
| Which dependency changes were assessed? | [Assessment](components/dependency-assessment/REPORT.md) and [candidate results](components/dependency-assessment/CANDIDATE_RESULTS.md) |
| Did the candidate change the saved research comparisons? | [Corrected comparator](components/compatibility-review/code/compare_research.py) and [saved compatibility result](components/compatibility-review/results/normal/SUMMARY.json). All 35 checks passed on the bounded set of 75 contexts. The recorded comparison covered 300 answer requests. |
| How can I check the published study counts? | [Baseline study](../research/baseline/README.md) and [extended comparisons](EXTENDED_COMPARISONS.md) |

The October mapping assessed six STRIDE threats and the ten entries in each of the OWASP Web, API, LLM and ML lists for the version examined. The records identify controls, evidence and residual risks. They do not establish a security certification for the later semester GUI.

## Check the published security registers

From the repository root, this command runs three original file-integrity controls using temporary fixtures:

```bash
python3 -B reproduction/tools/test_handover_tools.py IntegrityControls
```

## Replaying the archived handover

The original [environment notes](ENVIRONMENT_AND_ASSETS.md), [evidence index](EVIDENCE_INDEX.md) and [reproduction guide](REPRODUCTION_GUIDE.md) describe the full sealed semester packet. Run full-packet commands in a working copy of that packet. Its manifests, input evidence and original directory names are part of those checks. The research repository uses descriptive component directories and includes a publication subset.

Historical reports retain the review status at their original dates. The compatibility candidate is an engineering snapshot separate from the semester GUI. Some display copies replace archived contact numbers or machine-local path prefixes. Use the sealed originals for a byte-for-byte comparison.
