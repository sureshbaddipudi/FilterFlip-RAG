"""Local, single-job live demonstration. Browser inputs never become paths/commands."""
import argparse, hmac, importlib.util, json, os, re, secrets, signal, subprocess
import threading, time, uuid, shutil
from safety import load, save, decode, check_selection, verify_release, require, load_config
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from pathlib import Path

ROOT=Path(__file__).resolve().parent
JOB_SECONDS=2400
MAX_RUN_BYTES=128*1024*1024
JOB=re.compile(r'[0-9a-f]{32}\Z')
HEADERS={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY',
 'Permissions-Policy':'camera=(), microphone=(), geolocation=()',
 'Cross-Origin-Opener-Policy':'same-origin','Referrer-Policy':'no-referrer','Cross-Origin-Resource-Policy':'same-origin',
 'Content-Security-Policy':"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"}
def encoded(x):return json.dumps(x,ensure_ascii=False,allow_nan=False).encode()
def kill(process):
    if process:
        try:os.killpg(process.pid,signal.SIGKILL)
        except ProcessLookupError:pass
        process.wait(timeout=5)
class Manager:
    def __init__(self,config):
        self.config_path=Path(config).absolute();self.cfg=load_config(self.config_path)
        require(self.cfg.get('compute_profile')=='cpu','Only the reviewed CPU profile is supported')
        for name in ('python','package','encoder','ollama_binary','ollama_models','runs'):
            require(isinstance(self.cfg.get(name),str) and Path(self.cfg[name]).is_absolute(),'Absolute configured path required')
        payload=load(ROOT/'data/recorded.json')
        self.cases={c['case_id']:dict(c) for c in payload['cases']}
        ledger=load(ROOT/'data/human_reviews.json')
        self.reviews={c['case_id']:c for c in ledger['records']}
        review_summary=load(ROOT/'data/CURRENT_REVIEW_SUMMARY.json')
        self.display_reviews={c['case_id']:c for c in review_summary['records']}
        self.benign=set(load(ROOT/'data/week06_plan.json')['generation_case_ids'])
        self.approved={d['case_id'] for d in load(ROOT/'data/challenge_review.json')['decisions'] if d['decision']=='approve'}
        self.qualifications={c['case_id']:c['qualification'] for c in load(ROOT/'data/challenge_definitions.json')['anchors']}
        for cid,c in self.cases.items():
            c['current_human_review']=self.reviews[cid]
            c['display_review_summary']=self.display_reviews[cid]
            c['review_notice']='Saved evidence only. Human confirmation reported by Suresh on 27 October; earlier manual and joint decisions retain precedence. New runs require new review.'
        self.runs=Path(self.cfg['runs']).resolve()
        forbidden=[ROOT,Path(self.cfg['package']).resolve(),Path(self.cfg['encoder']).resolve(),Path(self.cfg['ollama_models']).resolve()]
        if any(self.runs.is_relative_to(p) or p.is_relative_to(self.runs) for p in forbidden):raise ValueError('Run folder must be separate from code and inputs')
        self.runs.mkdir(parents=True,exist_ok=True,mode=0o700)
        require(self.runs.stat().st_uid==os.getuid(),'Run folder must belong to this account')
        require(self.runs.stat().st_mode & 0o077 == 0,'Run folder must be private (chmod 700)')
        from operations import RunLock, AuditLog
        self.archive_lock=RunLock(self.runs);self.audit=AuditLog(self.runs)
        self.lock=threading.Lock();self.active=None;self.process=None;self.cancel_requested=False
    def start(self,data):
        check_selection(data,self.cases,self.approved,self.benign)
        with self.lock:
            if self.active:raise RuntimeError('One live comparison is already running')
            if len(list(self.runs.glob('[0-9a-f]'*32)))>=60:raise RuntimeError('Run archive limit reached. Stop the server and use archive_runs.py; see ARCHIVE_GUIDE.md')
            require(shutil.disk_usage(self.runs).free>=1024**3,'At least 1 GiB free disk is required')
            require(sum(p.stat().st_size for p in self.runs.rglob('*') if p.is_file() and not p.is_symlink())<1024**3,'Archive size limit reached')
            key=uuid.uuid4().hex;folder=self.runs/key;folder.mkdir(mode=0o700);self.active=key;self.cancel_requested=False
            state={'run_id':key,'status':'running','case_id':data['case_id'],'mode':data['mode'],'condition':data['condition'],'compute_profile':'cpu','started_at':time.time(),'kind':'live_computation','semantic_review':'pending'}
            save(folder/'state.json',state)
            threading.Thread(target=self.work,args=(key,state),daemon=True).start();return key
    def work(self,key,state):
        folder=self.runs/key;p=None
        try:
            env=dict(os.environ,HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1')
            with (folder/'console.log').open('wb') as log:
                with self.lock:
                    if self.cancel_requested:state['status']='cancelled';return
                    p=subprocess.Popen([self.cfg['python'],'-u',str(ROOT/'backend.py'),'--config',str(self.config_path),
                      '--out',str(folder),'--case',state['case_id'],'--mode',state['mode'],'--condition',state['condition']],
                      start_new_session=True,stdin=subprocess.DEVNULL,stdout=log,stderr=log,env=env)
                    self.process=p
                deadline=time.monotonic()+JOB_SECONDS
                while p.poll() is None:
                    if time.monotonic()>=deadline:
                        state['status']='timed_out';kill(p);break
                    size=sum(f.stat().st_size for f in folder.iterdir() if f.is_file() and not f.is_symlink())
                    if size>MAX_RUN_BYTES or shutil.disk_usage(folder).free<256*1024*1024:
                        state['status']='resource_limit';kill(p);break
                    time.sleep(.2)
                code=p.wait(timeout=5)
                if state['status']=='running':state['status']='cancelled' if self.cancel_requested else ('completed' if code==0 else 'failed')
                state['exit_code']=code
        except Exception as e:state.update(status='failed',error=type(e).__name__)
        finally:
            if p:kill(p) # Also removes owned descendants after abnormal leader exit.
            state['finished_at']=time.time();save(folder/'state.json',state)
            with self.lock:self.process=None;self.active=None
    def cancel(self,key):
        require(isinstance(key,str) and JOB.fullmatch(key) is not None,'Invalid run ID')
        with self.lock:
            if key!=self.active:raise ValueError('No matching active run')
            self.cancel_requested=True
            if self.process:kill(self.process)
    def snapshot(self,key):
        if not isinstance(key,str) or not JOB.fullmatch(key):raise ValueError('Invalid run ID')
        folder=self.runs/key
        if not folder.is_dir() or folder.is_symlink():raise ValueError('Run unavailable')
        result={}
        for name,label in [('state.json','state'),('result.json','result')]:
            p=folder/name
            if p.exists() and not p.is_symlink() and p.stat().st_size<8*1024*1024:
                try:result[label]=load(p)
                except (ValueError,OSError):pass
        p=folder/'events.jsonl'
        if p.exists() and not p.is_symlink() and p.stat().st_size<256*1024:
            result['events']=[]
            for line in p.read_text().splitlines():
                try:result['events'].append(decode(line))
                except (ValueError,OSError):pass
        # A restarted server cannot resume old live jobs silently.
        if result.get('state',{}).get('status')=='running' and self.active!=key:result['state']['status']='interrupted'
        result['effective_status']=result.get('state',{}).get('status','unavailable')
        result['snapshot_notice']='Job status is authoritative. An interrupted worker snapshot is retained as last observed, not completed.'
        return result
class Server(ThreadingMixIn,HTTPServer):
    daemon_threads=True;request_queue_size=8;allow_reuse_address=False
    def __init__(self,config,port):
        self.manager=Manager(config);self.token=secrets.token_urlsafe(32);self.slots=threading.BoundedSemaphore(8)
        super().__init__(('127.0.0.1',port),Handler)
        self.hosts={f'127.0.0.1:{self.server_port}',f'localhost:{self.server_port}'}
    def server_close(self):
        super().server_close()
        lock=getattr(self.manager,'archive_lock',None)
        if lock is not None:lock.close()
    def get_request(self):
        sock,addr=super().get_request();sock.settimeout(3);return sock,addr
    def process_request(self,request,address):
        if not self.slots.acquire(False):self.shutdown_request(request);return
        try:super().process_request(request,address)
        except BaseException:self.slots.release();raise
    def process_request_thread(self,request,address):
        try:super().process_request_thread(request,address)
        finally:self.slots.release()
class Handler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.0';server_version='FilterFlipLive';sys_version=''
    def log_message(self,*args):pass
    def reply(self,code,body,kind='application/json; charset=utf-8'):
        method=getattr(self,'command','UNKNOWN')
        path=getattr(self,'path','')
        route=('/api/runs' if path=='/api/runs' else '/api/cancel' if path=='/api/cancel' else
               'run-read' if path.startswith('/api/runs/') else 'other')
        if method=='POST' or code>=400:
            method=method if method in ('GET','HEAD','POST','PUT','PATCH','DELETE','OPTIONS','TRACE','CONNECT') else 'OTHER'
            self.server.manager.audit.record(method,route,code,getattr(self,'audit_run_id',None))
        self.close_connection=True;body=body if isinstance(body,bytes) else encoded(body)
        self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)))
        for k,v in HEADERS.items():self.send_header(k,v)
        self.end_headers()
        if self.command!='HEAD':self.wfile.write(body)
    def send_error(self,code,*args):self.reply(code,{'error':'Request rejected'})
    def guard(self,post=False):
        hosts=self.headers.get_all('Host') or [];origins=self.headers.get_all('Origin') or []
        if len(hosts)!=1 or hosts[0] not in self.server.hosts or len(origins)>1 or (origins and origins[0]!='http://'+hosts[0]):self.reply(403,{'error':'Origin or host rejected'});return False
        if self.headers.get('Sec-Fetch-Site') in ('cross-site','same-site'):self.reply(403,{'error':'Cross-origin request rejected'});return False
        if len(self.path)>512 or sum(len(k)+len(v) for k,v in self.headers.items())>8192:self.reply(431,{'error':'Request too large'});return False
        lengths=self.headers.get_all('Content-Length') or []
        if self.headers.get('Transfer-Encoding') or len(lengths)>1:self.reply(400,{'error':'Framing rejected'});return False
        if post:
            tokens=self.headers.get_all('X-Run-Token') or []
            if len(tokens)!=1 or not hmac.compare_digest(tokens[0].encode('utf-8'),self.server.token.encode('ascii')):self.reply(403,{'error':'Run token required'});return False
            if self.headers.get_all('Content-Type')!=['application/json'] or len(lengths)!=1 or not lengths[0].isdigit() or not 1<=int(lengths[0])<=1024:self.reply(400,{'error':'Invalid JSON body size'});return False
        elif lengths and lengths[0]!='0':self.reply(400,{'error':'Body not accepted'});return False
        return True
    def do_GET(self):
        if not self.guard():return
        m=self.server.manager
        try:
            static={'/':('index.html','text/html'),'/app.js':('app.js','text/javascript'),'/style.css':('style.css','text/css'),'/study.js':('study.js','text/javascript'),'/findings.js':('findings.js','text/javascript'),'/project.js':('project.js','text/javascript')}
            if self.path in static:
                name,kind=static[self.path];return self.reply(200,(ROOT/'static'/name).read_bytes(),kind+'; charset=utf-8')
            if self.path=='/semester-report.pdf':return self.reply(200,(ROOT/'documents/semester-report.pdf').read_bytes(),'application/pdf')
            if self.path=='/api/project':return self.reply(200,load(ROOT/'data/project.json',16*1024*1024))
            if self.path=='/api/findings':return self.reply(200,load(ROOT/'data/findings.json',16*1024*1024))
            if self.path=='/api/bootstrap':return self.reply(200,{'token':self.server.token,'active':m.active,'cases':[{'id':c['case_id'],'question':c['question'],'mitigation':c['case_id'] in m.benign,'challenge':c['case_id'] in m.approved,'trust':c['case_id'] in __import__('trust').catalog(),'source_qualification':c.get('source_qualification',''),'qualification':m.qualifications.get(c['case_id'],'')} for c in m.cases.values()]})
            if self.path.startswith('/api/study/'):
                from study import load_study
                return self.reply(200,load_study(self.path[len('/api/study/'):]))
            if self.path.startswith('/api/reference/'):
                cid=self.path[len('/api/reference/'):];return self.reply(200,m.cases[cid])
            if self.path.startswith('/api/runs/'):return self.reply(200,m.snapshot(self.path[len('/api/runs/'):]))
            self.reply(404,{'error':'Unknown route'})
        except (ValueError,KeyError):self.reply(404,{'error':'Unknown record'})
        except Exception:self.reply(500,{'error':'Local operation failed; inspect the launch terminal'})
    def do_POST(self):
        if not self.guard(True):return
        try:
            data=decode(self.rfile.read(int(self.headers['Content-Length'])))
            if not isinstance(data,dict):raise ValueError()
            if self.path=='/api/runs':
                self.audit_run_id=self.server.manager.start(data);return self.reply(202,{'run_id':self.audit_run_id})
            if self.path=='/api/cancel':
                if set(data)!={'run_id'}:raise ValueError()
                self.server.manager.cancel(data['run_id']);self.audit_run_id=data['run_id'];return self.reply(200,{'status':'cancellation_requested'})
            self.reply(404,{'error':'Unknown operation'})
        except RuntimeError as e:self.reply(409,{'error':str(e)})
        except (ValueError,TypeError,KeyError):self.reply(400,{'error':'Invalid request'})
        except Exception:self.reply(500,{'error':'Local operation failed; inspect the launch terminal'})
    def do_HEAD(self):self.do_GET()
    def reject(self):self.reply(405,{'error':'Method not allowed'})
    do_PUT=do_PATCH=do_DELETE=do_OPTIONS=do_TRACE=do_CONNECT=reject
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(ROOT/'config.local.json'));p.add_argument('--port',type=int,default=8767);a=p.parse_args()
    if not 1024<=a.port<=65535:p.error('Use a port between 1024 and 65535')
    os.umask(0o077);verify_release()
    server=Server(a.config,a.port);print(f'Live demo: http://127.0.0.1:{server.server_port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:
        if server.manager.active:server.manager.cancel(server.manager.active)
        until=time.monotonic()+8
        while server.manager.active and time.monotonic()<until:time.sleep(.05)
        server.server_close()
