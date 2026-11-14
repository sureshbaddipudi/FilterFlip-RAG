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
if hashlib.sha256((ROOT/'baseline_v1/continue_answers.py').read_bytes()).hexdigest() != 'c610a6cb4949850b2dd5dac7c979c2d81f259ffbe1c9c8b473810751034f5a5e':
    raise ValueError('Frozen baseline module changed; refusing import')
spec = importlib.util.spec_from_file_location('continuation_baseline', ROOT/'baseline_v1/continue_answers.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return c.decode(c.read(path))


def verify_chain(path):
    raw = c.read(path)
    c.require(raw.endswith(b'\n'), 'Partial journal line')
    events, previous = [], '0'*64
    for line in raw.splitlines():
        event = c.decode(line)
        actual = event.pop('sha256')
        c.require(event['previous'] == previous and c.sha(c.canonical(event)) == actual, 'Broken journal chain')
        previous = actual
        events.append(event)
    c.require(bool(events), 'Empty journal')
    return events


def reconcile(events, captures, jobs):
    begun, done = {}, {}
    for event in events:
        if event['kind'] == 'begin':
            n = event['ordinal']
            c.require(n in jobs and n not in begun, 'Duplicate or unknown attempt')
            c.require(event['request_sha256'] == jobs[n]['call']['request_sha256'], 'Begin identity differs')
            begun[n] = event
        elif event['kind'] == 'done':
            n, record = event['ordinal'], event['record']
            c.require(n in begun and n not in done and record['ordinal'] == n, 'Unpaired completion')
            c.require(record['request_sha256'] == begun[n]['request_sha256'], 'Completion identity differs')
            response = record['raw_response']
            status = c.validate_response(response, jobs[n]['call']['estimated_prompt_tokens'])
            c.require(record['status'] == status and record['answer'] == response['message']['content'], 'Response record differs')
            done[n] = record
    raw_by_hash = {}
    for capture in captures:
        raw = base64.b64decode(capture['response_base64'], validate=True)
        key = capture['request_sha256']
        c.require(len(raw) == capture['response_bytes'] and c.sha(raw) == capture['response_sha256'], 'Raw capture differs')
        c.require(key not in raw_by_hash, 'Repeated captured request')
        raw_by_hash[key] = c.decode(raw)
    c.require(set(raw_by_hash) == {r['request_sha256'] for r in done.values()}, 'Unreconciled raw response; investigate before resume')
    for record in done.values():
        c.require(raw_by_hash[record['request_sha256']] == record['raw_response'], 'Raw/parsed response differs')
    return begun, done


def validate_release():
    for rel, expected in load(ROOT/'SHA256_MANIFEST.json').items():
        path = Path(rel)
        c.require(not path.is_absolute() and '..' not in path.parts, 'Unsafe manifest entry')
        c.require(c.sha(c.read(ROOT/path)) == expected, 'Recovery release changed: '+rel)
    original_plan, original_queue, calls, prior = c.validate_inputs()
    plan = load(ROOT/'RECOVERY_PLAN.json')
    c.require(plan['schema'] == 'week04-recovery-v2' and plan['first_ordinal'] == 286 and plan['last_ordinal'] == 706, 'Wrong recovery bounds')
    c.require(plan['original_attempt_cap'] == 579 and plan['amended_attempt_cap'] == 580, 'Attempt cap changed')
    c.require(plan['explicit_retry_286'] is True and plan['predecessor_attempts_begun'] == 159, 'Missing retry accounting')
    jobs = {j['ordinal']: j for j in original_queue}
    events = verify_chain(ROOT/'predecessor_run/journal.jsonl')
    c.require(events[0]['identity']['release_manifest_sha256'] == digest(ROOT/'baseline_v1/SHA256_MANIFEST.json'), 'Predecessor release identity differs')
    c.require(events[0]['identity']['plan_sha256'] == digest(ROOT/'baseline_v1/PLAN.json'), 'Predecessor plan identity differs')
    begun, done = reconcile(events, c.lines(ROOT/'predecessor_run/raw_responses.jsonl'), jobs)
    c.require(list(begun) == list(range(128, 287)) and list(done) == list(range(128, 286)), 'Predecessor checkpoint differs')
    c.require(Counter(e['kind'] for e in events) == Counter(identity=1, session_start=1, backend_identity=1, begin=159, done=158), 'Unexpected predecessor event')
    c.require(plan['predecessor_journal_sha256'] == digest(ROOT/'predecessor_run/journal.jsonl'), 'Predecessor chain anchor differs')
    expected_queue = [dict(jobs[n], attempt_role='explicit_user_authorized_retry_of_uncertain_286' if n == 286 else 'previously_unattempted') for n in range(286, 707)]
    queue = load(ROOT/'RECOVERY_QUEUE.json')
    c.require(queue == expected_queue and len(queue) == 421, 'Recovery queue differs')
    c.require({j['call']['request_sha256'] for j in queue}.isdisjoint({r['request_sha256'] for r in prior[:127]} | {r['request_sha256'] for r in done.values()}), 'Completed request would be repeated')
    c.require(plan['new_active_seconds_cap'] > 0 and plan['accounted_predecessor_seconds'] + plan['new_active_seconds_cap'] <= 28800, 'Time accounting exceeds original envelope')
    return plan, original_plan, queue, calls, prior, done


def require_execution_authority(plan):
    c.require(plan['active_time_amendment_approved'] is True, 'Historical active time is unknown; recovery accounting amendment requires explicit approval')
    c.require(bool(plan['active_time_approval_text']), 'Missing active-time approval record')


def current_state(out, identity, queue):
    journal_path = out/'journal.jsonl'
    if not journal_path.exists():
        c.require(not (out/'RUN.lock').exists(), 'Lock without journal; inspect')
        return [], {}, 0.0
    c.require(not (out/'RUN.lock').exists(), 'Recovery lock remains; inspect ownership, do not delete blindly')
    events = verify_chain(journal_path)
    c.require(events[0].get('identity') == identity, 'Recovery identity differs')
    c.require(not any(e['kind'] == 'fault' for e in events), 'Faulted recovery requires a new explicit assessment')
    begun, done = reconcile(events, c.lines(out/'raw_responses.jsonl') if (out/'raw_responses.jsonl').exists() else [], {j['ordinal']: j for j in queue})
    c.require(list(begun) == list(done), 'Uncertain recovery request; no automatic retry')
    c.require(list(begun) == [j['ordinal'] for j in queue[:len(begun)]], 'Recovery queue order differs')
    c.require(sum(e['kind'] == 'session_start' for e in events) == sum(e['kind'] == 'session_end' for e in events), 'Unclosed recovery session')
    return events, done, sum(e['seconds'] for e in events if e['kind'] == 'session_end')


def snapshot(out, calls, prior, old_done, events, plan):
    new_done = {e['ordinal']: e['record'] for e in events if e['kind'] == 'done'}
    effective = {r['request_sha256']: dict(r, result_origin='Shradha_original_completed_prefix') for r in prior[:127]}
    effective.update({r['request_sha256']: dict(r, result_origin='Suresh_local_continuation_2026-10-27') for r in old_done.values()})
    effective.update({r['request_sha256']: dict(r, result_origin='Suresh_explicit_recovery_v2') for r in new_done.values()})
    ref = {r['request_sha256']: r for r in c.lines(c.ROOT/'inputs/reference_unique_results.jsonl')}
    logical = []
    for call in calls:
        result = effective.get(call['request_sha256'])
        logical.append({k: call[k] for k in ['call_id', 'case_id', 'condition', 'mode', 'request_sha256']})
        logical[-1].update(status=result['status'] if result else 'pending', answer=result['answer'] if result else None,
                           result_origin=result['result_origin'] if result else None,
                           exact_reference_text_match=result['answer'] == ref[call['request_sha256']]['answer'] if result and result['status'] == 'ok' else None,
                           response_reused=call['identical_request_to'] is not None,
                           semantic_review='pending; no automatic transfer of original labels')
    begun = [e for e in events if e['kind'] == 'begin']
    summary = dict(planned_unique=706, planned_logical=1062, original_completed_prefix=127,
                   predecessor_attempts_begun=159, predecessor_durable_responses=158,
                   predecessor_uncertain_attempts_preserved=[286], explicit_retry_286_completed=286 in new_done,
                   recovery_attempts_begun=len(begun), recovery_durable_responses=len(new_done), recovery_planned=421,
                   total_fresh_attempts_begun_including_uncertain=159+len(begun), amended_attempt_cap=580,
                   effective_unique_status_counts=dict(Counter(r['status'] for r in effective.values())),
                   effective_unique_pending=706-len(effective), logical_status_counts=dict(Counter(r['status'] for r in logical)),
                   effective_completed_exact_reference_matches=sum(r['status'] == 'ok' and r['answer'] == ref[r['request_sha256']]['answer'] for r in effective.values()),
                   new_recovery_different_reference_text=sum(r['status'] == 'ok' and r['answer'] != ref[r['request_sha256']]['answer'] for r in new_done.values()),
                   all_recovery_requests_accounted_for=len(new_done) == 421,
                   original_128_and_retry_statuses=[prior[127]['status'], old_done[128]['status']],
                   active_time_basis=plan['active_time_basis'], measured_predecessor_total_seconds=None,
                   meaning='Completion is technical only. Old uncertain 286 remains in attempt history even if the authorized retry completes. Combined reproduction spans machines/operators; not uninterrupted independent teammate reproduction.')
    attempts = [dict(ordinal=n, phase='predecessor', **{k:r[k] for k in ['request_sha256','status','attempt_role']}) for n,r in old_done.items()]
    attempts.append(dict(ordinal=286, phase='predecessor', request_sha256=load(ROOT/'RECOVERY_QUEUE.json')[0]['call']['request_sha256'], status='uncertain_no_durable_response', attempt_role='original_interrupted_attempt'))
    attempts.extend(dict(ordinal=e['ordinal'], phase='recovery_v2', request_sha256=e['request_sha256'], status=new_done[e['ordinal']]['status'] if e['ordinal'] in new_done else 'uncertain_no_durable_response', attempt_role=e['attempt_role']) for e in begun)
    for name, obj in [('SUMMARY.json',summary), ('COMBINED_LOGICAL_RESULTS.json',logical), ('RECOVERY_RESULTS.json',list(new_done.values())), ('ATTEMPT_LEDGER.json',attempts)]:
        temp = out/(name+'.tmp')
        c.require(not temp.exists(), 'Unfinished snapshot; investigate')
        c.save_new(temp,obj)
        os.replace(temp,out/name)
    return summary


def identity_for(plan):
    return dict(schema='week04-recovery-v2', release_manifest_sha256=digest(ROOT/'SHA256_MANIFEST.json'),
                predecessor_journal_sha256=plan['predecessor_journal_sha256'],
                plan_sha256=digest(ROOT/'RECOVERY_PLAN.json'), cpu_only=True, dedicated_port=11436)


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
        print(json.dumps(dict(status='PASS', generation_calls=0, predecessor_attempts=159, queued=421, execution_authorized=plan['active_time_amendment_approved'])))
        return
    require_execution_authority(plan)
    c.require(args.out is not None and not (args.preflight and args.resume), 'Invalid output/mode')
    out=args.out.absolute()
    expected_out=ROOT.parent/('FilterFlip_Week04_Recovery_Preflight_2026-10-30' if args.preflight else 'FilterFlip_Week04_Recovery_Run_2026-10-30')
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
            c.require(159+sum(e['kind']=='begin' for e in journal.events)<580, 'Attempt allowance exhausted')
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
            print(f'[{n}/706] {call["call_id"]}: {status}; recovery {len(done)}/421; {record["wall_seconds"]:.1f}s',flush=True)
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
