# Artifact sources and attribution

This package is a team research handover. It does not assign a new blanket license to all included material. Preserve each upstream project's notices and dataset attribution. Project-authored experiment scripts and reports are supplied for this collaboration; no additional public license is asserted here.

| Material | Source / pinned identity | Local provenance |
|---|---|---|
| RAGDefender code and research artifacts | https://github.com/SecAI-Lab/RAGDefender ; commit `ba2a17efba165d45409114df2d70b030ade1e1b8` | `reference/legacy/vendor/RAGDefender/`, including `LICENSE`, READMEs and Git metadata |
| TrustRAG source used by the component adapter | https://github.com/HuichiZhou/TrustRAG ; commit `11dcea0262d14b0e38e22e1d7ddce4a151e82a61` | `reference/output/filterflip_study_v1/sources/TrustRAG/`; component adapter and manifest under `reference/output/filterflip_trustrag_component/` |
| NanoNQ | https://huggingface.co/datasets/zeta-alpha-ai/NanoNQ ; revision `77540146379abf95df8326a3c5bb9eb21c7146c3` | Original card/data and acquisition manifest under `reference/output/filterflip_study_v1/sources/` |
| NanoMSMARCO | https://huggingface.co/datasets/zeta-alpha-ai/NanoMSMARCO ; revision `7b8ff22f2771dc65ac5b439f222eb19a1f56abda` | Same sources directory |
| Earlier selected research inputs | Bundled upstream RAGDefender artifacts plus recorded selection plans | `reference/legacy/vendor/RAGDefender/artifacts/` and per-stage plans/results |
| TrustRAG component Python dependencies | Recorded small runtime dependency tree | `reference/output/filterflip_trustrag_component/runtime/`; package metadata/license notices retained |
| Main/alternative MiniLM and SimCSE weights | Hugging Face repositories and revisions listed in `models.json` | Not included; downloaded separately and hash-checked |
| Qwen and Llama served model packages | Ollama models named/digested in the guide and original request manifests | Not included; obtain separately under their respective model terms |

The bundled Nano dataset cards advertise CC BY 4.0. Preserve the publisher attribution, original cards, acquisition records and transformation descriptions. Our use of their `train` files as evaluation corpora is a study-design choice, not a publisher-designated test split. Original-source facts may be historical.

Copies, neutral prefixes, chunks, case selection, assistant source/outcome labels, and generated answers are documented research transformations. The portable `work/` copy additionally adapts machine paths and derived hash references; `PORTABILITY_REPORT.json` records this after preparation. Original reference artifacts remain byte-preserved.

This team ZIP includes raw evidence needed for review, including public-source contact passages. Prefer the Heather example for public demonstrations; do not present archived contact details as current contact advice. Before a public artifact release, reconcile annotations, confirm attribution/redistribution requirements for all upstream content, and prepare a deliberate publication subset.
