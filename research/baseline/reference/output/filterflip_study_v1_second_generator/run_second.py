"""Second generator on the frozen twelve-question subset; no new retrieval/filter calls."""
import sys,json,time,hashlib,argparse
from pathlib import Path
from collections import Counter
HERE=Path(__file__).resolve().parent
FIRST=HERE.parent/'filterflip_study_v1_answers'
sys.path.insert(0,str(FIRST))
import run_answers as primary
MODEL='llama3.2:3b'
OPTIONS=primary.OPTIONS.copy()
api=primary.api
rows=primary.rows
sha=primary.sha
save=primary.save
canonical=primary.canonical
digest=primary.digest
PATTERN=r"(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\r\n\p{L}\p{N}]?\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+"

def rendered(req):
    system,user=req['messages']
    assert system['role']=='system' and user['role']=='user'
    return ('<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n'
       'Cutting Knowledge Date: December 2023\n\n'+system['content']+'<|eot_id|>'
       '<|start_header_id|>user<|end_header_id|>\n\n'+user['content']+'<|eot_id|>'
       '<|start_header_id|>assistant<|end_header_id|>\n\n')

def identity():
    version=api('version');tags=api('tags');matches=[m for m in tags['models'] if m['name']==MODEL]
    assert version=={'version':'0.34.2'} and len(matches)==1
    return dict(ollama=version,model=matches[0])

def response_status(r,estimate):
    if r.get('done') is not True or not isinstance(r.get('message',{}).get('content'),str):return 'malformed'
    if not r['message']['content'].strip():return 'empty'
    if r.get('done_reason')=='length':return 'truncated'
    if r.get('prompt_eval_count')!=estimate:return 'token_count_review_needed'
    if estimate+OPTIONS['num_predict']+64>OPTIONS['num_ctx']:return 'context_window_review_needed'
    return 'ok'

def verify():
    m=json.loads((HERE/'FROZEN_MANIFEST.json').read_text())
    for n,h in m['files'].items():assert sha(HERE/n)==h,n
    for n,h in m['inputs'].items():assert sha(HERE.parent/n)==h,n
    ident=identity();assert ident['model']['digest']==m['model_digest']
    assert digest(api('show',{'model':MODEL})['template'].encode())==m['template_sha256']
    return m

def output(calls,unique,out):
    expanded=[]
    for c in calls:
        r=unique.get(c['request_sha256']);row={k:v for k,v in c.items() if k!='request'}
        if r:row.update(status=r['status'],answer=r.get('answer'),response_reused=c['identical_request_to'] is not None)
        else:row.update(status='pending',answer=None,response_reused=c['identical_request_to'] is not None)
        expanded.append(row)
    with (out/'results.jsonl').open('w') as f:
        for r in expanded:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    s=dict(planned_logical=72,planned_distinct=66,saved_distinct=len(unique),logical_status_counts=dict(Counter(r['status'] for r in expanded)),distinct_status_counts=dict(Counter(r['status'] for r in unique.values())),note='API completion does not establish correct or grounded answers. Fixed twelve-question subset; no primary success-rate replacement.')
    save(out/'summary.json',s)
    return s

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');a=parser.parse_args()
    manifest=verify();calls=rows(HERE/'calls.jsonl');out=HERE/'results/run1'
    if out.exists() and not a.resume:raise FileExistsError('Existing run: preserve it')
    out.mkdir(parents=True,exist_ok=a.resume)
    if not (out/'frozen_manifest.json').exists():(out/'frozen_manifest.json').write_bytes((HERE/'FROZEN_MANIFEST.json').read_bytes())
    assert sha(out/'frozen_manifest.json')==sha(HERE/'FROZEN_MANIFEST.json')
    pending=out/'PENDING_REQUEST.json'
    if pending.exists():raise RuntimeError('Uncertain interrupted attempt: manual review required')
    unique={r['request_sha256']:r for r in rows(out/'unique_results.jsonl')} if (out/'unique_results.jsonl').exists() else {}
    if any(r['status']!='ok' for r in unique.values()):raise RuntimeError('Non-ok saved response: manual review required')
    if not (out/'identity_start.json').exists():save(out/'identity_start.json',identity())
    seen=set();work=[]
    for c in calls:
        if c['request_sha256'] not in seen:work.append(c);seen.add(c['request_sha256'])
    assert len(calls)==72 and len(work)==66
    print('72 logical comparisons; 66 distinct requests; '+str(len(unique))+' saved.',flush=True)
    with (out/'unique_results.jsonl').open('a') as f:
        for n,c in enumerate(work,1):
            h=c['request_sha256']
            if h in unique:continue
            save(pending,dict(request_sha256=h,first_call_id=c['call_id'],started_unix=time.time()))
            t=time.perf_counter();r=dict(request_sha256=h,first_call_id=c['call_id'])
            try:
                res=api('chat',c['request']);r.update(status=response_status(res,c['estimated_prompt_tokens']),answer=res.get('message',{}).get('content'),raw_response=res,wall_seconds=time.perf_counter()-t)
            except Exception as e:r.update(status='fault',answer=None,error=repr(e),wall_seconds=time.perf_counter()-t)
            f.write(json.dumps(r,ensure_ascii=False)+'\n');f.flush();unique[h]=r;pending.unlink()
            output(calls,unique,out)
            print(f'[{n}/66] {c["call_id"]}: {r["status"]} ({r["wall_seconds"]:.1f}s)',flush=True)
            if r['status']!='ok':raise RuntimeError('Non-ok response preserved; stop without retry')
    save(out/'identity_end.json',identity())
    save(out/'RESULT_MANIFEST.json',{'files':{p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='RESULT_MANIFEST.json'}})
    print('Complete.',flush=True)

if __name__=='__main__':main()
