"""Readable interpretation of audited order results; semantic claims are narrowly scoped."""
import json
from pathlib import Path
from collections import defaultdict
from run_order_check import HERE,rows,save,sha

def main():
 out=HERE/'results/run1'
 validation=json.loads((HERE/'VALIDATION.json').read_text());assert validation['status']=='passed'
 s=json.loads((out/'summary.json').read_text());rr=rows(out/'results.jsonl')
 grouped=defaultdict(list)
 for r in rr:grouped[r['group'],r['case_id'],r['condition']].append(r)
 frozen=[];tied=[]
 for (g,cid,co),r in grouped.items():
  record=dict(case_id=cid,condition=co,orders=len(r),distinct_kept_sets=len({tuple(sorted(x['kept_chunk_ids'])) for x in r}),
      quote_states=sorted({x['after']['quote_present'] for x in r}),source_copy_states=sorted({x['after']['source_or_copy_present'] for x in r}),
      source_copy_retained=sum(x['after']['source_or_copy_present'] for x in r),
      quote_retained=sum(x['after']['quote_present'] for x in r))
  (frozen if g=='frozen_12_three_orders' else tied).append(record)
 changed=[r for r in frozen if r['distinct_kept_sets']>1]
 indicator_changed=[r for r in frozen if len(r['quote_states'])>1 or len(r['source_copy_states'])>1]
 data=dict(status='assistant_interpretation_of_audited_filter_only_results',native_calls=s['completed'],canonical_matches=s['canonical_matches'],
    frozen_sample=dict(questions=12,contexts=36,orders_per_context=3,kept_set_changes=len(changed),quote_or_source_state_changes=len(indicator_changed),changed_contexts=changed),
    tied_diagnostic=dict(questions=2,contexts=6,orders_per_context=120,records=tied,
      semantic_qualification='Assistant inspected all five possible passages in C, BN1 and PN1 for these two questions. Only the target source or its copy supplies the requested filming location/archived office-number relation. Thus source/copy presence tracks that relation within these six fixed context sets. This equivalence is not assumed for other questions.'),
    generator_reexecuted=False,primary_rates_changed=False,human_verified=False,
    input_hashes={'results/run1/results.jsonl':sha(out/'results.jsonl'),'FROZEN_MANIFEST.json':sha(HERE/'FROZEN_MANIFEST.json')})
 save(HERE/'ORDER_REVIEW.json',data)
 lines=['# FilterFlip: passage-order check results','',
   f'**Completed {s["completed"]}/828 native filter calls with {s["faults"]} faults. All {s["canonical_matches"]}/42 original-order comparisons reproduced their saved survivor sets.**','',
   'The corpus, retrieved context membership, model checkpoint and filter settings were unchanged. Only the input order of the same five passages changed. No new generator calls were made. Reusing a previous answer for a reordered prompt would not be valid.','',
   '## Frozen secondary sample','',
   f'The 12 questions selected before primary outcomes were each checked in clean (C), background-copy control (BN1), and correct-source-copy (PN1) conditions. Canonical, reverse and rotate-by-two orders give 108 calls across 36 contexts. {len(changed)} contexts change which documents survive; {len(indicator_changed)} change source/copy or exact-quote retention. These counts are context-level repeated diagnostics, not independent attack samples.','',
   '| Case | Condition | Survivor-set variants | Source/copy retention states |','|---|---|---|---|']
 for r in changed:lines.append(f'| {r["case_id"]} | {r["condition"]} | {r["distinct_kept_sets"]} | {r["source_copy_states"]} |')
 lines+=['', 'The differing retention case is a prompt for semantic review, not automatically an induced failure. Three orders are a limited sensitivity check, not exhaustive invariance. The exact three permutations were fixed before this diagnostic but after primary outcomes; only the case subset and general order-check intention were frozen before primary outcomes.','',
   '## Exhaustive diagnostics for the two tied cases','',
   'These two cases were selected after their primary outcomes specifically because they had clean-filter boundary ties. Their results are reported separately from the frozen sample. All 120 orders of each saved five-passage context were tested; the three conditions therefore require 720 calls.','',
   '| Case | Condition | Orders tested | Orders retaining answer source/copy | Distinct survivor sets |','|---|---|---:|---:|---:|']
 for r in tied:lines.append(f'| {r["case_id"]} | {r["condition"]} | {r["orders"]} | {r["source_copy_retained"]} | {r["distinct_kept_sets"]} |')
 by={(r['case_id'],r['condition']):r for r in tied}
 robust=all(by[cid,co]['source_copy_retained']==(0 if co=='PN1' else 120) for cid in ['NanoNQ:test929','NanoMSMARCO:1092161'] for co in ['C','BN1','PN1'])
 if robust:
  lines+=['', '**For both tied cases, every clean/control order retained the answer evidence and every PN1 order lost it.** The clean tie sometimes changes which irrelevant passage is removed. It does not change the evidence-retention contrast in these fixed contexts.','',
    'This strengthens the filter-stage interpretation of the Woody Woodpecker and Northampton examples: their evidence loss is not an artifact of the single original input order. It does not establish that the LLM will give the same response under every order.']
 else:lines+=['', 'The full table includes all observed retention changes; do not describe these cases as order-invariant without accounting for every condition.']
 heather=[r for r in frozen if r['case_id']=='NanoNQ:test1009']
 heather_stable=len(heather)==3 and all(r['source_copy_retained']==(0 if r['condition']=='PN1' else 3) for r in heather)
 lines+=['', '## Scope of the conclusion','',
   ('- Heather actor: all three tested clean/control orders retain the answer source, while all three PN1 orders remove the source and copy. This is not a 120-order check.' if heather_stable else '- Heather actor belongs to the frozen sample; inspect its three-order results in the machine-readable records. This is not a 120-order check.'),
   '- Bald-eagle genus is not in either selected group, so this stage establishes no order-robustness result for it.',
   '- Five-passage permutations do not test a different corpus, retrieval model, filter model, top-k, paraphrase attack or another generator.',
   '- The diagnostic cannot settle answer-completeness disputes in the eight unresolved primary cases. The conservative primary assessment remains 4 assistant-confirmed recorded events, 47 comparisons not satisfying the strict endpoint, and 8 requiring adjudication.',
   '- For the two tied cases only, every possible passage was semantically inspected: other passages discuss unrelated box office, voice actors or other telephone services. Source/copy retention therefore tracks the requested relation in these fixed contexts. This was assistant review, not independent human ground truth.','',
   '## Next step','',
   'Preserve these results and proceed to the next frozen-subset generality check. A second generator would test whether the answer-level failure depends on Qwen2.5:3b; a second filter/configuration would test a different boundary. Neither should be claimed complete from this experiment. Any extra successful-example demo rerun should be labeled demonstrative rather than an independent prevalence result.','',
   'Audit: VALIDATION.json. Full per-order decisions and score traces: results/run1/results.jsonl. Plan and input hashes: FROZEN_MANIFEST.json. No earlier results were overwritten.']
 (HERE/'ORDER_CHECK_REVIEW.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps(dict(frozen_kept_set_changes=len(changed),frozen_retention_state_changes=len(indicator_changed),two_tied_cases_have_invariant_evidence_contrast=robust,heather_three_order_results=heather),indent=2))

if __name__=='__main__':main()
