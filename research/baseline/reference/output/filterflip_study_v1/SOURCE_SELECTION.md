# Baseline source selection and eligibility

Sections 1–3 of the September 2026 study protocol, reproduced as recorded. The pending counts below describe the initial screening stage.

## 1. Source decision and scope amendment

Use the publisher-provided **NanoNQ and NanoMSMARCO** releases, pinned to the revisions in `sources/acquisition.json`:

| Collection | Documents | Questions | Positive relevance pairs | Prior-overlap exclusions | Pending source review |
|---|---:|---:|---:|---:|---:|
| NanoNQ | 5,035 | 50 | 57 | 1 | 49 |
| NanoMSMARCO | 5,043 | 50 | 50 | 0 | 50 |

These are two separate retrieval corpora, **not one 10,078-document retrieval pool**. Source pages: [NanoNQ](https://huggingface.co/datasets/zeta-alpha-ai/NanoNQ), [NanoMSMARCO](https://huggingface.co/datasets/zeta-alpha-ai/NanoMSMARCO). Their dataset cards label the files `train`; we use them as an evaluation subset by explicit study design, not as an official test split. The cards advertise CC BY 4.0; original cards and source links are preserved.

**Amendment made before outcomes:** the preceding research-scope document proposed 100 new questions and 10,000–50,000 chunks. For the first locked study, use all candidates from these public compact releases instead of assembling a private outcome-selected sample. This provides 100 candidates before exclusions and 99 after prior-overlap screening; the final number depends on source eligibility. The corpus sizes above refer to documents; chunk counts will be recorded later. This is a compact evaluation, not full BEIR, and does not establish publication-scale generality. Wider/harder corpora remain a later extension. We do not choose replacement questions to restore a round denominator.

Relevance pairs do **not** supply complete QA answers or prove single-hop support. Human/assistant source review must establish an answer and an exact supporting quotation. Incomplete relevance labels also cannot prove that other corpus passages lack support.

## 2. Prior exposure and leakage screening

The conservative prior catalog contains 200 distinct normalized questions and 229 distinct reference/chunk texts from both author-artifact collections, previous plans and the two earlier indexed corpora. This excludes more than the successful pilot cases.

Text normalization: Unicode NFKC, case-folding, word extraction and whitespace joining. Exclude a candidate for normalized question equality or any qrel source matching a prior text by normalized equality, or at least ten common five-word shingles with Jaccard >= 0.8 or shorter-text containment >= 0.8. Also group new cases sharing near-duplicate qrel sources or the same normalized question; propagate prior-overlap exclusion through such a group. Record all matches, not only the first.

Observed overlap: `NanoNQ:test31`, the Saint Peter question, matches earlier work. No additional new-case family links were found under the lexical rule. This does not establish semantic/entity independence: canonical article URLs are absent from these exports. Reviewers must flag obvious shared-source families missed by text screening before sealing labels. Old material may remain as background corpus documents; the claim is new target questions/sources under the stated screen, not an entirely unseen corpus or absence from model training.

## 3. Eligibility review, before outcomes

An eligible question must have a clear source-relative factual answer supported by a single supplied qrel document. Preserve historical dates, ambiguity and qualifications rather than silently changing the question. A disputed or qualified claim can be included only if the answer rubric retains the qualification. Exclude open-ended/list-heavy questions requiring an unsuitable rubric, missing support, unresolved ambiguity or genuinely multi-hop evidence under this single-hop scope. Record the reason.

For each candidate record reviewer, decision, chosen document ID, answer, aliases, exact support quote and source qualification. If multiple documents independently support it, choose the lexicographically smallest eligible document ID as the insertion source; retain the others as possible supporting evidence. Record any departure with a source-based reason before evaluation. Do not select the source by retrieval score or filter outcome.

Assistant drafts are permitted and must be attributed as such. They are not independent human validation. Both teammates should independently review decisive outcome cases and a preselected sample of non-events later; initial labels can be prepared in batches now. Freeze all initial eligibility decisions before the first primary filter/generation outcome. Excluded cases remain in the source-screening denominator; all eligible cases remain in the experiment denominator even if retrieval later fails.
