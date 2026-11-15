# FilterFlip-RAG — final semester report, v2

Prepared from the 9 November 2026 evidence cutoff; packaged 10 November 2026 from the completed semester records and the latest accepted handover/security evidence. This is the revised manuscript for the authors' final reading, not a new human acceptance of the report.

## Read first

Open **FilterFlip_Final_Semester_Report.pdf**. The report explains the problem, related work, architecture, experimental method, primary findings, reproduction, nine copy conditions, TrustRAG stage-1 extension, mitigation trade-offs, GUI and Secure Software Engineering work. Limitations and post-semester research are explicit.

The report contains eight figures, including three actual GUI screenshots, and 24 tables. The primary 8/51 finding, reproduction scope, unresolved outcomes and unsuccessful mitigation are preserved. Academic references contain papers, datasets and standards. Internal hashes remain only in the companion evidence/verification files.

## Editable source

The complete source is `latex/main.tex`, its `sections/`, `figures/` and `references.bib`. No files outside this package are needed to compile it.

On a system with a standard TeX Live installation and latexmk:

```bash
cd latex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The output is `latex/main.pdf`. Without latexmk:

```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Shell escape is not required. Figures and screenshots are included locally. Diagram/chart source is in the LaTeX sections.

## Supporting material

- `review/V1_REVIEW_AND_CHANGES.md`: substantive review of the earlier manuscript and the changes made.
- `review/QUALITY_CHECKS.md`: compilation, layout and source-consistency checks.
- `evidence/TABLE_TO_SOURCE.md`: where the numerical findings come from.
- `evidence/PRIMARY_CASE_CATALOG.json`: all 59 primary case identities, questions, qualifications and recorded values.
- `evidence/v1_snapshot/`: unchanged copies of selected historical analysis records.
- `evidence/final_acceptance/`: dated acceptance that supersedes older pending fields for its exact scope.
- `evidence/final_security/`: latest local-GUI security assessment and remaining risks.
- `evidence/SCREENSHOT_PROVENANCE.json`: actual served-GUI capture context; no model calls during capture.
- `evidence/SOURCE_INDEX.json`: source locations and integrity identities for the copied records.

Historical snapshots can contain status statements that were pending at their original date. Use the dated final acceptance for current status, without rewriting the original snapshot. Review attribution in original evidence is retained.

This is a report/source package, not a replacement for the full experiment reproduction packages. No original code, frozen input, result or review was edited. No Desktop files were changed and no research generation was performed.

The bibliography includes a brief GuardRAG citation because the completed Task-10 literature record already includes that work. Detailed implementation comparison and experiments remain future research; the report makes no claim about an author's personal reading date.
