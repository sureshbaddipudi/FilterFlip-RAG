#!/usr/bin/env python3
"""Offline closure audit and paired review material; never invokes a model."""
import argparse,base64,json
from collections import Counter
from pathlib import Path
import run_task03 as r

def audit(root,run,out,strict=True):
    r.need(not out.exists(),'Use a separate new audit output')
    plan,queue,logical,probe=r.validate_release(root)
    j=r.Journal(run/'journal.jsonl',r.identity_for(root))
    begun,done,used,active=r.validate_state(run,j,queue,probe,resume=False)
    r.need(not active and not (run/'RUN.lock').exists(),'Run not closed')
    r.need(used<=7200,'Measured active time exceeds allowance')
    faults=[e for e in j.events if e['kind']=='fault']
    complete=set(done)==set(range(61)) and not faults
    if strict:r.need(complete,'Study incomplete or faulted; no automatic retry')
    r.need(all(e.get('faulted') is False for e in j.events if e['kind']=='session_end') if complete else True,'Fault status differs')
    cpu=[e for e in j.events if e['kind']=='cpu_loaded_identity'];r.need({e['ordinal'] for e in cpu}==set(done),'CPU identity coverage differs')
    for event in cpu:
        models=[m for m in event['identity'].get('models',[]) if m.get('name')==plan['model']['name']]
        r.need(len(models)==1 and models[0]['digest']==plan['model']['digest'] and models[0]['size_vram']==0,'Loaded device identity differs')
    sourcechecks={}
    for name,rec in r.read(root/'INPUT_SOURCE_MANIFEST.json').items():sourcechecks[rec['source']]=r.sha(Path(rec['source']))==rec['sha256']
    for name,rec in r.read(root/'design/SOURCE_MANIFEST.json').items():sourcechecks[rec['source']]=r.sha(Path(rec['source']))==rec['sha256']
    for path,h in r.read(root/'ADDITIONAL_SOURCE_FINGERPRINTS.json').items():sourcechecks[path]=r.sha(Path(path))==h
    r.need(all(sourcechecks.values()),'Preserved original source changed')
    results={rec['request_sha256']:rec for i,rec in done.items() if i>0}
    historic_ref={x['request_sha256']:x for x in r.lines(root/'inputs/reference_answers.jsonl')}
    historic_rep={x['request_sha256']:x for x in r.read(root/'inputs/historical_reproduction.json')}
    joins=[]
    for row in logical:
        rec=results.get(row['request_sha256']);h=row['request_sha256']
        joins.append(dict(logical_id=row['logical_id'],case_id=row['case_id'],condition=row['condition'],arm=row['arm'],request_sha256=h,status=rec['status'] if rec else 'pending',answer=rec['answer'] if rec else None,
            ordinal=rec['ordinal'] if rec else None,same_run_reuse_of=row['same_run_reuse_of'],result_origin='Task03_fresh_same_run' if rec else None,
            exact_historical_reference_match=rec['answer']==historic_ref[h]['answer'] if rec and rec['status']=='ok' and h in historic_ref else None,
            exact_historical_reproduction_match=rec['answer']==historic_rep[h]['answer'] if rec and rec['status']=='ok' and h in historic_rep and historic_rep[h]['status']=='ok' else None,
            historical_answer_used_for_primary=False,semantic_review='pending'))
    by={(x['case_id'],x['condition'],x['arm']):x for x in joins}
    component={(x['case_id'],x['condition']):x for x in r.lines(root/'design/evidence/component_results.jsonl')}
    caseinfo={x['case_id']:x for x in r.read(root/'design/checks/CASE_SELECTION.json')}
    rag={(x['case_id'],x['condition']):x for x in r.lines(root/'inputs/ragdefender_results.jsonl')}
    current={x['case_id']:x for x in r.read(root/'design/evidence/current_primary_review_summary.json')['records']}
    paired=[];packets=[]
    for cid in plan['case_ids']:
        context=[]
        for co in plan['conditions']:
            x=component[cid,co];u,t=by[cid,co,'U'],by[cid,co,'T']
            paired.append(dict(case_id=cid,condition=co,U=u,T=t,same_request=u['request_sha256']==t['request_sha256'],same_complete_answer_text=(u['answer']==t['answer']) if u['status']==t['status']=='ok' else None,review_status='unreviewed'))
            context.append(dict(condition=co,retrieved=x['retrieved'],T_native_indices=x['kept_indices_native_order'],T_output_texts=x['output_texts'],T_removed_indices=x['removed_indices'],component_before=x['before'],component_after=x['after'],prior_ragdefender_survivor_indices=rag[cid,co]['kept_indices'],
              U=dict(new_result=u,historical_reference=historic_ref.get(u['request_sha256']),historical_reproduction=historic_rep.get(u['request_sha256'])),
              T=dict(new_result=t,historical_reference=historic_ref.get(t['request_sha256']),historical_reproduction=historic_rep.get(t['request_sha256'])),
              historical_R=dict(reference=historic_ref.get(next(y['request_sha256'] for y in r.lines(root/'inputs/reference_calls.jsonl') if y['case_id']==cid and y['condition']==co and y['mode']=='filtered'))),
              human_review=dict(reviewer=None,actual_review_date=None,assistance=None,blinding='Reference visible; unblinded',U_support=None,T_support=None,U_core_usable=None,T_core_usable=None,U_full_frozen_answer_completeness=None,T_full_frozen_answer_completeness=None,U_wrong_extra_claims=None,T_wrong_extra_claims=None,decisive_passages=None,rationale=None,disagreement=None)))
        packets.append(dict(case=caseinfo[cid],current_primary_review_history=current[cid],contexts=context,endpoint_review=dict(strict_event=None,background_qualified_event=None,clean_prerequisite=None,copy_exposure=None,unfiltered_prerequisite=None,all_support_lost=None,filtered_answer_failure=None,rule_used=None,rule_scope_or_extension_disposition=None,reviewer=None,actual_review_date=None,assistance=None,rationale=None),
          review_note='Earlier component judgments are assistant-authored; primary confirmations do not automatically adjudicate this hybrid pipeline or new answers.'))
    summary=dict(audit_status='PASS' if complete else 'INCOMPLETE_REQUIRES_INSPECTION',generation_calls_by_audit=0,all_approved_requests_accounted_for=complete,
        planned_unique=60,planned_logical=72,completed_durable_unique=len(results),unique_status_counts=dict(Counter(x['status'] for x in results.values())),logical_status_counts=dict(Counter(x['status'] for x in joins)),
        total_generation_attempts_including_synthetic=len(begun),attempt_cap=61,synthetic_preflight_status=done.get(0,{}).get('status','pending'),
        same_run_reused_logical_positions=12,active_seconds=used,active_seconds_cap=7200,
        historical_reference_exact_matches=sum(x['status']=='ok' and h in historic_ref and x['answer']==historic_ref[h]['answer'] for h,x in results.items()),
        historical_reproduction_exact_matches=sum(x['status']=='ok' and h in historic_rep and x['answer']==historic_rep[h]['answer'] for h,x in results.items()),
        historical_match_eligible_unique=sum(h in historic_ref for h in results),novel_unique=sum(h not in historic_ref for h in results),
        original_source_fingerprints_verified=sourcechecks,release_manifest_sha256=r.sha(root/'SHA256_MANIFEST.json'),journal_sha256=r.sha(run/'journal.jsonl'),
        human_semantic_review='pending task 7',scientific_acceptance='pending; technical completion does not establish correctness or a full TrustRAG failure',accepted_primary='8 events /51 non-events /0 unresolved unchanged',R110='uncertain unchanged')
    out.mkdir();(out/'cases').mkdir()
    for name,obj in [('AUDIT.json',summary),('LOGICAL_RESULTS.json',joins),('UNIQUE_RESULTS.json',list(results.values())),('PAIRED_RESULTS.json',paired),('ATTEMPT_LEDGER.json',[dict(ordinal=i,request_sha256=e['request_sha256'],status=done[i]['status'] if i in done else 'uncertain_no_durable_response') for i,e in begun.items()])]:r.save_new(out/name,obj)
    for packet in packets:r.save_new(out/'cases'/(packet['case']['case_id'].replace(':','_')+'.json'),packet)
    text='# Task 3: bounded TrustRAG stage-1 + evidence-only Qwen execution\n\nTechnical audit: '+summary['audit_status']+'. Human semantic review remains pending under task 7.\n\n'
    text+=f"{len(results)} durable distinct study responses serve 72 logical positions; status counts: {summary['unique_status_counts']} unique, {summary['logical_status_counts']} logical. The synthetic request is setup evidence and excluded from those study counts. Physical generation starts including preflight: {len(begun)}/61. Measured active time: {used:.3f}/7200 seconds.\n\n"
    text+='All primary answers in this panel were generated in the new run; only identical full requests share a same-run response. Forty-four unique request hashes have historical matches and sixteen are novel. Historical answers are diagnostics and never fill the new primary panel. String equality is not correctness; different strings are not automatically semantic failures.\n\n'
    text+='| Case | Condition | U status | T status | U answer | T answer |\n|---|---|---|---|---|---|\n'
    for x in paired:
        escape=lambda v:str(v).replace('|','\\|').replace('\n',' ')
        text+='| '+' | '.join(escape(v) for v in [x['case_id'],x['condition'],x['U']['status'],x['T']['status'],x['U']['answer'],x['T']['answer']])+' |\n'
    text+='\nThe twelve case packets preserve all five passages, native T order including empty outputs, exact new answers, historical answer provenance, original primary review history and blank new human fields. Full/core completeness, external support, wrong extra claims, uncertain and incomplete outcomes require actual review. Earlier four component support-loss judgments remain assistant interpretations; they are not four accepted new answer-loss events.\n\nThis evaluates saved TrustRAG stage-1 survivor selection followed by the existing evidence-only Qwen protocol. Later self-assessment/memory/consolidation stages were not evaluated. It does not establish a full TrustRAG failure or a population event rate. The accepted primary 8/51/0 and Week-6 results and R110 uncertainty remain unchanged. No teammate message was sent.\n'
    (out/'REPORT.md').write_text(text)
    r.save_new(out/'SHA256_MANIFEST.json',{str(p.relative_to(out)):r.sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
    print(json.dumps({k:v for k,v in summary.items() if k!='original_source_fingerprints_verified'},indent=2))
    return summary

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();audit(r.ROOT,a.run.resolve(),a.out.absolute())
if __name__=='__main__':main()
