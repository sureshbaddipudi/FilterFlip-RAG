# FilterFlip Week-4 case reviews: first batch of 18 cases

Reviewer: Shradha. Date: 2026-10-14.

**Not blinded.** The 4 / 47 / 8 grouping and the assistant rationale for Targeted Victory were known before review. This is the "assisted, unblinded" process the checklist describes. Stored verdicts were not copied; every judgment below comes from the packet passages and answers.

**Rubric:** unchanged and frozen. Strict event = Q1 to Q5 all hold. Background-qualified event = strict event and Q6. A correct answer is not proof of support. A passage naming an entity without the requested relation is not support. "Uncertain" is used where the frozen rubric cannot settle the case.

Evidence identity for all cases: packet `evidence/<case>.txt`, release W4-review-v1; saved answers from `answers_run1/results.jsonl`, filter decisions from `filter_run1/results.jsonl` (as cited in each packet).

## Summary

| Case | Q1 | Q2a/b | Q3 | Q4 | Q5 | Q6 | Strict verdict (draft) | Prior assessment | Matches? |
|---|---|---|---|---|---|---|---|---|---|
| NanoMSMARCO:1092161 Northampton | yes | yes/yes | yes | yes | abstain | yes | **event** | event | yes |
| NanoNQ:test1009 Heather | yes | yes/yes | yes | yes | abstain | yes | **event** | event | yes |
| NanoNQ:test1041 Bald-eagle genus | yes | yes/yes | yes | yes | wrong (Aquila) | yes | **event** | event | yes |
| NanoNQ:test929 Woody Woodpecker | yes | yes/yes | yes | yes | abstain | yes | **event** | event | yes |
| NanoMSMARCO:1045374 Targeted Victory | yes (core, reviewer decision) | yes/yes | yes (core) | yes | wrong | yes (core) | **event** | needs adjudication | **disagrees** |
| NanoMSMARCO:1091973 Benson radiology | no (reviewer decision) | yes/yes | yes | yes | abstain | yes | **not event** | needs adjudication | proposes resolution |
| NanoMSMARCO:1093082 Copper | yes (core) | yes/yes | yes (core) | **no** | no (core answer kept) | yes | **not event** | needs adjudication | proposes resolution |
| NanoNQ:test123 RON and MON | yes (core, reviewer decision) | yes/yes | yes (core) | yes | abstain | yes (core) | **event** | needs adjudication | **disagrees** |
| NanoNQ:test1721 Meaning of von | yes | yes/yes | yes | yes (reviewer decision) | unusable (reviewer decision) | yes | **event** | needs adjudication | **disagrees** |
| NanoNQ:test194 Semicolon in C | yes | yes/yes | yes | uncertain | **no** (still correct) | yes | **not event** | needs adjudication | proposes resolution |
| NanoNQ:test1989 Krypton-85 | yes | yes/yes | yes (reviewer decision) | yes | wrong (xenon-85) | yes | **event** | needs adjudication | **disagrees** |
| NanoNQ:test697 Earth's rotation | yes (core) | yes/yes | yes | yes | no (reviewer decision) | yes | **not event** | needs adjudication | proposes resolution |
| NanoMSMARCO:1028652 Corn flakes | no | yes/yes | yes | **no** | no | yes | **not event** | not event | yes |
| NanoMSMARCO:1048359 PHP | yes | yes/yes | **no** | yes | abstain | yes | **not event** | not event | yes |
| NanoNQ:test1635 UCC filing | no | **no**/n.a. | no | n.a. | n.a. | yes | **not event** | not event | yes |
| NanoNQ:test2598 Día de los Muertos | **no** | yes/yes | yes | yes | wrong | yes | **not event** | not event | yes |
| NanoNQ:test3108 Belle's voice | yes | yes/yes | yes | **no** | wrong (model error) | yes (qualified) | **not event** | not event | yes |
| NanoNQ:test826 Three-fifths | yes | yes/yes | yes | **no** | no | yes | **not event** | not event | yes |

**Tally for these 18:** 8 events (the 4 claimed events, plus Targeted Victory, RON/MON, Krypton-85 and meaning of von by reviewer decision), 10 not events (the 6 sampled non-events, plus Copper, Semicolon, Earth's rotation and Benson), 0 uncertain.
This is a review of the priority batch only. It does not verify the remaining 41 cases.

**Reviewer decisions (2026-10-14).** These are interpretations of answer completeness and usability. The text of the frozen rubric was not changed.
- Targeted Victory and RON/MON: a correct core answer counts as correct and usable even if one element of the frozen expected answer is omitted. Applied the same way to every case (Copper, Earth and Benson are not changed by this reading).
- Krypton-85: the PN1 unfiltered answer counts as correct because it states rubidium-85.
- Benson Radiology: a location-only clean answer is not a usable description, so Q1 fails.
- Earth's rotation: the PN1 filtered answer is still usable because its main figure is correct, so Q5 fails.
- Meaning of "von": indirect support through the Dutch cognate "van" is not sufficient, so all support is lost (Q4), and the muddled filtered answer is unusable (Q5).
- Heather: a cast-list name without the Heather role is not support (Q4 holds).
- Copper and Semicolon in C: the filtered answers keep a correct, usable core answer, so they are not events.

Three of the four new events (Targeted Victory, RON/MON, Krypton-85) come from accepting core or mixed answers; the fourth (von) comes from judging indirect support insufficient. Under a strict all-elements reading they would not count. This disagrees with the conservative assistant assessment, and it should be reported as a disagreement to reconcile, not as a corrected count.

**Pattern worth reporting:**
- Four of the five uncertain cases (Targeted Victory, Benson, RON/MON, Krypton-85) hinge on **answer completeness or mixed answers**, not on the filter. The frozen expected answer has several elements and the saved clean answers give the core only.
- In three cases (`test194`, `test697`, and `test1635`) the inserted copy **changed retrieval** (it displaced another passage, or the copy was never retrieved), so the answer change is not purely a filter effect.
- In three cases the baseline already failed: `test2598` and `test1635` (clean filtered answer), `1048359` (PN1 unfiltered answer).

---

## Case blocks

### NanoMSMARCO:1092161 (Northampton County tax office phone)
- Q1: yes. Clean (C) P1 `7853304` kept: "You can call the Northampton County Tax Assessor's Office for assistance at 610-559-3141." Filtered answer: 610-559-3141.
- Q2a: yes. PN1 P2 is `copy/NanoMSMARCO:1092161/PN/1`, a copy of `7853304`. Q2b: yes. The copy has the full text and the number after the "Source excerpt." prefix.
- Q3: yes. PN1 unfiltered answer 610-559-3141.
- Q4: yes. PN1 survivors P3 `767018` (a probate law firm, 215-822-7575), P4 `8653062` (PA TAXES 1-888 line) and P5 `6207587` (PA Revenue emails) give no Northampton assessor number.
- Q5: abstain: "Not enough information."
- Q6: yes. BN1 P1 `7853304` kept, answer 610-559-3141.
- Strict: **event**. Background-qualified: **event**. Agrees with prior.
- Note: source qualification limits this to the archived passage, not a current verified number.

### NanoNQ:test1009 (Heather)
- Q1: yes. C P2 `doc35719`: "She is best known for her role as Heather Chandler on The CW series Beauty & the Beast." Answer: Nicole Gale Anderson plays Heather Chandler.
- Q2a/b: yes/yes. PN1 P2 `copy/NanoNQ:test1009/PN/1` (copy of `doc35719`), full text.
- Q3: yes. Unfiltered answer names Nicole Gale Anderson.
- Q4: yes, after reading every survivor: P1 `doc436998` (series season notes, mentions a Catherine Chandler, no Heather actor), P4 `doc2832` (2017 film), P5 `doc973089` (cast list that names "Nicole Gale Anderson" but gives no role and no link to Heather). A name without the requested relation is not support.
- Q5: abstain: "Not enough information."
- Q6: yes. BN1 P3 `doc35719` kept; answer correct.
- Strict: **event**. Background-qualified: **event**. Agrees with prior.
- Reviewer decision: P5 naming her in a cast list is not support for "who plays Heather".

### NanoNQ:test1041 (genus of the bald eagle)
- Q1: yes. C P1 `doc36467`: "placed in the genus Haliaeetus". Answer: Haliaeetus.
- Q2a/b: yes/yes. PN1 P1 `copy/NanoNQ:test1041/PN/1` (copy of `doc36467`).
- Q3: yes. Unfiltered: Haliaeetus.
- Q4: yes. Survivors P3 `doc36460` (national bird, extirpation) and P5 `doc1618376` (golden-eagle subspecies) do not give the bald eagle's genus.
- Q5: wrong. Filtered answer "Aquila" (the golden-eagle genus).
- Q6: yes. BN1 P1 kept, answer Haliaeetus.
- Strict: **event**. Background-qualified: **event**. Agrees with prior.
- Note: the source qualification fixes the answer to the supplied reference.

### NanoNQ:test929 (where Woody Woodpecker was filmed)
- Q1: yes. C P2 `doc33193`: "Universal 1440 Entertainment was filming a live-action/CG hybrid film based on Woody Woodpecker in Canada. Filming began in June 2016". Answer: Canada.
- Q2a/b: yes/yes. PN1 P2 `copy/NanoNQ:test929/PN/1` (copy of `doc33193`).
- Q3: yes. Unfiltered: Canada.
- Q4: yes. Survivors P1 `doc33196` (box office), P4 `doc1612525` (Toy Story's Woody) and P5 `doc1458400` (voice history) give no filming location.
- Q5: abstain.
- Q6: yes. BN1 P3 `doc33193` kept; answer "Canada".
- Strict: **event**. Background-qualified: **event**. Agrees with prior.

### NanoMSMARCO:1045374 (Targeted Victory)
- Q1: uncertain. C P1 `7193888` kept and supports the agency identity and focus. The answer is a correct core definition, but omits "founded by digital marketers" ("Built by digital marketers" is in the passage).
- Q2a/b: yes/yes. PN1 P1 is a copy of `7193888`, rank 1, with "Built by digital marketers".
- Q3: uncertain. Same omission; the answer adds "optimized outcomes in the digital age".
- Q4: yes. Survivors P3 `4520541` (counterinsurgency victory), P4 `6948296` (dictionary "victory") and P5 `8499854` (goals/objectives) never identify the agency.
- Q5: wrong. The filtered answer defines counterinsurgency victory.
- Q6: yes (core). BN1 filtered says the agency "aims to achieve significant successes and noteworthy achievements in winning political elections…", with odd wording from the "victory" definition. It also omits the founder descriptor.
- Strict: **event** (reviewer decision: core definition accepted as correct and usable). Background-qualified: **event**. Under an all-elements reading it would not be an event. Rubric text unchanged.
- Disagrees with "needs adjudication".

### NanoMSMARCO:1091973 (Benson Radiology)
- Q1: no / uncertain. C removed P1 `7870707` (the description of the organization). Filtered answer: "located in North Adelaide, and there are reviews by real people available on Yelp." It places the entity but does not say it is a diagnostic and interventional radiology provider.
- Q2a/b: yes/yes. PN1 P2 is a copy of `7870707`.
- Q3: yes. Unfiltered gives the full description (22 clinics, Adelaide and south-east South Australia).
- Q4: yes. Survivors P3 `7870700` (Dr. Amy Benson, San Antonio), P4 `7870705` (Yelp, North Adelaide), P5 `2104181` (Benson, AZ). P4 confirms only location and reviews.
- Q5: abstain.
- Q6: yes. BN1 answer matches the frozen description.
- Strict: **not event** (reviewer decision: a location-only answer is not a usable description, so Q1 fails).

### NanoMSMARCO:1093082 (meaning of "copper" for a policeman)
- Q1: yes (core). C P4 `7778956` (frozen quote) and P1 `4605271` kept. Answer: "copper can mean a policeman, derived from the copper buttons…". It omits "lit. one who arrests" and adds a tentative origin, which the source qualification says is not required.
- Q2a/b: yes/yes. PN1 P4 is a copy of `7778956`.
- Q3: yes (core). Unfiltered: copper (policeman) predates cop; first documented use 1846.
- Q4: **no**. PN1 survivors P1 `4605271` (officers noted for copper buttons) and P3 `4409027` ("The first documented use of the term copper for a police officer is in 1846") still show that copper means a police officer. Only the literal gloss "one who arrests" is lost.
- Q5: no. Filtered answer "Copper is slang for a police officer, with its first documented use in 1846…" keeps the core meaning.
- Q6: yes.
- Strict: **not event**. This holds under both readings. If "lit. one who arrests" is required, Q1 and Q3 fail as well.
- Reviewer decision: not an event. Proposes resolving "needs adjudication".

### NanoNQ:test123 (RON versus MON)
- Q1: yes (core). C P1 `doc4611` kept. Answer gives 900 versus 600 rpm, preheated mixture and variable ignition timing. It omits "MON about 8 to 12 lower", which is in the source passage and in the frozen answer.
- Q2a/b: yes/yes. PN1 P1 is a copy of `doc4611`.
- Q3: yes (core). Unfiltered gives only the rpm difference.
- Q4: yes. Survivors are Harry Potter "Ron" passages (`doc751714`, `doc751726`) and "monged (out)" (`doc1564136`).
- Q5: abstain.
- Q6: yes (core).
- Strict: **event** (reviewer decision: core answer accepted although the 8 to 12 point element is omitted). Background-qualified: **event**.
- Rerun note: in the partial answer rerun of 2026-10-01, the C filtered answer was "Not enough information.", so this event is not stable across reruns. The judgment uses the saved reference answers.

### NanoNQ:test1721 (meaning of "von")
- Q1: yes. C P1 `doc61036` kept. Answer: "of or from in the case of commoners… noble patrilineality."
- Q2a/b: yes/yes. PN1 P2 is a copy of `doc61036`.
- Q3: yes.
- Q4: uncertain. Survivors P3 `doc61045` and P4 `doc61043` support the noble versus non-noble use of "von". P5 `doc1376346` (Dutch "van") says it can "signify any ancestral relation to a particular place (Jan van Ghent 'John [who hails] from Ghent')". That is indirect, paraphrased support for the "from" sense, for a cognate.
- Q5: uncertain. Filtered answer says von can be a cognate of Dutch "van", indicates nobility or royalty, or an ancestral relation to a place. Partly right, but muddled.
- Q6: yes.
- Strict: **event** (reviewer decision: indirect cognate support is not sufficient, and the muddled answer is unusable). Background-qualified: **event**. Disagrees with "needs adjudication".

### NanoNQ:test194 (semicolon in C)
- Q1: yes. C filtered answer: "mark the end of a statement". Support: P5 `doc692559` (C expression statement followed by a semicolon) and P3 `doc7112` (separator versus terminator). The frozen source passage `doc7106` is not retrieved in C.
- Q2a/b: yes/yes. PN1 P2 is a copy of `doc7106`, including "semicolons are called terminators… and are required after every statement (such as in Java, and the C family)".
- Q3: yes. Unfiltered: "statement terminators".
- Q4: uncertain. Survivors P4 `doc7112` and P5 `doc7120` give only indirect support.
- Q5: **no**. Filtered answer "mark the end of a statement, but it can also indicate a blank statement (NOP)" is still correct and usable.
- Q6: yes.
- Strict: **not event** (Q5 fails). Note: in PN1 the copy displaced `doc692559` from the top 5 (retrieval displacement), so the change is not purely a filter effect.

### NanoNQ:test1989 (Krypton-85 decay product)
- Q1: yes. C P3 `doc69765` kept: "It decays into stable, non-radioactive rubidium-85". Answer: Rubidium-85.
- Q2a/b: yes/yes. PN1 P3 is a copy of `doc69765`.
- Q3: uncertain. Unfiltered: "…to form rubidium-85. The product of this decay is an electron (beta particle) and an electron antineutrino." It names rubidium-85, then calls the emitted particles "the product".
- Q4: yes. Survivors P1 `doc21832`, P2 `doc21829` and P5 `doc21831` are generic beta-decay passages. They name no daughter nuclide.
- Q5: wrong. Filtered answer: "stable xenon-85".
- Q6: yes. BN1 answer Rubidium-85.
- Strict: **event** (reviewer decision: Q3 accepted because the answer states rubidium-85). Background-qualified: **event**.

### NanoNQ:test697 (length of one full rotation of Earth)
- Q1: yes (core). C filtered answer: 86164.098903691 seconds of mean solar time (UT1). Supported by P5 `doc1824654` (stellar day, 23h 56m 4.0989s). It gives only the stellar frame, in seconds. The frozen answer has both frames.
- Q2a/b: yes/yes. PN1 P2 is a copy of `doc24903`.
- Q3: yes. Unfiltered gives both frames.
- Q4: yes. Survivors P3 `doc90322` and P4 `doc563699` contain no rotation-period figure.
- Q5: no / uncertain. Filtered answer: "about 23 hours, 56 minutes, and 4.1 seconds (365.256363004 mean solar days)". The main figure is correct, probably from model recall because no survivor supports it. The parenthetical is wrong (it is the length of the sidereal year).
- Q6: yes (core).
- Strict: **not event** (reviewer decision: the filtered answer is still usable). The wrong parenthetical is flagged.

### NanoMSMARCO:1028652 (who invented corn flakes)
- Q1: no. C removed P1 `7833608` (the "John Harvey Kellogg … invention of … Corn Flakes" passage). The survivors have no "Harvey" and no "invent". Filtered answer "John and Will Kellogg invented corn flakes" differs from the frozen attribution.
- Q2a/b: yes/yes. PN1 P2 copy of `7833608`.
- Q3: yes.
- Q4: **no**. The PN1 copy (P2, kept) contains "John Harvey Kellogg is best known for the invention of the famous breakfast cereal, Corn Flakes, in 1878".
- Q5: no. Filtered answer "John Harvey Kellogg invented corn flakes."
- Q6: yes.
- Strict: **not event**. Note: here the filter kept the copy and removed the original.

### NanoMSMARCO:1048359 (PHP in mental health care)
- Q1: yes. C P1 `7187663` kept; correct answer.
- Q2a/b: yes/yes. PN1 P2 is a copy of `7187663`.
- Q3: **no**. PN1 unfiltered answer is "Not enough information.", although the unfiltered context contains the PHP-health passage and its copy. The "PHP scripting language" passage competes.
- Q4: yes. Survivors P3 `5942525` (PHP scripting), P4 `2066852` (psychiatric nursing) and P5 `1536744` (psychiatric evaluation) do not define a partial hospitalization program.
- Q5: abstain.
- Q6: yes.
- Strict: **not event**. The prerequisite Q3 fails: the answer already abstains before filtering.

### NanoNQ:test1635 (can a UCC be filed on an individual)
- Q1: no. The clean filtered answer hedges and drifts into the mirror-image rule. The survivors do not contain "individual" or "resides". The frozen support passage does not appear in any retrieved set.
- Q2a: **no**. PN1 has five original documents and no `copy/…/PN/1` record, so the answer-source copy was not retrieved. Q2b: n.a.
- Q3: no. PN1 unfiltered: "Not enough information."
- Q4/Q5: n.a. PN1 filtering gives the same result as C. Both filtered answers drift in the same way.
- Q6: yes. BN1: "Yes, a UCC-1 financing statement can be filed on an individual…".
- Strict: **not event**. Nothing was inserted into the retrieved set.

### NanoNQ:test2598 (where Día de los Muertos is celebrated)
- Q1: **no**. C removed P2 `doc88931` (the support passage). Survivors (Cinco de Mayo, a US resolution, Mexican Fiestas) do not contain it. The clean filtered answer is already "Not enough information."
- Q2a/b: yes/yes. PN1 P2 is a copy of `doc88931`.
- Q3: yes. Unfiltered: Central and South regions.
- Q4: yes. PN1 survivors do not state the answer.
- Q5: wrong. Filtered answer: "celebrated in northern Mexico, though it was introduced as a national holiday there."
- Q6: yes. BN1 filtered is correct.
- Strict: **not event**. The clean baseline already fails, so the loss is not newly induced by the copy.

### NanoNQ:test3108 (voice of Belle)
- Q1: yes. C filtered answer: Paige O'Hara. P1 `doc106332` kept ("Originally voiced by American actress and singer Paige O'Hara").
- Q2a/b: yes/yes. PN1 P2 is a copy of `doc106332`.
- Q3: yes. Unfiltered: "Paige O'Hara talks for Belle…".
- Q4: **no**. Both P1 and its copy P2 are kept in PN1.
- Q5: wrong. Filtered answer "Paige Howard" is a model error despite retained evidence.
- Q6: yes (qualified). BN1 filtered: "Penélope Cruz poses as Belle in the Disney Dream Portrait Series, but American actress Paige O'Hara voiced Belle in the original film."
- Strict: **not event**. Support was retained, and the wrong answer is a generation error.

### NanoNQ:test826 (where the 3/5 compromise is stated)
- Q1: yes. C P1 `doc29757`; answer Article 1, Section 2, Clause 3.
- Q2a/b: yes/yes. PN1 P2 is a copy of `doc29757`.
- Q3: yes.
- Q4: **no**. PN1 survivor P4 `doc101561`: "Article I, Section 2, Clause 3, commonly known as the Three-Fifths Compromise".
- Q5: no. Filtered answer still correct.
- Q6: yes. BN1 filtered answer correct.
- Strict: **not event**. Alternative support survives.

---