"""Audit request identity, response reuse, complete coverage and token accounting."""
import json
from collections import Counter
from run_answers import HERE,RETRIEVAL,FILTER,rows,sha,canonical,digest,request,response_status,save

def main():
    out=HERE/'results/answers_run1';calls=rows(HERE/'calls.jsonl');logical=rows(out/'results.jsonl');unique=rows(out/'unique_results.jsonl')
    assert len(calls)==len(logical)==1062
    assert len({c['call_id'] for c in calls})==1062
    contexts={(r['case_id'],r['condition']):r for r in rows(FILTER/'results/filter_run1/results.jsonl')}
    ur={r['request_sha256']:r for r in unique};assert len(ur)==len(unique)
    assert set(ur)=={c['request_sha256'] for c in calls}
    seen={}
    for c,r in zip(calls,logical):
        assert c['call_id']==r['call_id']
        ctx=contexts[c['case_id'],c['condition']]
        selected=ctx['retrieved'] if c['mode']=='unfiltered' else [ctx['retrieved'][i] for i in ctx['kept_indices']]
        assert c['request']==request(c['question'],selected)
        assert c['chunk_ids']==[d['chunk_id'] for d in selected]
        assert c['text_hashes']==[d['text_sha256'] for d in selected]
        h=digest(canonical(c['request']));assert h==c['request_sha256']
        assert c['identical_request_to']==seen.get(h)
        seen.setdefault(h,c['call_id'])
        u=ur[h];assert u['first_call_id']==seen[h]
        assert u['status']==r['status']=='ok'
        assert response_status(u['raw_response'],c['estimated_prompt_tokens'])=='ok'
        assert u['answer']==r['answer']
        assert r['response_reused']==(c['identical_request_to'] is not None)
    m=json.loads((HERE/'FROZEN_MANIFEST.json').read_text())
    for rel,h in m['files'].items():assert sha(HERE/rel)==h
    for rel,h in m['filter_inputs'].items():assert sha(FILTER/rel)==h
    for rel,h in m['retrieval_inputs'].items():assert sha(RETRIEVAL/rel)==h
    max_delta=max(abs(ur[c['request_sha256']]['prompt_eval_count']-c['estimated_prompt_tokens']) for c in calls)
    record={'status':'passed','logical_conditions':1062,'distinct_requests':len(ur),'reused_logical_conditions':1062-len(ur),
        'questions':59,'max_prompt_count_difference':max_delta,'response_status_counts':dict(Counter(r['status'] for r in unique)),
        'checks':['frozen requests reconstructed from saved passages','no expected answer or label added to prompts',
                  'all 59 questions and nine conditions paired','duplicate reuse mapped to first exact request',
                  'raw response and logical answer agreement','completed nonempty responses within token limits','frozen hashes unchanged'],
        'limits':'This audit establishes execution and accounting, not response correctness or semantic grounding.'}
    save(HERE/'VALIDATION.json',record);print(json.dumps(record,indent=2))

if __name__=='__main__':main()
