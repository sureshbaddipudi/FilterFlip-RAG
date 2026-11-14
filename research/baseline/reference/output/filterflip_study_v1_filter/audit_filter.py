#!/usr/bin/env python3
"""Validate saved filter accounting without re-running a model."""
import json
from pathlib import Path
from run_filter import HERE,PREV,CONDITIONS,rows,metrics,classify,save,sha

def main():
    out=HERE/'results/filter_run1'
    results=rows(out/'results.jsonl');up=rows(PREV/'results/retrieval_run1/contexts.jsonl')
    source={(r['case_id'],r['condition']):r for r in up}
    plan=json.loads((PREV/'case_manifest.json').read_text());cases={c['case_id']:c for c in plan['cases']}
    expected={(c,co) for c in cases for co in CONDITIONS}
    assert len(results)==len(expected)==531
    assert {(r['case_id'],r['condition']) for r in results}==expected
    assert all(r['status']=='ok' for r in results)
    for r in results:
        key=r['case_id'],r['condition'];c=cases[r['case_id']]
        assert r['retrieved']==source[key]['retrieved']
        assert r['review_status']==c['review_status']
        kept=r['kept_indices'];removed=r['removed_indices']
        assert sorted(kept+removed)==list(range(5)) and not set(kept)&set(removed)
        assert r['kept_chunk_ids']==[r['retrieved'][i]['chunk_id'] for i in kept]
        assert r['removed_chunk_ids']==[r['retrieved'][i]['chunk_id'] for i in removed]
        assert r['before']==metrics(r['retrieved'],c['target_document_id'],c['support_quote'])
        assert r['after']==metrics([r['retrieved'][i] for i in kept],c['target_document_id'],c['support_quote'])
        assert r['trace']['matches_native_removals'] and r['trace']['estimated_removal_count']==len(removed)
        assert r['trace']['removal_ranking']==sorted(range(5),key=lambda i:(-r['trace']['frequency_scores'][i],i))
        assert sorted(r['trace']['removal_ranking'][:len(removed)])==removed
        assert len(r['trace']['all_pairs'])==10
        assert len(r['token_counts'])==5 and max(r['token_counts'])<=256
        assert r['semantic_support']=='UNREVIEWED' and r['generation_status']=='NOT_RUN'
    summary=json.loads((out/'summary.json').read_text());lookup={(r['case_id'],r['condition']):r for r in results}
    screens=[classify({co:lookup[cid,co] for co in CONDITIONS}) for cid in cases]
    assert summary['quote_loss_candidates']==sum(s['quote_loss_candidate'] for s in screens)
    assert summary['background_qualified_candidates']==sum(s['background_qualified'] for s in screens)
    for co in CONDITIONS:
        rr=[r for r in results if r['condition']==co];v=summary['conditions'][co]
        assert v['completed']==len(rr)==59
        for when in ['before','after']:
            assert v['quote_'+when]==sum(r[when]['quote_present'] for r in rr)
            assert v['source_copy_'+when]==sum(r[when]['source_or_copy_present'] for r in rr)
    for name,digest in json.loads((out/'RESULT_MANIFEST.json').read_text())['files'].items():assert sha(out/name)==digest
    frozen=json.loads((HERE/'FROZEN_MANIFEST.json').read_text())
    for name,digest in frozen['inputs'].items():assert sha(PREV/name)==digest
    record={'status':'passed','study_calls':531,'questions':59,'native_trace_matches':531,
        'checks':['saved retrieval contexts unchanged','every planned case-condition pair present once',
                  'kept/removed index partition and duplicate-instance IDs correct','native score ranking agrees with removals',
                  'quote/source screening counts recomputed','token windows respected','input/result hashes unchanged'],
        'limits':'Semantic answer support and generation are not established by this audit.'}
    save(HERE/'VALIDATION.json',record);print(json.dumps(record,indent=2))

if __name__=='__main__':main()
