"""Synthetic browser start/stop fixture: no production backend or model can be launched."""
import argparse,json,os,subprocess,sys,threading,time
from pathlib import Path
from unittest.mock import patch
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'app'))
import server,safety
p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--port',type=int,default=8771);a=p.parse_args()
w=a.work.resolve()
if w.exists() or w.is_relative_to(R) or R.is_relative_to(w):raise SystemExit('Choose new external fixture work')
os.umask(0o077);w.mkdir(parents=True);cfg={k:str(w/('UNUSED_'+k)) for k in ['package','encoder','ollama_binary','ollama_models']};cfg.update(python=sys.executable,runs=str(w/'runs'),compute_profile='cpu');safety.save(w/'config.json',cfg)
worker=w/'synthetic_worker.py';worker.write_text('''import json,pathlib,sys,time
args=sys.argv;out=pathlib.Path(args[args.index('--out')+1]);co=args[args.index('--condition')+1]
r={'kind':'SYNTHETIC_CONTROL_TEST_ONLY','status':'running','conditions':{co:{'retrieved':[{'text':'SYNTHETIC passage; not a research response.'}],'policies':{'U':{'kept':[0],'representatives':[0]},'N':{'kept':[],'representatives':[0]}},'answers':{'U':{'text':'SYNTHETIC answer, not Qwen output.','status':'synthetic','seconds':0},'N':{'text':'SYNTHETIC partial export check.','status':'synthetic','seconds':0}}}},'generation_attempts':0}
if args[args.index('--mode')+1]=='trust':
 c=r['conditions'][co];c['policies']['T']=c['policies'].pop('N');c['answers']['T']=c['answers'].pop('N');c['policies']['T']['source']='synthetic_filter_only'
(out/'result.json').write_text(json.dumps(r));time.sleep(60)
''')
original=subprocess.Popen
# The actual production Manager and HTTP handlers remain in use. Only the worker path is replaced.
def synthetic_only(argv,*args,**kwargs):
 if len(argv)<3 or argv[2]!=str(R/'app/backend.py'):raise RuntimeError('Unexpected child refused in synthetic fixture')
 argv=list(argv);argv[2]=str(worker);return original(argv,*args,**kwargs)
class Handler(server.Handler):
 def reply(self,code,body,kind='application/json; charset=utf-8'):
  if isinstance(body,bytes) and kind.startswith('text/html'):body=body.replace(b'<body>',b'<body><p class="notice">SYNTHETIC BROWSER CONTROL TEST ONLY. No models or research inference.</p>',1)
  return super().reply(code,body,kind)
safety.verify_release()
with patch.object(server.subprocess,'Popen',synthetic_only):
 s=server.Server(w/'config.json',a.port);s.RequestHandlerClass=Handler
 timer=threading.Timer(180,s.shutdown);timer.daemon=True;timer.start()
 print('Synthetic fixture only: http://127.0.0.1:'+str(s.server_port),flush=True)
 try:s.serve_forever()
 except KeyboardInterrupt:pass
 finally:
  timer.cancel()
  if s.manager.active:s.manager.cancel(s.manager.active)
  until=time.monotonic()+8
  while s.manager.active and time.monotonic()<until:time.sleep(.05)
  s.server_close()
