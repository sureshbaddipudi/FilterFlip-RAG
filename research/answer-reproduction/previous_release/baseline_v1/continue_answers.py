#!/usr/bin/env python3
"""Frozen-request continuation with owned CPU Ollama, durable attempts and no blind retries."""
import argparse
import base64
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import signal
import socket
import subprocess
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
PORT = 11436

def require(ok, message):
    if not ok:
        raise ValueError(message)

def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def decode(raw):
    def pairs(items):
        obj = {}
        for k, v in items:
            require(k not in obj, 'Duplicate JSON key')
            obj[k] = v
        return obj
    def number(value):
        result = float(value)
        require(math.isfinite(result), 'Nonfinite JSON')
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_float=number,
                      parse_constant=lambda x: require(False, 'Nonfinite JSON'))

def read(path, cap=32*1024*1024):
    path = Path(path)
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= cap, 'Missing/unsafe/oversized input: ' + str(path))
    return path.read_bytes()

def lines(path):
    return [decode(x) for x in read(path).splitlines() if x]

def save_new(path, obj):
    with Path(path).open('xb') as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False).encode() + b'\n')
        f.flush(); os.fsync(f.fileno())

def append(path, obj):
    require(not Path(path).is_symlink(), 'Symlink log')
    with Path(path).open('ab') as f:
        f.write(canonical(obj) + b'\n'); f.flush(); os.fsync(f.fileno())

def validate_response(response, estimated):
    require(response.get('done') is True, 'Response did not finish')
    answer = response.get('message', {}).get('content')
    require(isinstance(answer, str) and bool(answer.strip()), 'Empty/malformed answer')
    count = response.get('prompt_eval_count')
    require(type(count) is int and abs(count - estimated) <= 16, 'Prompt token estimate mismatch')
    require(count + 128 + 64 <= 4096, 'Context overflow')
    reason = response.get('done_reason')
    require(reason in ['stop', 'length'], 'Unexpected finish reason')
    return 'truncated' if reason == 'length' else 'ok'

def validate_inputs():
    manifest = decode(read(ROOT/'SHA256_MANIFEST.json'))
    for rel, digest in manifest.items():
        p = Path(rel)
        require(not p.is_absolute() and '..' not in p.parts, 'Unsafe manifest path')
        require(sha(read(ROOT/p)) == digest, 'Release changed: ' + rel)
    plan = decode(read(ROOT/'PLAN.json'))
    for rel, digest in plan['input_files'].items():
        require(sha(read(ROOT/rel)) == digest, 'Frozen input changed')
    require(sha(read(ROOT/'queue.json')) == plan['queue_sha256'], 'Queue changed')
    queue = decode(read(ROOT/'queue.json'))
    calls = lines(ROOT/'inputs/calls.jsonl')
    ordered = {}
    for c in calls:
        require(sha(canonical(c['request'])) == c['request_sha256'], 'Request digest mismatch')
        req = c['request']
        require(req['model'] == plan['model'] and req['options'] == plan['model_options'] and req['stream'] is False, 'Frozen settings mismatch')
        require(0 < c['estimated_prompt_tokens'] and c['estimated_prompt_tokens'] + 192 <= 4096, 'Request too long')
        ordered.setdefault(c['request_sha256'], c)
    prior = lines(ROOT/'inputs/prior_unique_results.jsonl')
    work = list(ordered.values())
    require(len(work) == 706 and len(calls) == 1062 and len(prior) == 128 and len(queue) == 579, 'Plan coverage mismatch')
    require(len({c['call_id'] for c in calls}) == 1062, 'Duplicate logical call')
    for i, r in enumerate(prior):
        require(r['request_sha256'] == work[i]['request_sha256'], 'Prior prefix mismatch')
        require(r['status'] == ('ok' if i < 127 else 'truncated'), 'Prior status changed')
    for i, job in enumerate(queue, 128):
        require(job['ordinal'] == i and job['call'] == work[i-1], 'Queue order changed')
    require(plan['request_count'] == 579 and plan['max_active_seconds'] == 28800 and plan['max_seconds_per_request'] == 600, 'Unexpected bounds')
    return plan, queue, calls, prior

class Journal:
    def __init__(self, path, identity):
        self.path, self.events, self.previous = path, [], '0'*64
        if path.exists():
            raw = read(path)
            require(raw.endswith(b'\n'), 'Partial journal record; no blind resume')
            for line in raw.splitlines():
                e = decode(line); digest = e.pop('sha256')
                require(e['previous'] == self.previous and sha(canonical(e)) == digest, 'Journal chain changed')
                self.previous = digest; self.events.append(e)
            require(self.events[0].get('identity') == identity, 'Run identity changed')
            require(not any(e['kind'] == 'fault' for e in self.events), 'Faulted run requires investigation')
            begun = [e['ordinal'] for e in self.events if e['kind'] == 'begin']
            done = [e['ordinal'] for e in self.events if e['kind'] == 'done']
            require(len(set(begun)) == len(begun) and begun == done, 'Uncertain prior attempt; no blind retry')
            require(sum(e['kind'] == 'session_start' for e in self.events) == sum(e['kind'] == 'session_end' for e in self.events), 'Unclosed prior session')
        else:
            self.add('identity', identity=identity)
    def add(self, kind, **values):
        e = dict(kind=kind, previous=self.previous, **values)
        digest = sha(canonical(e)); append(self.path, dict(e, sha256=digest))
        self.events.append(e); self.previous = digest

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError('Redirect prohibited')

class Backend:
    def __init__(self, binary, models, out, plan):
        self.process = None
        self.plan, self.out = plan, out
        require(sha(read(binary, 128*1024*1024)) == plan['ollama_binary_sha256'], 'Ollama binary changed')
        with socket.socket() as probe:
            probe.settimeout(.5)
            require(probe.connect_ex(('127.0.0.1', PORT)) != 0, 'Dedicated port occupied; refusing shared service')
        self.log = (out/'ollama_console.log').open('ab')
        env = dict(os.environ, OLLAMA_HOST=f'127.0.0.1:{PORT}', OLLAMA_MODELS=str(models),
                   OLLAMA_NUM_PARALLEL='1', OLLAMA_MAX_LOADED_MODELS='1', OLLAMA_NO_CLOUD='1',
                   OLLAMA_VULKAN='0', OLLAMA_LLM_LIBRARY='cpu', CUDA_VISIBLE_DEVICES='-1', OLLAMA_NOPRUNE='1')
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        try:
            self.process = subprocess.Popen([str(binary), 'serve'], env=env, stdin=subprocess.DEVNULL,
                stdout=self.log, stderr=self.log, start_new_session=True)
            deadline = time.monotonic() + 60
            while True:
                try:
                    self.start_identity = self.identity()
                    break
                except urllib.error.URLError:
                    require(self.process.poll() is None and time.monotonic() < deadline, 'Owned daemon unavailable; inspect console log')
                    time.sleep(.2)
            shown = self.api('show', {'model': plan['model']})
            require(sha(shown['template'].encode()) == plan['template_sha256'], 'Model template differs')
            self.start_identity['template_sha256'] = sha(shown['template'].encode())
        except BaseException:
            self.close(); raise
    def api(self, endpoint, payload=None, timeout=10):
        require(endpoint in ['version', 'tags', 'show', 'chat'], 'Unexpected endpoint')
        require(self.process.poll() is None, 'Owned daemon exited')
        req = urllib.request.Request(f'http://127.0.0.1:{PORT}/api/'+endpoint,
              data=canonical(payload) if payload is not None else None, headers={'Content-Type':'application/json'})
        try:
            with self.opener.open(req, timeout=timeout) as response:
                raw = response.read(2*1024*1024+1)
        except urllib.error.HTTPError as error:
            raw = error.read(2*1024*1024+1)
            if endpoint == 'chat': self.capture(payload, raw)
            raise
        if endpoint == 'chat': self.capture(payload, raw)
        require(len(raw) <= 2*1024*1024, 'Oversized response')
        obj = decode(raw); require(not obj.get('error'), 'Backend error')
        return obj
    def capture(self, request, raw):
        append(self.out/'raw_responses.jsonl', {'request_sha256':sha(canonical(request)),
               'response_sha256':sha(raw), 'response_bytes':len(raw), 'response_base64':base64.b64encode(raw).decode()})
    def identity(self):
        version = self.api('version')
        models = [m for m in self.api('tags').get('models', []) if m.get('name') == self.plan['model']]
        require(version == {'version':self.plan['ollama_version']} and len(models) == 1 and models[0]['digest'] == self.plan['model_digest'], 'Served model/version differs')
        return {'ollama':version, 'model':models[0]}
    def close(self):
        if self.process is not None:
            try: os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError: pass
            self.process.wait(timeout=10)
        if hasattr(self, 'log'): self.log.close()

def build_outputs(out, calls, prior, journal):
    completed = [e['record'] for e in journal.events if e['kind'] == 'done']
    effective = {r['request_sha256']:dict(r, result_origin='Shradha_original_completed_prefix') for r in prior[:127]}
    for r in completed:
        require(r['request_sha256'] not in effective, 'Duplicate completed request')
        effective[r['request_sha256']] = dict(r, result_origin='Suresh_local_continuation')
    if prior[127]['request_sha256'] not in effective:
        effective[prior[127]['request_sha256']] = dict(prior[127], result_origin='Shradha_original_truncated_128')
    reference = {r['request_sha256']:r for r in lines(ROOT/'inputs/reference_unique_results.jsonl')}
    logical = []
    for c in calls:
        r = effective.get(c['request_sha256'])
        logical.append({'call_id':c['call_id'], 'case_id':c['case_id'], 'condition':c['condition'], 'mode':c['mode'],
                        'request_sha256':c['request_sha256'], 'status':r['status'] if r else 'pending',
                        'answer':r.get('answer') if r else None, 'result_origin':r.get('result_origin') if r else None,
                        'response_reused':c['identical_request_to'] is not None,
                        'exact_reference_text_match':r.get('answer') == reference[c['request_sha256']]['answer'] if r and r['status'] == 'ok' else None,
                        'new_answer_human_review':'pending' if r and r.get('result_origin') == 'Suresh_local_continuation' else 'not_changed_by_this_continuation'})
    summary={'planned_unique':706, 'planned_logical':1062, 'continuation_attempts_completed':len(completed),
             'continuation_planned':579, 'all_queued_requests_attempted':len(completed)==579,
             'effective_unique_status_counts':dict(Counter(r['status'] for r in effective.values())),
             'logical_status_counts':dict(Counter(r['status'] for r in logical)),
             'continuation_status_counts':dict(Counter(r['status'] for r in completed)),
             'new_completed_exact_reference_matches':sum(r['status']=='ok' and r['answer']==reference[r['request_sha256']]['answer'] for r in completed),
             'new_completed_different_reference_text':sum(r['status']=='ok' and r['answer']!=reference[r['request_sha256']]['answer'] for r in completed),
             'meaning':'ok means complete response, not human correctness. Different answer text is not automatically wrong. Original 128 truncation remains preserved; combined output mixes original teammate prefix and local continuation.',
             'new_human_outcome_review':'pending; original 59-case confirmations do not automatically approve these new answers'}
    # Atomic derived snapshots can be regenerated; raw evidence/journal remain append-only.
    for name,obj in [('SUMMARY.json',summary),('COMBINED_LOGICAL_RESULTS.json',logical),('CONTINUATION_RESULTS.json',completed)]:
        temp=out/(name+'.tmp')
        require(not temp.exists(), 'Unexpected unfinished derived snapshot')
        save_new(temp,obj);os.replace(temp,out/name)
    return summary

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--models',type=Path,default=Path('/usr/share/ollama/.ollama/models'))
    parser.add_argument('--binary',type=Path,default=Path('/usr/local/bin/ollama'))
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--preflight',action='store_true')
    args=parser.parse_args()
    plan,queue,calls,prior=validate_inputs()
    out=args.out.absolute();models=args.models.resolve(strict=True);binary=args.binary.resolve(strict=True)
    require(not out.is_symlink() and not any(x.is_symlink() for x in out.parents), 'Symlink output path')
    require(not out.resolve().is_relative_to(ROOT) and not out.resolve().is_relative_to(models) and not out.resolve().is_relative_to(Path(plan['source_package'])), 'Output overlaps protected inputs')
    if args.resume:require(out.is_dir() and not args.preflight, 'Invalid resume')
    else:out.mkdir(parents=False,exist_ok=False)
    lock=out/'RUN.lock';save_new(lock,{'pid':os.getpid()})
    backend=None;j=None;started=None
    try:
        if args.preflight:
            backend=Backend(binary,models,out,plan)
            save_new(out/'PREFLIGHT.json',{'identity':backend.start_identity,'research_calls':0,'queue_count':len(queue),'status':'ready'})
            print('Preflight passed: exact model, version and template; 579 queued requests; zero research calls.',flush=True)
            return
        identity={'release_manifest_sha256':sha(read(ROOT/'SHA256_MANIFEST.json')),'plan_sha256':sha(read(ROOT/'PLAN.json')),
                  'binary_sha256':sha(read(binary,128*1024*1024)),'models':str(models),'platform':platform.platform(),
                  'python':platform.python_version(),'hostname':socket.gethostname(),'cpu_only_requested':True}
        j=Journal(out/'journal.jsonl',identity)
        finished={e['ordinal'] for e in j.events if e['kind']=='done'}
        require(finished <= {q['ordinal'] for q in queue}, 'Unexpected completed ordinal')
        used=sum(e['seconds'] for e in j.events if e['kind']=='session_end')
        require(used<plan['max_active_seconds'], 'Active time budget exhausted')
        if len(finished)==579:
            build_outputs(out,calls,prior,j);print('Already complete; no inference.');return
        started=time.monotonic();j.add('session_start',unix=time.time())
        backend=Backend(binary,models,out,plan);j.add('backend_identity',identity=backend.start_identity)
        build_outputs(out,calls,prior,j)
        for job in queue:
            ordinal=job['ordinal'];c=job['call']
            if ordinal in finished:continue
            remaining=plan['max_active_seconds']-used-(time.monotonic()-started)
            require(remaining>0,'Active time budget exhausted')
            backend.identity()
            j.add('begin',ordinal=ordinal,request_sha256=c['request_sha256'],attempt_role=job['attempt_role'],unix=time.time())
            t=time.monotonic();response=backend.api('chat',c['request'],timeout=min(590,remaining))
            status=validate_response(response,c['estimated_prompt_tokens'])
            record={'ordinal':ordinal,'request_sha256':c['request_sha256'],'first_call_id':c['call_id'],
                    'status':status,'answer':response['message']['content'],'raw_response':response,
                    'done_reason':response['done_reason'],'prompt_eval_count':response['prompt_eval_count'],
                    'eval_count':response.get('eval_count'),'wall_seconds':time.monotonic()-t,'attempt_role':job['attempt_role']}
            j.add('done',ordinal=ordinal,record=record)
            finished.add(ordinal)
            build_outputs(out,calls,prior,j)
            print(f'[{ordinal}/706] {c["call_id"]}: {status}; {len(finished)}/579 continuation attempts ({record["wall_seconds"]:.1f}s)',flush=True)
        backend.identity()
    except BaseException as error:
        if j is not None:j.add('fault',error_type=type(error).__name__,message=str(error)[:500])
        raise
    finally:
        if backend:backend.close()
        if j is not None and started is not None:
            j.add('session_end',seconds=time.monotonic()-started,unix=time.time())
            summary=build_outputs(out,calls,prior,j)
            print(json.dumps(summary),flush=True)
        lock.unlink(missing_ok=True)

if __name__=='__main__':
    main()
