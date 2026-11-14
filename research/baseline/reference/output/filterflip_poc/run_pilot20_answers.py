#!/usr/bin/env python3
"""18 canonical-order answer calls on the first three frozen strict candidates.
Requires the earlier run_filterflip_answers.py helper beside this script.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path
from run_filterflip_answers import api, save


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(source, previous, audit_path):
    audit=json.loads(audit_path.read_text())
    for filename,expected in audit['source_hashes'].items():
        if sha(source/filename)!=expected: raise ValueError('Audited source result changed: '+filename)
    plan=json.loads((source/'frozen_plan.json').read_text())
    summary=json.loads((source/'summary.json').read_text())
    selected=[s['source_id'] for s in summary['cases'] if s['strict_candidate']][:3]
    if selected!=audit['selected_ids']: raise ValueError('Predeclared follow-up selection changed.')
    prior=json.loads((previous/'experiment.json').read_text())
    rows=[json.loads(s) for s in (source/'results.jsonl').read_text().splitlines()]
    calls=[]
    for qid in selected:
        case=next(c for c in plan['cases'] if c['id']==qid)
        for condition in ['clean','background_copy_control','target_redaction_attack']:
            record=next(r for r in rows if r['source_id']==qid and r['order']=='canonical' and r['condition']==condition)
            docs=case['conditions'][condition]
            if record['status']!='ok' or record['input_ids']!=[d['id'] for d in docs]:
                raise ValueError('Saved native filtering is incomplete or input order differs.')
            removed=record['removed_indices']
            if len(set(removed))!=len(removed) or any(type(i) is not int or i<0 or i>=len(docs) for i in removed):
                raise ValueError('Invalid saved indices.')
            kept=[d for i,d in enumerate(docs) if i not in set(removed)]
            if [d['id'] for d in kept]!=record['kept_ids']: raise ValueError('Saved indices and IDs disagree.')
            for mode,chosen in [('unfiltered',docs),('filtered',kept)]:
                call_id=f'{qid}__{condition}__{mode}'
                judgment=audit['calls'][call_id]
                hashes=[d['sha256'] for d in chosen]
                if hashes!=judgment['passage_hashes']: raise ValueError('Audited passage set differs.')
                for d in chosen:
                    if hashlib.sha256(d['text'].encode()).hexdigest()!=d['sha256']: raise ValueError('Passage content changed.')
                context='\n\n'.join(d['text'] for d in chosen)
                if len(context)>10000: raise ValueError('Unexpectedly large context.')
                calls.append(dict(call_id=call_id,source_id=qid,condition=condition,mode=mode,
                    question=case['question'],expected_answer=case['expected_answer'],
                    passage_ids=[d['id'] for d in chosen],support_judgment=judgment['support'],
                    support_review_note=judgment['reason'],context=context,
                    request={'model':prior['model']['name'],'stream':False,'options':prior['options'],
                        'messages':[{'role':'system','content':prior['system_prompt']},
                                    {'role':'user','content':f"Document:\n<document>\n{context}\n</document>\n\nQuestion: {case['question']}"}]}))
    if len(calls)!=18: raise ValueError('Expected 18 calls.')
    return prior,audit,calls


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=Path('results/filterflip_pilot20_run1'))
    parser.add_argument('--previous',type=Path,default=Path('results/filterflip_answers_run1'))
    parser.add_argument('--audit',type=Path,default=Path(__file__).with_name('pilot20_followup_audit.json'))
    parser.add_argument('--out',type=Path,default=Path('results/pilot20_answers_run1'))
    parser.add_argument('--check-only',action='store_true')
    args=parser.parse_args()
    prior,audit,calls=prepare(args.source,args.previous,args.audit)
    if args.check_only:
        print('Check passed: test19, test20, test31; canonical order; 18 paired calls.')
        print('Frozen source results and support-review passage hashes verified. No model calls made.')
        return
    if args.out.exists(): raise SystemExit('Output exists; preserve it and use a fresh --out if needed.')
    version,tags=api('version'),api('tags')
    matches=[m for m in tags.get('models',[]) if m.get('name')==prior['model']['name']]
    if version!=prior['ollama'] or len(matches)!=1 or matches[0].get('digest')!=prior['model']['digest']:
        raise SystemExit('Ollama or model changed; inspect before comparing.')
    args.out.mkdir(parents=True)
    save(args.out/'experiment.json',dict(model=matches[0],ollama=version,options=prior['options'],
        system_prompt=prior['system_prompt'],audit=audit,calls=calls,
        script_sha256=sha(Path(__file__)),
        scope='Three preselected development cases sharing a background set. No actual retrieval. Assistant-reviewed support labels; human confirmation pending. Answers may come from model memory. No generation-based reselection.'))
    for call in calls:
        folder=args.out/call['call_id']; folder.mkdir()
        save(folder/'request.json',call['request'])
        (folder/'context.txt').write_text(call['context'],encoding='utf-8')
    summary=['Pilot20 follow-up: first three strict candidates, canonical order, 18 fixed model calls.',
             'Shared backgrounds; controlled contexts; no retrieval. Context support reviewed by assistant, not independently human-validated.',
             'A correct answer without context support can reflect model memory; it is not proof of evidence retention.','']
    with (args.out/'results.jsonl').open('w',encoding='utf-8') as handle:
        for i,call in enumerate(calls,1):
            row={k:v for k,v in call.items() if k not in ('context','request')}
            print(f"[{i}/18] {call['call_id']} ...",flush=True)
            start=time.perf_counter()
            try:
                response=api('chat',call['request'])
                save(args.out/call['call_id']/'response.json',response)
                answer=response.get('message',{}).get('content')
                if response.get('done') is not True or not isinstance(answer,str): raise ValueError('Incomplete model response.')
                row.update(status='truncated' if response.get('done_reason')=='length' else 'ok' if answer.strip() else 'empty_response',
                           answer=answer,done_reason=response.get('done_reason'))
            except Exception as error:
                row.update(status='fault',answer=None,error=f'{type(error).__name__}: {error}')
                save(args.out/call['call_id']/'error.json',row)
            row['wall_seconds_including_load']=round(time.perf_counter()-start,3)
            handle.write(json.dumps(row,ensure_ascii=False)+'\n'); handle.flush()
            display=row['error'] if row['status']=='fault' else row['answer']
            block=(f"{call['call_id']} | {row['status']}\n  Question: {call['question']}\n"
                   f"  Expected: {call['expected_answer']}\n  Context support: {call['support_judgment']}\n"
                   f"  Answer: {display}\n")
            print(block,flush=True); summary.append(block)
            (args.out/'summary.txt').write_text('\n'.join(summary),encoding='utf-8')
            if row['status']=='fault': raise SystemExit('Stopped on model-call fault. Preserve this run and share the error.')
    print(f"Finished. Share {args.out/'summary.txt'}",flush=True)


if __name__=='__main__': main()
