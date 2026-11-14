"""Audit saved calls and emit readable contexts; never rerun filtering."""
from run_config import *

def main():
    verify();out=HERE/'results/run1';rr=rows(out/'results.jsonl')
    manifest=json.loads((out/'RESULT_MANIFEST.json').read_text())
    for n,h in manifest['files'].items():assert sha(out/n)==h,n
    assert sha(out/'frozen_manifest.json')==sha(HERE/'FROZEN_MANIFEST.json')
    recovery=json.loads((out/'recovery.json').read_text())
    prefix=(out/'results_before_resume.jsonl').read_bytes()
    assert (out/'results.jsonl').read_bytes().startswith(prefix)
    assert sha(out/'results_before_resume.jsonl')==recovery['saved_prefix_sha256']
    assert sha(out/'original_frozen_manifest.json')==recovery['original_manifest_sha256']
    assert sha(out/'runner_before_reporting_fix.py')==recovery['old_runner_sha256']
    plan=json.loads((HERE/'plan.json').read_text())
    expected=[(a['name'],c,co) for a in ARMS for c in plan['case_ids'] for co in CONDITIONS]
    assert [(r['arm'],r['case_id'],r['condition']) for r in rr]==expected and len(rr)==108
    saved={(r['case_id'],r['condition']):r for r in rows(INPUT)}
    cases={r['case_id']:r for r in json.loads(PLAN.read_text())['cases']}
    audits={a['name']:json.loads((out/(a['name']+'_token_audit.json')).read_text()) for a in ARMS}
    for r in rr:
        c=cases[r['case_id']];old=saved[r['case_id'],r['condition']];docs=r['retrieved']
        assert r['status']=='ok' and r['retrieved']==old['retrieved'] and r['question']==old['question']
        assert sorted(r['kept_indices']+r['removed_indices'])==list(range(5))
        assert not set(r['kept_indices']) & set(r['removed_indices'])
        assert r['kept_chunk_ids']==[docs[i]['chunk_id'] for i in r['kept_indices']]
        assert r['before']==base.metrics(docs,c['target_document_id'],c['support_quote'])
        assert r['after']==base.metrics([docs[i] for i in r['kept_indices']],c['target_document_id'],c['support_quote'])
        assert r['trace']['matches_native_removals'] and r['synthetic_wrapper_check']
        if r['arm']=='all_256':assert r['removed_indices']==old['removed_indices'] and r['baseline_match'] is True
        audit=audits[r['arm']];assert audit['window']==r['window']
        assert r['any_truncated']==any(audit['entries'][d['text_sha256']]['truncated'] for d in docs)
        for d in docs:
            e=audit['entries'][d['text_sha256']]
            assert e['used_count']==len(e['used_ids'])==min(r['window'],e['full_count'])
            assert e['truncated']==(e['full_count']>r['window'])
    save(HERE/'VALIDATION.json',dict(status='passed',native_calls=108,original_decisions_reproduced=36,
        questions=12,unchanged_ordered_contexts=True,all_result_manifest_hashes_verified=True,
        model_and_runner_hashes_verified=True,source_quote_metrics_recomputed=True,
        no_retrieval_or_generator_calls=True,reporting_error_recovered=True,first_saved_result_preserved=True,
        scope='Execution and screening audit; not complete semantic-support validation.'))
    lines=['# Saved contexts for configuration review','',
        'Assistant review material. Source/quote indicators are not complete semantic support. No new generator calls.','']
    for cid in plan['case_ids']:
        case=cases[cid];lines+=['## '+cid,'','Question: '+case['question'],'Expected: '+case['expected_answer'],'Qualification: '+case['source_qualification'],'']
        for co in CONDITIONS:
            old=saved[cid,co];related=[r for r in rr if r['case_id']==cid and r['condition']==co]
            lines+=['### '+co,'']
            for i,d in enumerate(old['retrieved']):
                states='; '.join(r['arm']+': '+('KEPT' if i in r['kept_indices'] else 'REMOVED') for r in related)
                lines+=['**'+d['record_id']+' — '+states+'**','',d['text'],'']
    (HERE/'CONTEXT_REVIEW.md').write_text('\n'.join(lines)+'\n')
    print((HERE/'VALIDATION.json').read_text())

if __name__=='__main__':main()
