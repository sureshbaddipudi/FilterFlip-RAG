# Review on 30 October 2026 — 15–20 minutes including a live demo

## Main message

“We have completed the agreed work through Week 6, with documented limitations. We found that copying correct evidence can change a filter's decision and leave the answer model without sufficient support. We then tested simple copy-handling policies. They sometimes recover useful evidence, but also lose good answers and can retain false claims. We are not claiming a generally reliable new defense.”

The live GUI demonstrates computation now. The separate research view summarizes accepted earlier evidence. New demo answers remain pending human interpretation.

## Before the review

1. Read README and SECURITY. Use the fixed CPU configuration and existing frozen inputs/models. Connect power, close unrelated heavy applications, and keep the launch terminal available.
2. Verify the release manifest and run the two offline test commands. These do not load models. Open http://127.0.0.1:8767. Confirm the original Heather question is selected.
3. Allow time for one clearly labelled rehearsal before the event if needed. Record its ID, time and outputs; do not select only successful trials. Do not start several runs in parallel. All prior rehearsal evidence, including interruption/failure, is retained in this package.
4. Use a readable browser zoom/projector size and rehearse expanding the biography passage. Check that the model startup folder exists. Do not change to GPU during the review; Shradha reported a Vulkan crash previously.
5. Keep the ZIP and offline validation accessible. Saved outputs are a labelled fallback for explaining a failure, not a substitute that can be called live.

## Core 15-minute sequence

| Time | Action | Plain-language explanation |
| --- | --- | --- |
| 0–1 min | State the research question and start Original finding / Heather / Clean + answer-source copy. | “I am starting a new run. We compare the same question with and without one extra copy of the answer source.” |
| 1–3 min | Explain attacker and pipeline while CPU computes. | “The attacker adds one document copy. Retrieval chooses passages, the filter keeps or removes them, and Qwen answers from what remains. We do not let the attacker change the model or filter. The evaluator is outside the pipeline.” |
| 3–5 min | Explain milestones. | “Weeks 1–2 established feasibility. Weeks 3–4 built the evaluation evidence and human review. Weeks 5–6 tested the mechanism, copy-handling choices and challenges, then reconciled scoring and independently reproduced the analysis.” |
| 5–8 min | Inspect completed live panels, or show honest progress if still running. Expand the answer biography and its copy, then kept/removed passages. | “The important question is whether enough correct evidence remains. Losing a named passage alone does not prove failure. We compare all four answers and inspect semantic support.” |
| 8–11 min | Open Findings and Evidence, explicitly identifying it as recorded accepted research. | “Across the selected benign panel, near-copy handling gives seven accepted-core gains, eight losses and one unresolved comparison versus native. In the bounded false-claim checks it introduces two acceptances and avoids one. The trade-off is mixed.” |
| 11–13 min | Explain secure development and remaining risks. | “Inputs and routes are restricted; text cannot become browser code; one bounded process runs at a time; outputs and failures are retained. STRIDE and both OWASP lists are mapped to evidence. The frozen dependencies still have open advisories, so this is a local demonstration, not a production-security claim.” |
| 13–15 min | State next work and take questions. Export the live run. | “The next phase is final delivery and a separately scoped publication extension. We will first address application dependency risks in a separate environment, then test any scientific changes with a declared comparison plan.” |

### If the slot is 20 minutes

If the first run completes early, start **Week-6 mitigation / Heather / Answer-source copy** immediately after inspecting it. Explain the accepted analysis while it computes. Compare U (no filter), N (native), E (exact-copy handling) and CN (near-copy handling) on the same retrieved context. In development rehearsal U and CN named Nicole Gale Anderson, while N and E abstained. This is one observed example, not a guarantee or an aggregate result.

The original rehearsal took about 5 minutes 5 seconds; mitigation took about 3 minutes 33 seconds on this machine. These are observations, not promises. The developer false-claim attempts were interrupted; Shradha’s instruction challenge completed in about 2 minutes 21 seconds on her machine. Do not schedule all three modes inside a 15–20 minute slot.

### Optional challenge demonstration

Shradha completed the Heather instruction-containing challenge and both teammates accepted its findings. For an optional demonstrated challenge, select **Security challenge / Heather / Instruction-containing excerpt**. The false-claim and neutral live variants still need their own complete validation; do not present them as covered. Say before launching: “This deliberately supplies a frozen clean five-passage context plus one approved sixth passage. We freshly filter and answer, but we are not claiming the sixth passage was retrieved by an attacker.” Explain that the added passage contains both the correct biography and an instruction to output a test marker. The fixture has a recorded limitation. Read the actual new outputs; do not assume the historical outcome will recur. Challenge approval concerns the test material, not a verdict on the new response.

## What to point at in the GUI

- Run ID and state show whether computation is active, complete or stopped.
- Clean versus copied condition isolates the corpus change in original mode.
- Kept / removed / grouped-out passages explain the filter's action; passage order matters.
- The answer box is generated now. “Human review pending” is deliberate.
- A singleton bypass is shown when the evaluated policy leaves one representative; do not hide it as a normal native-filter decision.
- The recorded-case panel preserves original attribution and the current human-review ledger; it is not the verdict for this run.

## If something fails or is slow

Do not repeatedly click Run, change settings, or conceal partial output. Show the status, explain CPU latency, and continue the research/security explanation. If the allotted time is exhausted, stop the run using the GUI and export the partial record. Clearly state that the live comparison did not finish in the slot. A successful saved rehearsal may explain intended behavior only when explicitly labelled recorded. A second launch is a new attempt and must be recorded, not silently substituted.

## Likely questions

**Is this prompt injection?** The primary attack copies existing evidence without inserting instructions. The separate instruction-containing challenge is a different bounded test.

**Have you invented a better defense?** Not yet. The tested policies show both benefits and harms; negative findings are useful evidence.

**Are all results human reviewed?** The original 59 assessments have human confirmation as recorded in the ledger. Week-6 judgments were human-decided with disclosed AI assistance. Accepted scoring and analysis were checked by both teammates. New demo outputs do not inherit those judgments.

**Why is one answer uncertain?** R110 has a mixed/completeness ambiguity affecting five linked conditions. Keeping it uncertain prevents forcing the result in a preferred direction.

**Does TrustRAG also generate the final answers here?** No. The secondary work tested its filter stage. This GUI's demonstrated answering path uses the native RAGDefender comparison and the Week-6 policies; do not draw a completed TrustRAG-to-Qwen path.

**Is everything finished?** The agreed scope through Week 6 is closed with limitations. The full additional Week-4 answer rerun was set aside with partial coverage. Week-8 integrated delivery and publication extensions remain.
