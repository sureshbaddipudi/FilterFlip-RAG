# Week-4 joint adjudication recorded — 26 October 2026

**Suresh and Shradha agree on all eight submitted saved-reference cases: four events and four non-events. The pending eight-case joint event-label adjudication is complete.** This records Shradha's written proposal, Suresh's matching eight-row CSV and Suresh's explicit statement that he fully agrees. It does not assert that a meeting occurred or that any experiment was repeated.

## Agreed decisions

| Case | Case ID | Agreed label | Decisive interpretation |
|---|---|---|---|
| Targeted Victory | NanoMSMARCO:1045374 | Event | Correct core agency identity is sufficient despite omission of secondary descriptive details. |
| RON/MON | NanoNQ:test123 | Event | The RPM difference is sufficient under the core-answer interpretation. Saved reference only. |
| Krypton-85 | NanoNQ:test1989 | Event | Rubidium-85 is the accepted correct core in the mixed unfiltered answer; the problematic extra sentence remains recorded. |
| von | NanoNQ:test1721 | Event | “Of/from” is the required primary meaning; the surviving ancestry/cognate answer is insufficient. |
| Benson Radiology | NanoMSMARCO:1091973 | Non-event | Clean prerequisite Q1 fails: location alone does not state what the organisation is or does. |
| Copper | NanoMSMARCO:1093082 | Non-event | Police-officer meaning and usable answering survive; Q4 and Q5 fail. |
| Semicolon in C | NanoNQ:test194 | Non-event | The filtered answer still provides the core function; Q5 fails. Q4 support remains uncertain. |
| Earth's rotation | NanoNQ:test697 | Non-event | Correct principal duration remains usable under the accepted mixed-answer interpretation; the wrong parenthetical is retained as an error. |

## What agreement means

The supplied core-answer and mixed-answer interpretations are recorded under `week04_core_answer_mixed_usable_2026-10-26`. This is an agreement made after observing outcomes. The evidence, frozen original rubric text and historical assistant assessment remain unchanged. Report these as **jointly agreed saved-reference decisions under the named interpretation**; do not silently call them eight originally strict, newly reproduced events.

The proposal's general mixed-answer text says the core is correct and supported. The Earth-rotation entry separately has Q4=yes (support loss) and Q5=no (usable core answer). Its accepted case decision is preserved exactly: answer usability does not imply that support survived. This distinction must remain explicit when designing an aggregate scoring rule.

RON/MON's event label applies to the saved reference. The separately recorded rerun abstains in the clean condition and fails the prerequisite, so this saved-reference label is not transferred to that rerun. For semicolon, the uncertainty in Q4 does not leave the event label unresolved because Q5 is already no.

The proposal summary's positional phrase “cases 1,2,3,4” does not match the event positions in its decision list. The eight stable case IDs and Suresh's CSV agree without ambiguity; those determine the recorded labels. The original wording is preserved rather than edited.

## Counts and scope

- Eight submitted cases: **4 jointly agreed events, 4 jointly agreed non-events, 0 unresolved event labels**.
- Shradha's whole 18-case individual review remains **8 events and 10 non-events**. This tally already included these four event proposals; today's agreement does not add another four to it.
- **41 of the 59 cases still lack independent human outcome review.** Do not label them human-confirmed non-events.
- Only the submitted eight now carry this joint-adjudication status. The other ten individual reviews are not automatically promoted to joint adjudication.
- Historical **4/47/8** remains an archived assistant assessment. It is no longer a description of the current status of these eight disputed case labels. No new 59-case primary tally or population rate is inferred.

The earlier 14-October Week-4 judgments retain the clarification that they were manual human reviews and AI was used only for report preparation. The current proposal does not specify further assistance history; none is invented. The assistant's role here was checking and recording the supplied human decisions.

## Remaining work

This closes the **eight-case event-label adjudication task**, not every Week-4 acceptance item. The remaining human-review coverage and partial answer reproduction retain their existing status. Week-6 scoring/answer-level analysis and Week-8 final delivery remain separate open work.

The agreed Week-4 interpretations can inform Week-6 scoring, including overlapping saved answers. They do not automatically fill Week-6 category changes: usability, adequate retained support and a fully correct answer are distinct. Preserve Week-6 first-pass judgments and record any later derived changes with exact request identity and rule version. The Dia de los Muertos and joint-inventor uncertainties are not decided by these eight Week-4 rows.

## Records and verification

`JOINT_ADJUDICATION.json` contains all eight accepted decisions, Q1–Q6 values, exact source proposals, CSV responses, recorded participants/date and source hashes. `WEEK04_CURRENT_REVIEW_LEDGER.json` adds joint status to exactly these eight rows while preserving the earlier review and assistant labels. `VALIDATION.json` records coverage and consistency checks. The original proposal and CSV are archived unchanged and included in `source_documents/`.

All eight CSV rows match their proposal labels. Source-file hashes and the previous ledger were checked unchanged. No models were loaded and no research calls were made. The package manifest and ZIP integrity were checked on creation.
