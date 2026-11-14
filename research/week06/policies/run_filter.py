"""Gated Week-6 filter runner. Research execution requires resolved human review."""
import argparse
from pathlib import Path
import sys
from common import *
from policies import prepare_arm,near_groups
from runtime import Journal,Worker

def load_prepared(root):
    root=Path(root).resolve()
    manifest=decode(read(root/'PREPARATION_MANIFEST.json'))
    require(manifest['code']==code_hashes(),'Code changed since preparation; create a new preparation version')
    required={'contexts.json','challenges_DRAFT.json','native_profile.json','plan.json','review_TEMPLATE.json','CHALLENGE_REVIEW.md'}
    require(set(manifest['files'])==required,'Unexpected preparation files')
    for name,digest in manifest['files'].items():verified(root,name,digest)
    contexts=decode(read(root/'contexts.json'));plan=decode(read(root/'plan.json'));draft=decode(read(root/'challenges_DRAFT.json'))
    require(len(contexts)==295 and len({c['key'] for c in contexts})==295,'Incorrect saved panel')
    require(len(draft['anchors'])==10,'Incorrect challenge anchors')
    return manifest,contexts,plan,draft

def reviewed_challenges(draft,review,draft_hash,contexts):
    require(review.get('schema')=='week06-independent-review-v1','Unknown review schema')
    require(review.get('draft_sha256')==draft_hash,'Review refers to another draft')
    require(review.get('reviewer_role')=='independent_human','Independent review is pending')
    require(isinstance(review.get('reviewer_name'),str) and review['reviewer_name'].strip() and review['reviewer_name'].lower() not in ('assistant','codex'),'Named human reviewer required')
    import datetime
    datetime.date.fromisoformat(review['review_date'])
    decisions=review['decisions'];require(len(decisions)==10,'Expected ten anchor decisions')
    by={d['case_id']:d for d in decisions}
    require(len(by)==10 and set(by)=={a['case_id'] for a in draft['anchors']},'Review anchor mismatch')
    additions=[]
    for anchor in draft['anchors']:
        decision=by[anchor['case_id']]
        require(decision['decision'] in ('approve','exclude'),'Every trio needs approval or exclusion')
        require(isinstance(decision.get('rationale'),str) and decision['rationale'].strip(),'Review rationale required')
        if decision['decision']=='exclude':continue
        require(anchor['fits_window'] and max(anchor['token_counts'].values())<=256,'Approved challenge would truncate')
        for key in ['source_checked','wrong_claim_clear','neutral_support_intact','instruction_checked','contradictions_assessed']:
            require(decision.get(key) is True,'Incomplete independent review check: '+key)
        require(isinstance(decision.get('wrong_answer_rubric'),str) and decision['wrong_answer_rubric'].strip(),'Final wrong-answer rubric required')
        base=next(c for c in contexts if c['case_id']==anchor['case_id'] and c['condition']=='C')
        for condition,text in anchor['variants'].items():
            require(sha(text.encode())==anchor['variant_sha256'][condition],'Challenge text mismatch')
            additions.append(dict(base,key=base['case_id']+'/'+condition,condition=condition,
                texts=base['texts']+[text],passage_ids=base['passage_ids']+['challenge:'+anchor['case_id']+':'+condition],
                token_counts=base['token_counts']+[anchor['token_counts'][condition]],saved_native_kept=None,track='forced_append6',
                designated_indices=base['designated_indices']+([] if condition=='wrong_answer_append' else [5]),
                harmful_indices=[] if condition=='neutral_append' else [5]))
    return additions

def run(prepared,review_path,out,package,vendor,model,resume=False,stop_after=None):
    prepared=Path(prepared).resolve();package=Path(package).resolve()
    require(not Path(out).resolve().is_relative_to(package),'Run output inside original package')
    manifest,contexts,plan,draft=load_prepared(prepared)
    review_raw=read(review_path);review=decode(review_raw)
    additions=reviewed_challenges(draft,review,sha(read(prepared/'challenges_DRAFT.json')),contexts)
    # Recheck original provenance. Reuse is forbidden if any selected source changed.
    for name,digest in manifest['source_files'].items():verified(package/'reference',name,digest)
    identity={'preparation_sha256':sha(read(prepared/'PREPARATION_MANIFEST.json')),'review_sha256':sha(review_raw),
              'code':code_hashes(),'vendor':str(Path(vendor).resolve()),'model':str(Path(model).resolve())}
    forbidden=[prepared,package,Path(vendor),Path(model),Path(__file__).resolve().parent]
    if resume:
        out=Path(out).resolve();require(out.is_dir() and all(not out.is_relative_to(Path(p).resolve()) for p in forbidden),'Invalid resume directory')
    else:out=new_directory(out,forbidden)
    # Atomic run ownership; a stale lock is preserved for investigation, not removed on resume.
    lock=out/'RUN.lock'
    with lock.open('x') as f:f.write('Exclusive local runner\n')
    worker=None;journal=None
    try:
        journal=Journal(out/'journal.jsonl',identity)
        completed={e['key']:e['result'] for e in journal.events if e['kind']=='context'}
        allcontexts=contexts+additions
        if len(completed)==len(allcontexts):
            print('Run already complete; no calls made.');return
        journal.start()
        command=[sys.executable,'-u',str(Path(__file__).with_name('worker.py')),'--profile',str(prepared/'native_profile.json'),
                 '--vendor',str(Path(vendor).resolve()),'--model',str(Path(model).resolve())]
        worker=Worker(command,min(120,journal.remaining()))
        sentinels=[c for c in contexts if c['case_id'] in plan['sentinel_and_timing_case_ids'] and c['condition'] in plan['sentinel_and_timing_conditions']]
        require(len(sentinels)==12,'Incorrect sentinel count')
        for c in sentinels:
            response,_=journal.call(worker,'sentinel:'+c['key'],{'op':'native','question':c['question'],'texts':c['texts']},force=True)
            require(response['kept']==c['saved_native_kept'],'Sentinel mismatch: '+c['key'])
        timing_keys={c['key']:i for i,c in enumerate(sorted(sentinels,key=lambda c:c['key']))}
        processed=0
        for c in allcontexts:
            if c['key'] in completed:continue
            journal.remaining()
            score,score_cached=journal.call(worker,'scores:'+c['key'],{'op':'scores','question':c['question'],'texts':c['texts']})
            near_groups(c['texts'],score['scores'],score['matrix'])
            arms=['N','E','CN','O']
            if c['key'] in timing_keys:
                offset=timing_keys[c['key']]%4;arms=arms[offset:]+arms[:offset]
            results={'U':{'kept':list(range(len(c['texts']))),'source':'unfiltered','singleton_bypass':False}}
            for arm in arms:
                decision=prepare_arm(arm,c['texts'],score['scores'],score['matrix']);reps=decision['representatives']
                if arm=='N' and c['saved_native_kept'] is not None and c['key'] not in timing_keys:
                    kept=c['saved_native_kept'];metadata={'source':'saved_native','new_execution_seconds':0}
                elif decision['singleton_bypass']:
                    kept=reps;metadata={'source':'unguarded_singleton','new_execution_seconds':0}
                else:
                    force=c['key'] in timing_keys
                    result,cached=journal.call(worker,arm+':'+c['key'],{'op':'native','question':c['question'],
                      'texts':[c['texts'][i] for i in reps]},force=force)
                    kept=[reps[i] for i in result['kept']]
                    if arm=='N' and c['saved_native_kept'] is not None:require(kept==c['saved_native_kept'],'Timing baseline mismatch')
                    metadata={'source':'exact_request_cache' if cached else 'fresh_native',
                      'new_execution_seconds':0 if cached else result['seconds'],'original_execution_seconds':result['seconds']}
                results[arm]=dict(decision,kept=kept,**metadata)
            for result in results.values():
                result['designated_evidence_retained']=bool(set(result['kept']) & set(c['designated_indices']))
                result['harmful_passage_retained']=bool(set(result['kept']) & set(c['harmful_indices']))
                result['semantic_support']='UNREVIEWED';result['answer_correctness']='NOT_MEASURED'
            row={'context':c,'policies':results,'scores':score['scores'],'matrix':score['matrix'],
                 'score_cache_reused':score_cached,'independent_outcome_verification':False}
            journal.append('context',key=c['key'],result=row);completed[c['key']]=row;processed+=1
            if stop_after is not None and processed>=stop_after:break
        is_complete=len(completed)==len(allcontexts)
        if is_complete and not (out/'filter_results.json').exists():write_new(out/'filter_results.json',{'identity':identity,'complete':True,'records':[completed[c['key']] for c in allcontexts]})
        print(f'Saved {len(completed)}/{len(allcontexts)} contexts. Independent outcome review pending.')
    except BaseException as error:
        if journal and journal.started is not None:journal.append('fault',id='session',error_type=type(error).__name__)
        raise
    finally:
        if worker:worker.close()
        if journal and journal.started is not None:journal.finish()
        lock.unlink()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['prepared','review','out','package','vendor','model']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--resume',action='store_true');p.add_argument('--stop-after-contexts',type=int)
    a=p.parse_args()
    if a.stop_after_contexts is not None:require(a.stop_after_contexts>0,'Stop count must be positive')
    run(a.prepared,a.review,a.out,a.package,a.vendor,a.model,a.resume,a.stop_after_contexts)
