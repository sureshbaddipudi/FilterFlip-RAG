"""Audit second-model request reconstruction and paired first-model identities."""
from run_second import *

def main():
    out=HERE/'results/run1';calls=rows(HERE/'calls.jsonl');logical=rows(out/'results.jsonl');u=rows(out/'unique_results.jsonl')
    assert len(calls)==len(logical)==72 and len(u)==66
    unique={r['request_sha256']:r for r in u};assert len(unique)==66
    m=json.loads((HERE/'FROZEN_MANIFEST.json').read_text())
    for n,h in m['files'].items():assert sha(HERE/n)==h
    for n,h in m['inputs'].items():assert sha(HERE.parent/n)==h
    for n in ['identity_start.json','identity_end.json']:
        ident=json.loads((out/n).read_text());assert ident['model']['digest']==m['model_digest'] and ident['ollama']=={'version':'0.34.2'}
    original={c['call_id']:c for c in rows(FIRST/'calls.jsonl')}
    seen={}
    for c,r in zip(calls,logical):
        assert c['call_id']==r['call_id']
        old=original[c['call_id']];req={**old['request'],'model':MODEL}
        assert c['request']==req
        assert c['chunk_ids']==old['chunk_ids'] and c['text_hashes']==old['text_hashes']
        assert c['baseline_request_sha256']==old['request_sha256']
        h=digest(canonical(req));assert h==c['request_sha256']
        assert c['identical_request_to']==seen.get(h);seen.setdefault(h,c['call_id'])
        record=unique[h];assert record['first_call_id']==seen[h]
        assert record['status']==r['status']=='ok' and record['answer']==r['answer']
        assert response_status(record['raw_response'],c['estimated_prompt_tokens'])=='ok'
    assert set(c['case_id'] for c in calls)==set(m['case_ids']) and len(m['case_ids'])==12
    save(HERE/'VALIDATION.json',dict(status='passed',logical_conditions=72,distinct_requests=66,questions=12,reused_logical_conditions=6,
        inputs_unchanged_except_model=True,exact_server_token_counts=True,within_context_window=True,frozen_hashes_unchanged=True,
        scope='Execution/request audit only; correctness and support remain manual judgments.'))
    lines=['# Second-model paired answers: frozen 12-question subset','',
      'Same saved canonical contexts and messages; different local model packages and native templates. No new retrieval/filter calls. All source qualifications remain applicable. API status ok is not correctness.','']
    for cid in m['case_ids']:
        rr=[r for r in logical if r['case_id']==cid];c=rr[0]
        lines += ['## '+cid,'','**Question:** '+c['question'],'**Expected:** '+c['expected_answer'],'**Qualification:** '+c['source_qualification'],'',
          '| Condition | Mode | Qwen2.5:3b saved answer | Llama3.2:3b answer |','|---|---|---|---|']
        for r in rr:
            clean=lambda x:x.replace('|','\\|').replace('\n',' ')
            lines.append(f'| {r["condition"]} | {r["mode"]} | {clean(r["baseline_answer"])} | {clean(r["answer"])} |')
        lines.append('')
    (HERE/'PAIRED_MODEL_ANSWERS.md').write_text('\n'.join(lines)+'\n')
    print((HERE/'VALIDATION.json').read_text())

if __name__=='__main__':main()
