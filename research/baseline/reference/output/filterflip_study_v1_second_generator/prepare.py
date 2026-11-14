"""Prepare local tokenizer and freeze second-model requests before study generation."""
from datetime import datetime,timezone
from run_second import *

def main():
    if (HERE/'FROZEN_MANIFEST.json').exists():raise FileExistsError('Already frozen')
    ident=identity();show=api('show',{'model':MODEL,'verbose':True});mi=show['model_info']
    save(HERE/'model_show_verbose.json',show)
    assert mi['tokenizer.ggml.pre']=='llama-bpe',mi.get('tokenizer.ggml.pre')
    assert mi['tokenizer.ggml.model']=='gpt2'
    tokens=mi['tokenizer.ggml.tokens'];merges=[tuple(x.split(' ')) for x in mi['tokenizer.ggml.merges']]
    assert len(tokens)==len(set(tokens)) and all(len(x)==2 for x in merges)
    from tokenizers import Tokenizer,AddedToken,Regex,pre_tokenizers,decoders
    from tokenizers.models import BPE
    tokenizer=Tokenizer(BPE({t:i for i,t in enumerate(tokens)},merges,fuse_unk=False,ignore_merges=True))
    tokenizer.pre_tokenizer=pre_tokenizers.Sequence([pre_tokenizers.Split(Regex(PATTERN),behavior='isolated',invert=False),pre_tokenizers.ByteLevel(add_prefix_space=False,use_regex=False)])
    tokenizer.decoder=decoders.ByteLevel()
    special=[t for t in tokens if t.startswith('<|') and t.endswith('|>')]
    tokenizer.add_special_tokens([AddedToken(t,normalized=False,special=True) for t in special])
    for t in ['<|begin_of_text|>','<|start_header_id|>','<|end_header_id|>','<|eot_id|>']:
        assert tokenizer.encode(t,add_special_tokens=False).ids==[tokens.index(t)]
    tokenizer.save(str(HERE/'tokenizer.json'))
    setup=dict(**ident,template=show['template'],template_sha256=digest(show['template'].encode()),parameters=show.get('parameters'),model_details=show['details'],options=OPTIONS,
        tokenizer_pre=mi['tokenizer.ggml.pre'],add_bos_token=mi.get('tokenizer.ggml.add_bos_token'),tokenizer_implementation='tokenizers BPE with GGUF vocab/merges, Meta Llama3 regex and byte-level transform; no normalization; BOS included in rendered prompt',
        sources=['https://ollama.com/library/llama3.2:3b','https://raw.githubusercontent.com/meta-llama/llama3/main/llama/tokenizer.py'])
    save(HERE/'model_setup.json',setup)
    # All are synthetic tokenizer checks, not study outcomes. Never overwrite a prior attempt.
    probes=[('colour','The box is blue.','What colour is the box?'),
            ('digits','The synthetic code is 1234567890. Its label is blue.','What is the label?'),
            ('unicode','Élodie writes café, λευκος, and ₹500. The label is blue.','What is the label?')]
    for name,text,question in probes:
        path=HERE/f'probe_{name}.json'
        if path.exists():
            rec=json.loads(path.read_text());assert rec['status']=='ok';continue
        req=primary.request(question,[{'text':text}]);req['model']=MODEL
        count=len(tokenizer.encode(rendered(req),add_special_tokens=False).ids)
        response=api('chat',req);status=response_status(response,count)
        save(path,dict(request=req,rendered_prompt=rendered(req),estimated_prompt_tokens=count,raw_response=response,status=status))
        print(name,'estimated',count,'server',response.get('prompt_eval_count'),'status',status,flush=True)
        if status!='ok':raise ValueError('Synthetic tokenizer probe mismatch; preserve and inspect before study calls')
    manifest=json.loads((primary.RETRIEVAL/'case_manifest.json').read_text());ids=manifest['secondary_case_ids']
    original={(c['case_id'],c['condition'],c['mode']):c for c in rows(FIRST/'calls.jsonl')}
    saved={r['request_sha256']:r for r in rows(FIRST/'results/answers_run1/unique_results.jsonl')}
    calls=[];seen={}
    for cid in ids:
        for co in ['C','BN1','PN1']:
            for mode in ['unfiltered','filtered']:
                old=original[cid,co,mode];c={k:v for k,v in old.items() if k not in ['request','request_sha256','estimated_prompt_tokens','identical_request_to']}
                req=json.loads(json.dumps(old['request']));req['model']=MODEL
                assert req['messages']==old['request']['messages'] and req['options']==OPTIONS
                count=len(tokenizer.encode(rendered(req),add_special_tokens=False).ids)
                assert count+128+64<=4096
                key=digest(canonical(req));baseline=saved[old['request_sha256']];assert baseline['status']=='ok'
                c.update(request=req,request_sha256=key,estimated_prompt_tokens=count,identical_request_to=seen.get(key),
                    baseline_request_sha256=old['request_sha256'],baseline_model=primary.MODEL,baseline_answer=baseline['answer'])
                seen.setdefault(key,c['call_id']);calls.append(c)
    assert len(calls)==72 and len(seen)==66
    with (HERE/'calls.jsonl').open('w') as f:
        for r in calls:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    names=['run_second.py','prepare.py','PROTOCOL.md','tokenizer.json','model_setup.json','model_show_verbose.json','probe_colour.json','probe_digits.json','probe_unicode.json','calls.jsonl']
    inputs=[primary.RETRIEVAL/'case_manifest.json',primary.FILTER/'results/filter_run1/results.jsonl',FIRST/'calls.jsonl',FIRST/'results/answers_run1/unique_results.jsonl',FIRST/'run_answers.py']
    save(HERE/'FROZEN_MANIFEST.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),stage='frozen_before_second_model_study_calls',model_digest=ident['model']['digest'],template_sha256=setup['template_sha256'],case_ids=ids,
      max_prompt_tokens=max(c['estimated_prompt_tokens'] for c in calls),logical_calls=72,distinct_requests=66,
      files={n:sha(HERE/n) for n in names},inputs={str(p.relative_to(HERE.parent)):sha(p) for p in inputs}))
    print('Frozen 72 logical / 66 distinct requests. Maximum prompt tokens:',max(c['estimated_prompt_tokens'] for c in calls),flush=True)

if __name__=='__main__':main()
