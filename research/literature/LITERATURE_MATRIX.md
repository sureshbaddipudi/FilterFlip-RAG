# Closest literature — fifteen distinct works

Cutoff: 1 November 2026, Asia/Kolkata. This is a focused primary-source comparison, not a systematic review or proof of priority. [PAPER_REGISTRY.json](PAPER_REGISTRY.json) holds verified titles/authors/version dates, publication qualifiers and a short positioning note for each row. [VERSION_NOTES.json](VERSION_NOTES.json) records revision traps. Refer to exact source sections below; no experiment or headline paper score is reproduced by this table.

| ID / shorthand | Inspected text | Goal / role | Intervention stage | Closest overlap / boundary | Reading locators |
|---|---|---|---|---|---|
| R01 / RAGDEFENDER | [v1](https://arxiv.org/html/2511.01268v1) | defense / targeted knowledge corruption | prioritized adversarial retrieval; post-retrieval groups | No correct-copy-only primary attack established in audited threat setup | III; IV-A/B; V; VI-E; VII |
| R02 / TRUSTRAG | [v3](https://arxiv.org/html/2501.00879v3) | defense / corpus poisoning | cluster filtering then LLM recovery | Stage-1 filtering is not the full pipeline | 3.2; 3.3; 5.1; Appendix E |
| R03 / JAMMING | [v4](https://arxiv.org/html/2406.05870v4) | attack / answer denial | single inserted blocker document | Optimized blocker; not the coursework source-copy constraint | 4; 5.2–5.4; 6.5; 8 |
| R04 / POISON BENCH | [v1](https://arxiv.org/html/2505.18543v1) | benchmark / poisoning and defenses | multiple attack / defense settings | Benign evidence erasure already studied | 5; Appendix I (Details of Defense Results), hybrid-defense paragraph; Appendix J |
| R05 / MUTEDRAG | [v1](https://arxiv.org/html/2504.21680v1) | attack / guardrail refusal | retrieved jailbreak-trigger text | Safety-trigger content differs from correct-source copies | 3; 4 |
| R06 / CUER | [v1](https://arxiv.org/html/2604.05467v1) | measurement / evidence utility | retrieved-context interventions | Explicit DUPLICATE operator | 4.3; 4.6; 5.5; 6.1/6.9; Appendix C |
| R07 / SYBIL | [v1](https://arxiv.org/html/2607.03739v1) | benchmark / coordinated false target | forced exposure and retrieval diagnostics | Monomorphic versus diverse false-claim coalitions | 3; 4; 6; 8.1; Appendix A.6 |
| R08 / CAMODOCS | [v1](https://arxiv.org/html/2608.28389v1) | attack / camouflaged false target | corpus poisoning and filtering | Utility loss of erasure-heavy defense | 3.1/3.2; 4.3 Table 3; Appendix E |
| R09 / POISONEDRAG | [v3](https://arxiv.org/html/2402.07867v3) | attack / chosen incorrect answer | insertion into knowledge database | Duplicate-text filtering already evaluated | 3.1/3.2; 4.1/4.2; 7.3 |
| R10 / ROBUSTRAG | [v2](https://arxiv.org/html/2405.15556v2) | defense / certified aggregation | retrieval-corruption bound | Conditional certificate, not universal promise | II-B/D; III; IV; VI |
| R11 / GUARDRAG | [v1](https://arxiv.org/html/2610.35071v1) | defense / suspicious clusters | retrieval expansion, deduplication, HAC | Explicit correct-copy clean stress test | 4; 5.3 Table 5; Limitations; Appendix C |
| R12 / LENS | [v2](https://arxiv.org/html/2609.35155v2) | attack / valid rule applied out of scope | fact-preserving inserted packet | Factual validity does not ensure safe composition | 2.1/2.3; 3; 4.4; 5 |
| R13 / COORDGUARD | [v1](https://arxiv.org/html/2610.24834v1) | defense / coordinated retrieval poison | query-anchored geometry | Benign semantic concentration and utility frontier | 1; 3.1/3.3; 4.2/4.4; Appendix D |
| R14 / RAGSENTINEL | [published PDF](https://aclanthology.org/2026.emnlp-main.546.pdf) | defense / geometric consensus | post-retrieval filtering | Honest-majority and separation assumptions | Published PDF sections 3-5; Theorem 1 (PDF p.6 / printed p.12554); Appendix B |
| R15 / SAFERAG | [published PDF](https://aclanthology.org/2025.acl-long.230.pdf) | benchmark / RAG security | retriever/filter/generator boundaries | Silver noise and White DoS | Published PDF sections 3.3.1 and 3.3.4; Figure 4 |

“Not established” and NR refer to this reading scope; neither means the paper proves the opposite or never contains the feature. Human-annotation procedures were not exhaustively audited across all works, and no “first human-reviewed study” claim is made. There is no cross-paper score ranking: threat models, exposure protocols, evidence windows, generators and scoring rules differ.

The immediate priority checks for any future novelty claim are R06 and R11 for duplication/evidence effects; R03/R05/R15 for availability and refusal; R12 for broader fact-preserving attacks; and R04/R08/R13 for utility loss under defenses. R01 is the native method context; R02 bounds component-to-system transfer. R10/R14 illustrate conditional guarantees that this coursework has not tested or refuted.
