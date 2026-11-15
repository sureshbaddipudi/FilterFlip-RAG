# FilterFlip-RAG

M.Tech Secure Software Engineering project, IIT Hyderabad  
Suresh Kumar Baddipudi and Shradha Suryawanshi

Can adding a copy of a passage that contains the correct answer cause a RAG security filter to discard the evidence needed to answer a question? We compared retrieved passages, filter decisions and answers with and without filtering. The primary review identified eight events in 59 selected cases. The separate TrustRAG stage-1 study found five events, six non-events and one uncertain case among twelve selected questions.

Start with the [baseline study](research/baseline/README.md) for the research question, comparison conditions, datasets and software versions.

## Reproduce the study figures

From the repository root, use Python 3 with Matplotlib installed and choose a new output directory.

```bash
python3 reproduction/components/paired-results-analysis/code/plot_results.py --out figures-local
```

Open `figures-local/copy_exposure_endpoints.png` to see how many copies reached retrieval and how the reviewed outcomes changed across conditions. Open `figures-local/trustrag_support_core.png` to compare evidence support and answer usability for all 36 paired contexts. Each figure is also available in SVG format.

The [saved summaries](reproduction/components/paired-results-analysis/expected/) come from the semester paired analysis. The plotting script and four summary files are copied from that analysis. The TrustRAG context file includes only the case ID, condition and four recorded judgment fields used by the figure. Plotting uses the recorded labels and performs no model calls.

## Reproduction and extended comparisons

The [extended comparison guide](reproduction/EXTENDED_COMPARISONS.md) links the answer recovery code, copy-variant tables, TrustRAG stage-1 comparison and paired results. It includes commands for the offline recovery tests and copy-variant figure.

## Security and handover

See the [security and handover guide](reproduction/SECURITY_AND_HANDOVER.md) for STRIDE and OWASP coverage, dependency findings, compatibility results and an offline integrity check.

## Team contributions and review decisions

Suresh Kumar Baddipudi led the study design, research pipeline and experiments. Shradha Suryawanshi contributed the semester GUI release, application testing, case review and reproduction checks. We reviewed the outstanding cases together and recorded the scope of each decision.

| Study stage | Evidence |
|---|---|
| Primary study | [Week 4 decisions on the eight open cases](decisions/week04/SUMMARY.md) |
| Mitigation evaluation | [Week 6 scoring agreement](decisions/week06/SUMMARY.md) and [analysis acceptance](decisions/week06/ACCEPTANCE_RECORD.json) |
| Extended comparisons | [Agreed decisions](decisions/extension-review/JOINT_ADJUDICATION.json) and [fields retained as uncertain](decisions/extension-review/RETAINED_UNCERTAIN_FIELDS.json) |
| Semester handover | [Walkthrough and reproduction acceptance](decisions/final-handover/JOINT_ACCEPTANCE.md) and [verification records](verification/) |

Open the [GUI start guide](gui/START_HERE.md) to run the application. The [semester freeze decision](releases/FilterFlip_GUI_v2_9_Semester_Freeze_2026-11-14.md) covers v2.9. The [v2.9.3 checksum](releases/FilterFlip_GUI_v2_9_3.zip.sha256) identifies the distributed patch-release ZIP. Some links inside the original decisions refer to files in the corresponding archived handover packages.
