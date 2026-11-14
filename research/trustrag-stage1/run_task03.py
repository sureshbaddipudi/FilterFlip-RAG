#!/usr/bin/env python3
"""Bounded fresh Qwen answers on saved TrustRAG stage-1 contexts."""
import argparse,base64,contextlib,hashlib,json,math,os,platform,signal,socket,subprocess,threading,time,urllib.request,urllib.error
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PORT=11437

def need(x,msg):
    if not x:raise ValueError(msg)
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(x):return hashlib.sha256(x).hexdigest()
def decode(raw):
    def pairs(items):
        d={}
        for k,v in items:need(k not in d,'Duplicate JSON key');d[k]=v
        return d
    def reject(x):raise ValueError('Nonfinite JSON')
    x=json.loads(raw,object_pairs_hook=pairs,parse_constant=reject)
    def finite(x):
        if isinstance(x,float):need(math.isfinite(x),'Nonfinite JSON')
        elif isinstance(x,dict):
            for v in x.values():finite(v)
        elif isinstance(x,list):
            for v in x:finite(v)
    finite(x);return x
def read(p):return decode(Path(p).read_bytes())
def lines(p):return [decode(x) for x in Path(p).read_bytes().splitlines() if x]
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()
def append(p,x):
    need(not p.is_symlink(),'Symlink log')
    with p.open('ab') as f:f.write(canonical(x)+b'\n');f.flush();os.fsync(f.fileno())
def save_new(p,x):
    with p.open('xb') as f:f.write(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False).encode()+b'\n');f.flush();os.fsync(f.fileno())
def snapshot(p,x):
    temp=p.with_name(p.name+'.tmp');save_new(temp,x);os.replace(temp,p)

def validate_release(root=ROOT):
    for rel,h in read(root/'SHA256_MANIFEST.json').items():
        q=Path(rel);need(not q.is_absolute() and '..' not in q.parts,'Unsafe manifest path')
        need(not (root/q).is_symlink() and sha(root/q)==h,'Release changed: '+rel)
    auth=read(root/'EXECUTION_AUTHORIZATION.json');plan=read(root/'design/PROPOSED_DESIGN.json')
    need(all(auth[x] is True for x in ['design_approved','implementation_authorized','bounded_execution_authorized']),'Execution not authorized')
    need(auth['approved_design_manifest_sha256']==sha(root/'design/SHA256_MANIFEST.json'),'Approved design changed')
    for rel,h in read(root/'design/SHA256_MANIFEST.json').items():need(sha(root/'design'/rel)==h,'Design input changed')
    bounds=plan['proposed_bounds']
    need(bounds==dict(study_attempt_ceiling=60,synthetic_preflight_attempt_ceiling=1,total_generation_attempt_ceiling=61,overall_active_seconds_cap=7200,per_generation_request_seconds_cap=600,daemon_startup_and_metadata_seconds_cap=60,parallel_generation_requests=1,retries=0),'Bounds changed')
    logical=lines(root/'design/checks/DRAFT_LOGICAL_REQUESTS.jsonl');queue=read(root/'design/checks/DRAFT_UNIQUE_REQUEST_QUEUE.json')
    component=lines(root/'design/evidence/component_results.jsonl');by={(r['case_id'],r['condition']):r for r in component}
    need(len(by)==36 and len(logical)==72 and len(queue)==60,'Coverage differs')
    first={}
    for row in logical:
        req=row['request'];model=plan['model'];r=by[row['case_id'],row['condition']]
        docs=r['retrieved'] if row['arm']=='U' else [r['retrieved'][i] for i in r['kept_indices_native_order']]
        expected=dict(model=model['name'],stream=False,options=model['options'],messages=[dict(role='system',content=model['system_prompt']),dict(role='user',content='Document:\n<document>\n'+'\n\n'.join(d['text'] for d in docs)+'\n</document>\n\nQuestion: '+r['question'])])
        need(req==expected and digest(canonical(req))==row['request_sha256'],'Request/context/settings changed')
        need(row['chunk_ids']==[d['chunk_id'] for d in docs] and row['text_hashes']==[d['text_sha256'] for d in docs],'Context join changed')
        need(row['same_run_reuse_of']==(first[row['request_sha256']]['logical_id'] if row['request_sha256'] in first else None),'Reuse differs')
        first.setdefault(row['request_sha256'],row)
        need(row['estimated_prompt_tokens']+192<=4096,'Input exceeds context budget')
    # Stored reuse links contain logical IDs, not row objects.
    need([x['logical_id'] for x in queue]==[x['logical_id'] for x in first.values()],'Queue differs')
    need(set((r['case_id'],r['condition'],r['arm']) for r in logical)=={(c,co,a) for c in plan['case_ids'] for co in plan['conditions'] for a in ['U','T']},'Logical coverage changed')
    for name,item in read(root/'INPUT_SOURCE_MANIFEST.json').items():need(sha(root/'inputs'/name)==item['sha256'],'Historical snapshot changed')
    probe=read(root/'design/checks/DRAFT_SYNTHETIC_PREFLIGHT_REQUEST.json')
    return plan,queue,logical,probe

def identity_for(root=ROOT):return dict(release_manifest_sha256=sha(root/'SHA256_MANIFEST.json'),approved_design_manifest_sha256=sha(root/'design/SHA256_MANIFEST.json'))

class Journal:
    def __init__(self,path,identity,create=False):
        self.path=path;self.lock=threading.RLock();self.events=[];self.previous='0'*64
        if create:
            need(not path.exists(),'Existing journal');self.add('identity',identity=identity)
        else:
            raw=path.read_bytes();need(raw.endswith(b'\n'),'Partial journal; inspect interruption')
            for s in raw.splitlines():
                e=decode(s);h=e.pop('sha256');need(e['previous']==self.previous and digest(canonical(e))==h,'Journal chain corrupt')
                self.events.append(e);self.previous=h
            need(bool(self.events) and self.events[0]==dict(kind='identity',identity=identity,previous='0'*64),'Journal identity differs')
    def add(self,kind,**kw):
        with self.lock:
            e=dict(kind=kind,previous=self.previous,**kw);h=digest(canonical(e));append(self.path,dict(e,sha256=h));self.events.append(e);self.previous=h
    def copied_events(self):
        with self.lock:return list(self.events)

def response_status(response,row,model):
    need(isinstance(response,dict) and response.get('model')==model['name'],'Response model differs')
    need(response.get('done') is True and not response.get('error'),'Response did not complete')
    msg=response.get('message');need(isinstance(msg,dict) and isinstance(msg.get('content'),str) and bool(msg['content'].strip()),'Empty/malformed response')
    n=response.get('prompt_eval_count');need(type(n) is int and abs(n-row['estimated_prompt_tokens'])<=16,'Prompt token count mismatch')
    need(n+192<=4096,'Context overflow')
    count=response.get('eval_count');need(type(count) is int and 0<count<=128,'Output token budget/count differs')
    need(response.get('done_reason') in ['stop','length'],'Unknown stop reason')
    return 'truncated' if response['done_reason']=='length' else 'ok'

def validate_state(out,j,queue,probe,resume=False):
    jobs={0:probe,**{i:r for i,r in enumerate(queue,1)}};begun={};done={};captures={};ends=[];active=False
    raw=lines(out/'raw_responses.jsonl') if (out/'raw_responses.jsonl').exists() else []
    for e in j.copied_events()[1:]:
        k=e['kind']
        if k=='session_start':need(not active,'Overlapping sessions');active=True
        elif k=='session_end':
            need(active and type(e['seconds']) in [int,float] and e['seconds']>=0,'Invalid session closure');active=False;ends.append(e)
        elif k=='begin':
            i=e['ordinal'];need(active and i in jobs and i not in begun,'Duplicate/unexpected attempt')
            need(e['request_sha256']==jobs[i]['request_sha256'],'Attempt request mismatch')
            need(i==0 if not begun else i==max(begun)+1,'Attempt order differs')
            begun[i]=e
        elif k=='raw_capture':
            i=e['ordinal'];need(i in begun and i not in captures,'Unexpected raw capture');pos=e['raw_index'];need(pos==len(captures) and pos<len(raw),'Missing/duplicate raw payload')
            rec=raw[pos];payload=base64.b64decode(rec['response_base64'],validate=True)
            need(rec['ordinal']==i and rec['request_sha256']==jobs[i]['request_sha256'],'Raw request mismatch')
            need(len(payload)==rec['response_bytes'] and digest(payload)==rec['response_sha256']==e['response_sha256'],'Raw bytes/hash mismatch')
            captures[i]=(rec,payload)
        elif k=='done':
            i=e['ordinal'];need(i in begun and i in captures and i not in done,'Missing/duplicate attempt completion')
            rec,payload=captures[i];r=e['record'];need(rec['http_status']==200 and decode(payload)==r['raw_response'],'Raw/derived answer differs')
            need(r['request_sha256']==jobs[i]['request_sha256'] and r['answer']==r['raw_response']['message']['content'],'Completed join differs')
            need(r['status']==response_status(r['raw_response'],jobs[i],read(ROOT/'design/PROPOSED_DESIGN.json')['model']),'Status differs')
            done[i]=r
        elif k in ['identity','unexpected']:raise ValueError('Unexpected journal event')
        else:need(k in ['backend_identity','cpu_loaded_identity','heartbeat','fault'],'Unknown journal event')
    need(len(raw)==len(captures),'Orphaned raw capture; inspect before resume')
    need(len(begun)<=61 and len([i for i in begun if i])<=60,'Attempt cap exceeded')
    if 0 in done:need(done[0]['status']=='ok','Synthetic preflight failed')
    need(not any(i>0 for i in begun) or 0 in done,'Study began before successful preflight')
    if resume:
        need(not active and len(ends)>0,'Unclosed prior session; no automatic recovery')
        need(not any(e['kind']=='fault' for e in j.events),'Faulted run; inspect before resuming')
        need(set(begun)==set(done),'Ambiguous attempt; no automatic retry')
    return begun,done,sum(e['seconds'] for e in ends),active

class Budget:
    def __init__(self,used=0,cap=7200,clock=time.monotonic,alarms=True):self.used=used;self.cap=cap;self.clock=clock;self.started=clock();self.alarms=alarms
    def remaining(self):return self.cap-self.used-(self.clock()-self.started)
    def check(self):need(self.remaining()>0,'Active time allowance exhausted')
    def arm(self):
        self.check()
        if self.alarms:signal.setitimer(signal.ITIMER_REAL,self.remaining())
    @contextlib.contextmanager
    def limit(self,cap):
        self.check()
        if self.alarms:signal.setitimer(signal.ITIMER_REAL,min(cap,self.remaining()))
        try:yield
        finally:
            if self.alarms:signal.setitimer(signal.ITIMER_REAL,max(.001,self.remaining()))
    def cancel(self):
        if self.alarms:signal.setitimer(signal.ITIMER_REAL,0)

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**kw):raise ValueError('Redirect refused')

class Backend:
    def __init__(self,out,model,budget,binary=Path('/usr/local/bin/ollama'),models=Path('/usr/share/ollama/.ollama/models')):
        self.process=None;self.log=None;self.model=model;self.budget=budget
        need(sha(binary)==read(ROOT/'design/evidence/baseline_runtime_plan.json')['ollama_binary_sha256'],'Binary identity differs')
        with socket.socket() as s:need(s.connect_ex(('127.0.0.1',PORT))!=0,'Dedicated port occupied; refuse shared service')
        self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
        self.log=(out/'ollama_console.log').open('ab')
        env=dict(os.environ,OLLAMA_HOST=f'127.0.0.1:{PORT}',OLLAMA_MODELS=str(models),OLLAMA_NUM_PARALLEL='1',OLLAMA_MAX_LOADED_MODELS='1',OLLAMA_NO_CLOUD='1',OLLAMA_VULKAN='0',OLLAMA_LLM_LIBRARY='cpu',CUDA_VISIBLE_DEVICES='-1',OLLAMA_NOPRUNE='1')
        try:
            self.process=subprocess.Popen([str(binary),'serve'],stdin=subprocess.DEVNULL,stdout=self.log,stderr=self.log,env=env,start_new_session=True)
            save_new(out/'BACKEND_OWNERSHIP.json',dict(pid=self.process.pid,pgid=self.process.pid,port=PORT,cwd=str(Path.cwd()),binary=str(binary),models=str(models),cpu_requested=True))
            while True:
                need(self.process.poll() is None,'Owned model service exited')
                try:self.start_identity=self.identity();break
                except urllib.error.URLError:time.sleep(.2)
        except BaseException:self.close();raise
    def api_bytes(self,endpoint,payload=None,timeout=10):
        need(endpoint in ['version','tags','show','ps','chat'],'Unexpected endpoint');self.budget.check()
        need(self.process.poll() is None,'Owned model service exited')
        req=urllib.request.Request(f'http://127.0.0.1:{PORT}/api/'+endpoint,data=canonical(payload) if payload is not None else None,headers={'Content-Type':'application/json'})
        try:
            with self.opener.open(req,timeout=min(timeout,max(.001,self.budget.remaining()))) as res:return res.status,res.read(2*1024*1024+1)
        except urllib.error.HTTPError as e:return e.code,e.read(2*1024*1024+1)
    def api(self,endpoint,payload=None):
        code,raw=self.api_bytes(endpoint,payload);need(code==200 and len(raw)<=2*1024*1024,'Metadata HTTP/size fault');return decode(raw)
    def identity(self):
        v=self.api('version');tags=self.api('tags');models=[m for m in tags.get('models',[]) if m.get('name')==self.model['name']]
        need(v=={'version':self.model['ollama_version']} and len(models)==1 and models[0]['digest']==self.model['digest'],'Served identity differs')
        shown=self.api('show',{'model':self.model['name']});need(digest(shown['template'].encode())==self.model['template_sha256'],'Served template differs')
        return dict(version=v,model=models[0],template_sha256=digest(shown['template'].encode()))
    def loaded_cpu(self):
        ps=self.api('ps');models=[m for m in ps.get('models',[]) if m.get('name')==self.model['name']]
        need(len(models)==1 and models[0]['digest']==self.model['digest'] and models[0].get('size_vram')==0,'Expected CPU-loaded model differs')
        return ps
    def chat(self,request):return self.api_bytes('chat',request,timeout=600)
    def close(self):
        if self.process is not None:
            try:os.killpg(self.process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            self.process.wait(timeout=10)
        if self.log:self.log.close()

def progress(out,j,queue,probe):
    begin=[e for e in j.copied_events() if e['kind']=='begin'];done=[e for e in j.copied_events() if e['kind']=='done']
    snapshot(out/'PROGRESS.json',dict(study_begun=sum(x['ordinal']>0 for x in begin),study_saved=sum(x['ordinal']>0 for x in done),planned_study_requests=len(queue),status_counts=dict(Counter(x['record']['status'] for x in done if x['ordinal']>0)),generation_attempts_including_preflight=len(begin),human_review='pending',updated_unix=time.time()))

def run_session(out,j,plan,queue,logical,probe,backend_factory=Backend,budget_factory=Budget,max_jobs=None):
    begun,done,used,_=validate_state(out,j,queue,probe,resume=len(j.events)>1)
    need(used<7200,'Active allowance exhausted')
    if len(done)==61:return
    budget=budget_factory(used=used);backend=None;stop=threading.Event();heartbeat_error=[]
    j.add('session_start',unix=time.time(),pid=os.getpid(),used_predecessor_seconds=used)
    def heartbeat():
        while not stop.wait(15):
            try:j.add('heartbeat',seconds=budget.clock()-budget.started,unix=time.time())
            except BaseException as e:heartbeat_error.append(e);return
    thread=threading.Thread(target=heartbeat,daemon=True);thread.start();faulted=False
    try:
        budget.arm()
        with budget.limit(60):backend=backend_factory(out,plan['model'],budget)
        j.add('backend_identity',identity=backend.start_identity)
        pending=[(0,probe)]+list(enumerate(queue,1));executed=0
        for ordinal,row in pending:
            if ordinal in done:continue
            if ordinal and max_jobs is not None and executed>=max_jobs:break
            need(not heartbeat_error,'Durable heartbeat failed');budget.check()
            need(len([e for e in j.events if e['kind']=='begin'])<61,'Generation attempt ceiling exhausted')
            with budget.limit(60):backend.identity()
            j.add('begin',ordinal=ordinal,request_sha256=row['request_sha256'],unix=time.time(),active_elapsed=budget.used+budget.clock()-budget.started)
            started=budget.clock()
            with budget.limit(600):code,raw=backend.chat(row['request'])
            capture=dict(ordinal=ordinal,request_sha256=row['request_sha256'],http_status=code,response_sha256=digest(raw),response_bytes=len(raw),response_base64=base64.b64encode(raw).decode())
            index=sum(e['kind']=='raw_capture' for e in j.events);append(out/'raw_responses.jsonl',capture)
            j.add('raw_capture',ordinal=ordinal,raw_index=index,response_sha256=digest(raw))
            need(code==200 and len(raw)<=2*1024*1024,'Generation HTTP/size failure')
            response=decode(raw);status=response_status(response,row,plan['model'])
            record=dict(ordinal=ordinal,request_sha256=row['request_sha256'],status=status,answer=response['message']['content'],raw_response=response,wall_seconds=budget.clock()-started)
            j.add('done',ordinal=ordinal,record=record);done[ordinal]=record
            with budget.limit(60):j.add('cpu_loaded_identity',ordinal=ordinal,identity=backend.loaded_cpu())
            progress(out,j,queue,probe)
            if ordinal==0:need(status=='ok','Synthetic preflight incomplete')
            else:executed+=1;print(f'[{ordinal}/60] {row["logical_id"]}: {status} ({record["wall_seconds"]:.1f}s)',flush=True)
        with budget.limit(60):backend.identity()
    except BaseException as error:
        faulted=True;j.add('fault',error_type=type(error).__name__,message=str(error)[:1000],unix=time.time());raise
    finally:
        budget.cancel();stop.set();thread.join(timeout=5)
        try:
            if backend:backend.close()
        finally:
            j.add('session_end',seconds=budget.clock()-budget.started,faulted=faulted,unix=time.time())
            progress(out,j,queue,probe)


def verify_model_assets():
    p=Path('/usr/share/ollama/.ollama/models/manifests/registry.ollama.ai/library/qwen2.5/3b');m=read(ROOT/'design/PROPOSED_DESIGN.json')['model']
    need(sha(p)==m['digest'],'Local model manifest changed');record=[]
    manifest=read(p)
    for r in [manifest['config']]+manifest['layers']:
        q=p.parents[4]/'blobs'/r['digest'].replace(':','-');need(q.stat().st_size==r['size'] and sha(q)==r['digest'].split(':')[1],'Model layer differs')
        record.append(dict(path=str(q),sha256=r['digest'].split(':')[1],size=r['size']))
    return record

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--resume',action='store_true');a=parser.parse_args()
    plan,queue,logical,probe=validate_release();out=a.out.absolute()
    need(not out.is_symlink() and not any(p.is_symlink() for p in out.parents),'Symlink output')
    need(not out.resolve().is_relative_to(ROOT) and out.parent.resolve()==ROOT.parent.resolve(),'Output must be new sibling of release')
    if a.resume:need(out.is_dir(),'Resume output absent')
    else:out.mkdir(exist_ok=False)
    lock=out/'RUN.lock';save_new(lock,dict(pid=os.getpid(),release_manifest_sha256=sha(ROOT/'SHA256_MANIFEST.json')))
    j=None
    def halt(signum,frame):raise InterruptedError('Worker interrupted; preserve, do not retry')
    def expired(signum,frame):raise TimeoutError('Per-operation or overall active deadline reached')
    signal.signal(signal.SIGTERM,halt);signal.signal(signal.SIGINT,halt);signal.signal(signal.SIGALRM,expired)
    try:
        assets=verify_model_assets()
        if not a.resume:save_new(out/'MODEL_ASSET_VERIFICATION.json',dict(layers=assets,binary_sha256=sha(Path('/usr/local/bin/ollama')),python=platform.python_version(),hostname=socket.gethostname()))
        j=Journal(out/'journal.jsonl',identity_for(),create=not a.resume)
        run_session(out,j,plan,queue,logical,probe)
    finally:lock.unlink(missing_ok=True)
if __name__=='__main__':main()
