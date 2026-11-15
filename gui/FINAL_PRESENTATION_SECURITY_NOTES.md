# Points to include in the final presentation

Prepare slides when the professor's presentation instructions are available. These notes do not mark Task 11 complete.

- Explain the trust boundaries: untrusted corpus passages, local browser/API, application/worker, pinned model service and private evidence files.
- Describe STRIDE controls with concrete examples: fixed request choices, literal text rendering, private configuration, bounded work, cancellation, identity checks and saved run/security events.
- Show one test example and the current suite totals. Python -O removes assertions; security checks use explicit validation and the suite also passes with -O.
- Present OWASP Web, API, LLM and ML as a scope-and-control mapping. Clearly identify partial coverage and untested categories; do not call the tool OWASP-certified.
- Explain the medium scanner warning for deliberate verified module execution and the still-open dependency findings. Tested controls do not make the whole environment vulnerability-free.
- Distinguish the live GUI from recorded evidence. Recorded TrustRAG is stage 1 only. Saved-answer judgments do not transfer to a newly generated answer.
- Present both mitigation gains and losses, challenge harms, selected-case limitations, uncertainty and the restricted scale. Do not claim a secure general mitigation or proven publication novelty.
- Quote independent v2.8 acceptance only after an actual return is received. Current new-version evidence is developer software verification with zero new research model calls.

## v2.9 updates

Demonstrate the new TrustRAG mode honestly: fixed original contexts and embeddings, fresh stage-1 filtering and fresh Qwen; not full TrustRAG. Mention 81 application tests, 15 additional security checks, 36 matching filter contexts and the bounded fresh integration checks, with their attribution. Explain the separate legacy NLTK advisory matches and the fixed-input/text-budget controls, without claiming dependency closure. Use Project work and security to show the full coursework map and draft report; retain pending approval/presentation status.
