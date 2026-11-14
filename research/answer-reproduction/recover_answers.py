#!/usr/bin/env python3
"""Explicit recovery of the interrupted Week-4 continuation; frozen requests only."""
import argparse
import base64
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import time

ROOT = Path(__file__).resolve().parent
previous_spec = importlib.util.spec_from_file_location('previous_recovery', ROOT/'previous_release/recover_answers.py')
previous = importlib.util.module_from_spec(previous_spec)
previous_spec.loader.exec_module(previous)
c = previous.c
digest = previous.digest
load = previous.load
verify_chain = previous.verify_chain
reconcile = previous.reconcile


def validate_release():
    for rel, expected in load(ROOT/'SHA256_MANIFEST.json').items():
        path = Path(rel)
        c.require(not path.is_absolute() and '..' not in path.parts, 'Unsafe manifest entry')
        c.require(c.sha(c.read(ROOT/path)) == expected, 'Recovery release changed: '+rel)
    previous_plan, original_plan, old_queue, calls, prior, first_done = previous.validate_release()
    plan = load(ROOT/'RECOVERY_PLAN.json')
    c.require(plan['schema'] == 'week04-recovery-v3' and plan['first_ordinal'] == 487 and plan['last_ordinal'] == 706, 'Wrong recovery bounds')
    c.require(plan['original_attempt_cap'] == 579 and plan['amended_attempt_cap'] == 581 and plan['predecessor_attempts_begun'] == 361, 'Attempt accounting differs')
    c.require(plan['previous_release_manifest_sha256'] == digest(ROOT/'previous_release/SHA256_MANIFEST.json'), 'Prior release differs')
    events = verify_chain(ROOT/'second_interrupted_run/journal.jsonl')
    c.require(events[0]['identity'] == previous.identity_for(previous_plan), 'Second interrupted identity differs')
    begun, second_done = reconcile(events, c.lines(ROOT/'second_interrupted_run/raw_responses.jsonl'), {j['ordinal']:j for j in old_queue})
    c.require(list(begun) == list(range(286,488)) and list(second_done) == list(range(286,487)), 'Second interrupted checkpoint differs')
    c.require(Counter(e['kind'] for e in events) == Counter(identity=1, session_start=1, backend_identity=1, begin=202, done=201), 'Unexpected second interrupted events')
    c.require(digest(ROOT/'second_interrupted_run/journal.jsonl') == plan['predecessor_journal_sha256'], 'Second chain anchor differs')
    expected = [dict(j, attempt_role='explicit_user_authorized_retry_of_uncertain_487' if j['ordinal']==487 else 'previously_unattempted') for j in old_queue if j['ordinal']>=487]
    queue = load(ROOT/'RECOVERY_QUEUE.json')
    c.require(queue == expected and len(queue) == 220, 'Recovery queue differs')
    old_done = dict(first_done)
    old_done.update(second_done)
    c.require(len(old_done) == 359, 'Prior durable response count differs')
    c.require({j['call']['request_sha256'] for j in queue}.isdisjoint({r['request_sha256'] for r in prior[:127]} | {r['request_sha256'] for r in old_done.values()}), 'Would repeat durable response')
    c.require(plan['accounted_predecessor_seconds'] == 13142 and plan['new_active_seconds_cap'] == 15658 and plan['preflight_seconds_cap'] == 60, 'Time accounting differs')
    return plan, original_plan, queue, calls, prior, old_done


def require_execution_authority(plan):
    c.require(plan['active_time_amendment_approved'] is True and bool(plan['active_time_approval_text']), 'Time accounting requires explicit approval')
    c.require(plan['retry_amendment_approved'] is True and bool(plan['retry_authorization']), 'Retry 487 requires explicit approval')


def current_state(out, identity, queue):
    return previous.current_state(out, identity, queue)


def identity_for(plan):
    return dict(schema='week04-recovery-v3', release_manifest_sha256=digest(ROOT/'SHA256_MANIFEST.json'),
                predecessor_journal_sha256=plan['predecessor_journal_sha256'],
                plan_sha256=digest(ROOT/'RECOVERY_PLAN.json'), cpu_only=True, dedicated_port=11436)


def snapshot(out, calls, prior, old_done, events, plan):
    new_done = {e['ordinal']:e['record'] for e in events if e['kind']=='done'}
    effective = {r['request_sha256']:dict(r,result_origin='Shradha_original_completed_prefix') for r in prior[:127]}
    for n,r in old_done.items():
        effective[r['request_sha256']] = dict(r,result_origin='Suresh_local_continuation_2026-10-27' if n<=285 else 'Suresh_explicit_recovery_v2')
    for r in new_done.values():effective[r['request_sha256']] = dict(r,result_origin='Suresh_explicit_recovery_v3')
    ref={r['request_sha256']:r for r in c.lines(c.ROOT/'inputs/reference_unique_results.jsonl')}
    logical=[]
    for call in calls:
        result=effective.get(call['request_sha256'])
        row={k:call[k] for k in ['call_id','case_id','condition','mode','request_sha256']}
        row.update(status=result['status'] if result else 'pending',answer=result['answer'] if result else None,
                   result_origin=result['result_origin'] if result else None,
                   exact_reference_text_match=result['answer']==ref[call['request_sha256']]['answer'] if result and result['status']=='ok' else None,
                   response_reused=call['identical_request_to'] is not None,semantic_review='pending; no automatic transfer of original labels')
        logical.append(row)
    begun=[e for e in events if e['kind']=='begin']
    attempts=[]
    for n,r in old_done.items():
        if n<=285:attempts.append(dict(ordinal=n,phase='continuation_v1',**{k:r[k] for k in ['request_sha256','status','attempt_role']}))
    old_uncertain_286=previous.load(previous.ROOT/'RECOVERY_QUEUE.json')[0]
    attempts.append(dict(ordinal=286,phase='continuation_v1',request_sha256=old_uncertain_286['call']['request_sha256'],status='uncertain_no_durable_response',attempt_role='original_interrupted_attempt'))
    for n,r in old_done.items():
        if n>=286:attempts.append(dict(ordinal=n,phase='recovery_v2',**{k:r[k] for k in ['request_sha256','status','attempt_role']}))
    uncertain_487=load(ROOT/'RECOVERY_QUEUE.json')[0]
    attempts.append(dict(ordinal=487,phase='recovery_v2',request_sha256=uncertain_487['call']['request_sha256'],status='uncertain_no_durable_response',attempt_role='original_interrupted_attempt'))
    attempts.extend(dict(ordinal=e['ordinal'],phase='recovery_v3',request_sha256=e['request_sha256'],status=new_done[e['ordinal']]['status'] if e['ordinal'] in new_done else 'uncertain_no_durable_response',attempt_role=e['attempt_role']) for e in begun)
    summary=dict(planned_unique=706,planned_logical=1062,original_completed_prefix=127,predecessor_attempts_begun=361,
                 predecessor_durable_responses=359,predecessor_uncertain_attempts_preserved=[286,487],
                 explicit_retry_286_completed=True,explicit_retry_487_completed=487 in new_done,
                 recovery_attempts_begun=len(begun),recovery_durable_responses=len(new_done),recovery_planned=220,
                 total_fresh_attempts_begun_including_uncertain=361+len(begun),amended_attempt_cap=581,
                 effective_unique_status_counts=dict(Counter(r['status'] for r in effective.values())),effective_unique_pending=706-len(effective),
                 logical_status_counts=dict(Counter(r['status'] for r in logical)),
                 effective_completed_exact_reference_matches=sum(r['status']=='ok' and r['answer']==ref[r['request_sha256']]['answer'] for r in effective.values()),
                 new_recovery_different_reference_text=sum(r['status']=='ok' and r['answer']!=ref[r['request_sha256']]['answer'] for r in new_done.values()),
                 all_recovery_requests_accounted_for=len(new_done)==220,original_128_and_retry_statuses=[prior[127]['status'],old_done[128]['status']],
                 active_time_basis=plan['active_time_basis'],measured_predecessor_total_seconds=None,
                 meaning='Technical completion only. Both old uncertain attempts remain in history, even if their separately authorized retries complete. Combined-machine/operator reproduction, not uninterrupted independent teammate reproduction.')
    c.require(len(attempts)==361+len(begun) and len(attempts)<=581,'Attempt accounting exceeds bound')
    for name,obj in [('SUMMARY.json',summary),('COMBINED_LOGICAL_RESULTS.json',logical),('RECOVERY_RESULTS.json',list(new_done.values())),('ATTEMPT_LEDGER.json',attempts)]:
        temp=out/(name+'.tmp');c.require(not temp.exists(),'Unfinished snapshot; inspect');c.save_new(temp,obj);os.replace(temp,out/name)
    return summary


def timeout_handler(signum, frame):
    raise TimeoutError('Bounded recovery deadline or operator termination; preserve attempt and stop')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--verify-only',action='store_true')
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--models',type=Path,default=Path('/usr/share/ollama/.ollama/models'))
    parser.add_argument('--binary',type=Path,default=Path('/usr/local/bin/ollama'))
    args=parser.parse_args()
    plan,original_plan,queue,calls,prior,old_done=validate_release()
    if args.verify_only:
        print(json.dumps(dict(status='PASS', generation_calls=0, predecessor_attempts=361, queued=220, execution_authorized=plan['active_time_amendment_approved'] and plan['retry_amendment_approved'])))
        return
    require_execution_authority(plan)
    c.require(args.out is not None and not (args.preflight and args.resume), 'Invalid output/mode')
    out=args.out.absolute()
    expected_out=ROOT.parent/(plan['preflight_output_name'] if args.preflight else plan['recovery_output_name'])
    c.require(out == expected_out, 'Only the single plan-bound output destination is allowed')
    models=args.models.resolve(strict=True);binary=args.binary.resolve(strict=True)
    c.require(not any(p.is_symlink() for p in [out,*out.parents]), 'Linked output path')
    c.require(not out.resolve().is_relative_to(ROOT) and not out.resolve().is_relative_to(models), 'Output overlaps evidence/model')
    c.require(not out.resolve().is_relative_to(Path(original_plan['source_package'])), 'Output overlaps original package')
    identity=identity_for(plan)
    if args.resume:
        c.require(out.is_dir(), 'Missing recovery output')
        previous,done,used=current_state(out,identity,queue)
    else:
        c.require(not out.exists(), 'Output already exists; never use a new folder to evade faults/budgets')
        previous,done,used=[],{},0.0
    remaining=(plan['preflight_seconds_cap'] if args.preflight else plan['new_active_seconds_cap'])-used
    c.require(remaining>30, 'Recovery active allowance exhausted')
    if not args.resume: out.mkdir(mode=0o700)
    os.umask(0o077)
    journal=c.Journal(out/'journal.jsonl',identity)
    c.save_new(out/'RUN.lock',dict(pid=os.getpid(), identity=identity))
    backend=None;started=time.monotonic();deadline=started+remaining-30;fault=None;cleanup_ok=False
    signal.signal(signal.SIGTERM,timeout_handler)
    signal.signal(signal.SIGALRM,timeout_handler)
    signal.setitimer(signal.ITIMER_REAL, max(1,remaining-20))
    journal.add('session_start',unix=time.time(), active_allowance_remaining_seconds=remaining)
    try:
        backend=c.Backend(binary,models,out,original_plan)
        journal.add('backend_identity',identity=backend.start_identity)
        if args.preflight:
            journal.add('preflight_complete',research_calls=0)
            print('Preflight passed; no research generation.',flush=True)
            return
        snapshot(out,calls,prior,old_done,journal.events,plan)
        for job in queue:
            n,call=job['ordinal'],job['call']
            if n in done: continue
            if deadline-time.monotonic()<25:
                journal.add('budget_exhausted_before_request',ordinal=n)
                break
            backend.identity()
            c.require(361+sum(e['kind']=='begin' for e in journal.events)<581, 'Attempt allowance exhausted')
            journal.add('begin',ordinal=n,request_sha256=call['request_sha256'],attempt_role=job['attempt_role'],unix=time.time())
            t=time.monotonic()
            response=backend.api('chat',call['request'],timeout=min(590,deadline-time.monotonic()))
            status=c.validate_response(response,call['estimated_prompt_tokens'])
            record=dict(ordinal=n, request_sha256=call['request_sha256'], first_call_id=call['call_id'],
                        status=status, answer=response['message']['content'], raw_response=response,
                        done_reason=response['done_reason'],prompt_eval_count=response['prompt_eval_count'],
                        eval_count=response.get('eval_count'), wall_seconds=time.monotonic()-t, attempt_role=job['attempt_role'])
            journal.add('done',ordinal=n,record=record)
            done[n]=record
            summary=snapshot(out,calls,prior,old_done,journal.events,plan)
            print(f'[{n}/706] {call["call_id"]}: {status}; recovery {len(done)}/220; {record["wall_seconds"]:.1f}s',flush=True)
        backend.identity()
    except BaseException as error:
        fault=error
        journal.add('fault',error_type=type(error).__name__,message=str(error)[:500])
        raise
    finally:
        try:
            if backend: backend.close()
            cleanup_ok=True
        finally:
            signal.setitimer(signal.ITIMER_REAL,0)
            journal.add('session_end',seconds=time.monotonic()-started,unix=time.time(),faulted=fault is not None)
            summary=snapshot(out,calls,prior,old_done,journal.events,plan)
            # Remove only this invocation's lock after owned-backend cleanup and durable closure.
            if cleanup_ok: (out/'RUN.lock').unlink()
            print(json.dumps(summary),flush=True)


if __name__=='__main__':
    main()
