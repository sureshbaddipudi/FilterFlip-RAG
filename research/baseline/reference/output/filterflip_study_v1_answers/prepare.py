"""Freeze every paired request and derive tokenizer assets from the local GGUF metadata."""
from collections import Counter
from datetime import datetime,timezone
import json
from run_answers import *

def main():
    if (HERE/'FROZEN_MANIFEST.json').exists():raise FileExistsError('Generation plan already frozen')
    ident=identity();show=api('show',{'model':MODEL,'verbose':True});mi=show['model_info']
    if mi['tokenizer.ggml.pre']!='qwen2' or mi['tokenizer.ggml.add_bos_token'] is not False:raise ValueError('Unexpected tokenizer')
    tokens=mi['tokenizer.ggml.tokens'];merges=mi['tokenizer.ggml.merges']
    if len(tokens)!=len(set(tokens)):raise ValueError('Token vocabulary contains repeated strings')
    (HERE/'tokenizer').mkdir(exist_ok=True)
    save(HERE/'tokenizer/vocab.json',{t:i for i,t in enumerate(tokens)})
    (HERE/'tokenizer/merges.txt').write_text('#version: 0.2\n'+'\n'.join(merges)+'\n')
    save(HERE/'model_setup.json',dict(**ident,template=show['template'],template_sha256=digest(show['template'].encode()),
        options=OPTIONS,system_prompt=SYSTEM,tokenizer_source='Existing Ollama /api/show verbose metadata; no download',
        tokenizer_vocab_size=len(tokens),tokenizer_merge_count=len(merges),model_details=show['details']))
    tokenizer=load_tokenizer()
    for token in ['<|im_start|>','<|im_end|>']:
        assert tokenizer.encode(token,add_special_tokens=False)==[tokens.index(token)]
    # One bounded synthetic check of local tokenizer/template accounting, not a study outcome.
    probe=request('What colour is the box?',[{'text':'The box is blue.'}])
    estimate=len(tokenizer.encode(rendered_prompt(probe),add_special_tokens=False))
    response=api('chat',probe)
    save(HERE/'tokenizer_probe.json',dict(request=probe,estimated_prompt_tokens=estimate,response=response))
    if response_status(response,estimate)!='ok':raise ValueError('Tokenizer/template probe mismatch')
    plan=json.loads((RETRIEVAL/'case_manifest.json').read_text());cases={c['case_id']:c for c in plan['cases']}
    results=rows(FILTER/'results/filter_run1/results.jsonl');by={(r['case_id'],r['condition']):r for r in results}
    if len(results)!=531 or any(r['status']!='ok' for r in results):raise ValueError('Incomplete filter stage')
    calls=[];first={}
    # Primary+control block for every question first, then all secondary conditions.
    for block in [CONDITIONS[:3],CONDITIONS[3:]]:
        for cid,c in cases.items():
            for co in block:
                r=by[cid,co]
                for mode in ['unfiltered','filtered']:
                    docs=r['retrieved'] if mode=='unfiltered' else [r['retrieved'][i] for i in r['kept_indices']]
                    req=request(c['question'],docs);key=digest(canonical(req))
                    count=len(tokenizer.encode(rendered_prompt(req),add_special_tokens=False))
                    if count+OPTIONS['num_predict']+64>OPTIONS['num_ctx']:raise ValueError('Prompt budget overflow: '+cid)
                    call_id=f'{cid}__{co}__{mode}'
                    calls.append(dict(call_id=call_id,case_id=cid,condition=co,mode=mode,
                        question=c['question'],expected_answer=c['expected_answer'],source_qualification=c['source_qualification'],
                        source_review_status=c['review_status'],context_support='UNREVIEWED_FOR_THIS_CALL',
                        chunk_ids=[d['chunk_id'] for d in docs],text_hashes=[d['text_sha256'] for d in docs],
                        request=req,request_sha256=key,estimated_prompt_tokens=count,identical_request_to=first.get(key)))
                    first.setdefault(key,call_id)
    assert len(calls)==1062
    with (HERE/'calls.jsonl').open('w') as f:
        for call in calls:f.write(json.dumps(call,ensure_ascii=False)+'\n')
    record=dict(created_utc=datetime.now(timezone.utc).isoformat(),status='frozen_before_study_generation',
        question_count=59,logical_conditions=len(calls),unique_requests=len(first),
        max_estimated_prompt_tokens=max(c['estimated_prompt_tokens'] for c in calls),
        files={n:sha(HERE/n) for n in ['run_answers.py','prepare.py','test_answers.py','PROTOCOL.md','calls.jsonl','model_setup.json','tokenizer_probe.json','tokenizer/vocab.json','tokenizer/merges.txt']},
        retrieval_inputs={n:sha(RETRIEVAL/n) for n in ['case_manifest.json','support_labels_snapshot.json']},
        filter_inputs={n:sha(FILTER/n) for n in ['results/filter_run1/results.jsonl','results/filter_run1/RESULT_MANIFEST.json','SEMANTIC_REVIEW.json','FROZEN_MANIFEST.json']},
        template_sha256=digest(show['template'].encode()))
    save(HERE/'FROZEN_MANIFEST.json',record)
    print(json.dumps({k:record[k] for k in ['logical_conditions','unique_requests','max_estimated_prompt_tokens']},indent=2))

if __name__=='__main__':main()
