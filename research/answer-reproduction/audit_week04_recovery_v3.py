#!/usr/bin/env python3
"""Offline integrity and review-packet audit for the two-interruption v3 recovery."""
import argparse
from collections import Counter,defaultdict
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
from zoneinfo import ZoneInfo


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for arg in ['release','run','out']:parser.add_argument('--'+arg,type=Path,required=True)
    a=parser.parse_args();release=a.release.resolve();run=a.run.resolve();out=a.out.absolute()
    if out.exists() or out.resolve().is_relative_to(release) or out.resolve().is_relative_to(run):raise ValueError('New separate audit output required')
    for rel,expected in json.loads((release/'SHA256_MANIFEST.json').read_text()).items():
        p=Path(rel)
        if p.is_absolute() or '..' in p.parts or sha(release/p)!=expected:raise ValueError('Release differs: '+rel)
    spec=importlib.util.spec_from_file_location('recovery_v3',release/'recover_answers.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
    plan,original,queue,calls,prior,old_done=r.validate_release();c=r.c
    events,done,used=r.current_state(run,r.identity_for(plan),queue)
    pe,pd,pre_seconds=r.current_state(release.parent/plan['preflight_output_name'],r.identity_for(plan),queue)
    c.require(not pd and sum(x['kind']=='preflight_complete' for x in pe)==1 and pre_seconds<=60,'Preflight differs')
    c.require(used<=plan['new_active_seconds_cap'],'New recovery active allowance exceeded')
    first=r.load(release/'previous_release/RECOVERY_ASSESSMENT.json')
    second=r.load(release/'SECOND_INTERRUPTION_AUDIT.json')
    source_checks={p:sha(Path(p))==h for p,h in {**first['original_paths'],**second['v2_run_fingerprints_after_owned_cleanup']}.items()}
    c.require(all(source_checks.values()),'A preserved original source changed')
    effective={x['request_sha256']:dict(x,result_origin='Shradha_original_completed_prefix') for x in prior[:127]}
    for n,x in old_done.items():effective[x['request_sha256']]=dict(x,result_origin='Suresh_local_continuation_2026-10-27' if n<=285 else 'Suresh_explicit_recovery_v2')
    for x in done.values():effective[x['request_sha256']]=dict(x,result_origin='Suresh_explicit_recovery_v3')
    logical=r.load(run/'COMBINED_LOGICAL_RESULTS.json');summary=r.load(run/'SUMMARY.json');attempts=r.load(run/'ATTEMPT_LEDGER.json')
    c.require(len(logical)==len(calls)==1062,'Logical coverage differs')
    for row,call in zip(logical,calls):
        result=effective.get(call['request_sha256'])
        c.require(all(row[k]==call[k] for k in ['call_id','case_id','condition','mode','request_sha256']),'Logical request differs')
        c.require(row['status']==(result['status'] if result else 'pending') and row['answer']==(result['answer'] if result else None) and row['result_origin']==(result['result_origin'] if result else None),'Logical result/provenance differs')
    expected=[]
    for n,x in old_done.items():
        if n<=285:expected.append(dict(ordinal=n,phase='continuation_v1',**{k:x[k] for k in ['request_sha256','status','attempt_role']}))
    key286=r.load(release/'previous_release/RECOVERY_QUEUE.json')[0]['call']['request_sha256']
    expected.append(dict(ordinal=286,phase='continuation_v1',request_sha256=key286,status='uncertain_no_durable_response',attempt_role='original_interrupted_attempt'))
    for n,x in old_done.items():
        if n>=286:expected.append(dict(ordinal=n,phase='recovery_v2',**{k:x[k] for k in ['request_sha256','status','attempt_role']}))
    expected.append(dict(ordinal=487,phase='recovery_v2',request_sha256=queue[0]['call']['request_sha256'],status='uncertain_no_durable_response',attempt_role='original_interrupted_attempt'))
    expected.extend(dict(ordinal=n,phase='recovery_v3',**{k:x[k] for k in ['request_sha256','status','attempt_role']}) for n,x in done.items())
    c.require(attempts==expected and len(attempts)==361+len(done)<=581,'Attempt history/cap differs')
    counts=dict(Counter(x['status'] for x in effective.values()))
    c.require(summary['effective_unique_status_counts']==counts and summary['recovery_durable_responses']==len(done),'Summary differs')
    refs={x['request_sha256']:x for x in c.lines(c.ROOT/'inputs/reference_unique_results.jsonl')};groups=defaultdict(list)
    for call in calls:groups[call['request_sha256']].append(call)
    review=[];index=[]
    for key,linked in groups.items():
        result=effective.get(key);call=linked[0]
        entry=dict(request_sha256=key,question=call['question'],frozen_expected_answer=call['expected_answer'],source_qualification=call['source_qualification'],
                   reference_answer=refs[key]['answer'],reproduced_answer=result['answer'] if result else None,status=result['status'] if result else 'pending',
                   result_origin=result['result_origin'] if result else None,
                   exact_reference_text_match=result['answer']==refs[key]['answer'] if result and result['status']=='ok' else None,
                   logical_conditions=[{k:x[k] for k in ['call_id','case_id','condition','mode','context_support','chunk_ids','text_hashes']} for x in linked])
        index.append(entry)
        if result and result['result_origin']!='Shradha_original_completed_prefix':
            review.append(dict(entry,request=call['request'],historical_source_review_status=call['source_review_status'],
                               human_review=dict(reviewer=None,date=None,assistance_disclosure=None,blinding='Reference visible; unblinded comparison',
                                                 semantic_change=None,answer_category=None,semantic_support=None,endpoint_implication=None,rationale=None)))
    all_attempts=[dict(phase='Shradha_original_return',ordinal=i,request_sha256=x['request_sha256'],status=x['status']) for i,x in enumerate(prior,1)]+attempts
    complete=list(done)==list(range(487,707));stamp=datetime.now(ZoneInfo('Asia/Kolkata')).isoformat()
    audit=dict(recorded_at=stamp,audit_status='PASS',generation_calls=0,all_approved_recovery_requests_accounted_for=complete,
               effective_unique_status_counts=counts,effective_unique_pending=706-len(effective),logical_status_counts=dict(Counter(x['status'] for x in logical)),
               continuation_recovery_attempts=len(attempts),amended_attempt_cap=581,all_attempts_including_original_return=len(all_attempts),
               all_attempt_statuses=dict(Counter(x['status'] for x in all_attempts)),predecessor_uncertain_attempts_preserved=[286,487],
               explicit_retry_487_status=done.get(487,{}).get('status','pending'),original_128_and_retry_statuses=[prior[127]['status'],old_done[128]['status']],
               new_complete_exact_reference_matches=sum(x['status']=='ok' and x['answer']==refs[x['request_sha256']]['answer'] for x in done.values()),
               new_complete_different_reference_text=sum(x['status']=='ok' and x['answer']!=refs[x['request_sha256']]['answer'] for x in done.values()),
               preflight_measured_seconds=pre_seconds,v3_measured_active_seconds=used,actual_historical_total_active_seconds=None,active_time_basis=plan['active_time_basis'],
               review_packet_records=len(review),review_packet_status_counts=dict(Counter(x['status'] for x in review)),
               original_source_fingerprints_verified=source_checks,release_manifest_sha256=sha(release/'SHA256_MANIFEST.json'),
               journal_sha256=sha(run/'journal.jsonl'),auditor_sha256=sha(Path(__file__)),scientific_acceptance='Pending human semantic review; accepted primary/Week-6 evidence unchanged.')
    out.mkdir(mode=0o700)
    def save(name,obj):(out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    save('AUDIT.json',audit);save('ALL_ATTEMPTS.json',all_attempts);save('REPRODUCTION_COMPARISON_INDEX.json',index)
    save('NEW_RESPONSE_REVIEW_PACKET.json',{'status':'unreviewed','note':'All local new responses. Prior teammate prefix retained in comparison index; its existing review coverage is not reassessed here. Exact matches are not correctness; different strings are not semantic failures. Preserve source/core/mixed-answer rules and uncertainty.','records':review})
    save('CHANGED_OR_INCOMPLETE_REVIEW_PACKET.json',{'status':'unreviewed','records':[x for x in review if x['exact_reference_text_match'] is not True]})
    strata=defaultdict(list)
    for row in logical:strata[row['case_id'].split(':')[0],row['condition'],row['mode']].append(row)
    save('BY_DATASET_CONDITION.json',[dict(dataset=k[0],condition=k[1],mode=k[2],n=len(v),statuses=dict(Counter(x['status'] for x in v))) for k,v in sorted(strata.items())])
    (out/'REPORT.md').write_text(f'''# Week-4 answer reproduction: v3 final audit

Recorded: {stamp}. Integrity audit: PASS. All approved v3 requests accounted for: {complete}.

Effective unique outcomes: {counts}; {706-len(effective)} pending of 706. Logical outcomes: {audit['logical_status_counts']} of 1062. These are technical completion statuses, not semantic verdicts.

The complete attempt history preserves the original and retried 128 truncations, the uncertain original 286 and its approved completed v2 retry, and the uncertain original 487 and its separately approved v3 retry ({audit['explicit_retry_487_status']}). No failed/uncertain attempt was discarded or given a larger token limit. Continuation/recovery starts: {len(attempts)} of the amended 581 ceiling; total including Shradha's original 128 attempts: {len(all_attempts)}.

V3 durable responses: {len(done)}. Complete exact-reference text matches: {audit['new_complete_exact_reference_matches']}; complete different strings: {audit['new_complete_different_reference_text']}. Wording differences require human review. Exact text equality does not establish correctness or support.

Measured v3 active time: {used:.3f} seconds; preflight: {pre_seconds:.3f} seconds. Actual historical active totals remain unknown. The explicitly approved accounting convention is retained verbatim in AUDIT.json; do not claim a measured eight-hour combined total.

The audit verifies release hashes, both predecessor chains, v3 chain and raw captures, tokens, request identities, logical joins, exact phase/attempt histories, clean v3 closure, time/attempt bounds and original-source fingerprints. No models were run by this audit. Original raw evidence, review attribution, primary tally and accepted Week-6 analysis remain unchanged. This remains a combined-machine/operator reproduction rather than an uninterrupted independent teammate reproduction.

The full comparison index has all 706 planned requests. The local-response review packet contains {len(review)} new responses; its changed/incomplete subset is a prioritization aid. All review fields remain blank. Supply the exact evidence and agreed source/core qualifications to Shradha through Suresh; preserve disagreements and uncertainty. No message is sent automatically.
''')
    save('SHA256_MANIFEST.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()})
    print(json.dumps({k:v for k,v in audit.items() if k!='original_source_fingerprints_verified'},indent=2))


if __name__=='__main__':main()
