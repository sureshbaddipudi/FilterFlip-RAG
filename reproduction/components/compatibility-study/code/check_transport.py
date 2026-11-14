#!/usr/bin/env python3
"""Synthetic loopback model-API transport checks only. Never starts Ollama or loads weights."""
from pathlib import Path
import argparse,http.server,json,os,sys,threading,urllib.request
P=Path(__file__).resolve().parent.parent

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--profile',choices=['baseline','candidate'],required=True);ap.add_argument('--label',choices=['normal','optimized'],required=True);a=ap.parse_args();paths=json.loads((P/'AUTHORING_PATHS.json').read_text());sys.path.insert(0,paths[a.profile+'_app']);import backend,safety
 contexts=json.loads((Path(paths['task09_work'])/'profile_runs'/a.profile/'CONTEXTS.json').read_text());sample=contexts[0]['requests']['U'];request=sample['request'];body=backend.canonical(request);seen=[];checks=[]
 def record(name,ok,detail):checks.append({'check':name,'passed':bool(ok),'detail':detail})
 def fixture(kind):return {'model':'qwen2.5:3b','done':True,'done_reason':kind,'message':{'role':'assistant','content':'SYNTHETIC TRANSPORT FIXTURE — not a research answer'},'eval_count':1,'prompt_eval_count':sample['estimated_tokens']}
 class Handler(http.server.BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def do_POST(self):
   raw=self.rfile.read(int(self.headers['Content-Length']));seen.append((self.path,raw))
   if self.path=='/redirect':self.send_response(302);self.send_header('Location','/should-not-follow');self.end_headers();return
   payload=fixture('length' if self.path=='/truncated' else 'stop')
   if self.path=='/malformed':payload.pop('done')
   raw=b'x'*(2*1024*1024+1) if self.path=='/oversized' else backend.canonical(payload);self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
  def do_GET(self):seen.append((self.path,b''));self.send_response(500);self.end_headers()
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),backend.NoRedirect());captures={}
 try:
  for endpoint in ['/api/chat','/truncated','/malformed']:
   req=urllib.request.Request('http://127.0.0.1:'+str(server.server_port)+endpoint,data=body,headers={'Content-Type':'application/json'})
   with opener.open(req,timeout=5) as r:raw=r.read(2*1024*1024+1)
   captures[endpoint]={'raw_utf8':raw.decode(),'status':backend.response_status(safety.decode(raw))}
  record('canonical_request_bytes_transmitted_unchanged',all(raw==body for _,raw in seen),{'requests':len(seen),'request_sha256':backend.sha(body)})
  record('valid_stop_response_recognized',captures['/api/chat']['status']=='ok','Synthetic fixture only')
  record('raw_response_capture_retained',captures['/api/chat']['raw_utf8']==backend.canonical(fixture('stop')).decode(),'Original fixture bytes captured before decode')
  record('truncation_not_success',captures['/truncated']['status']=='truncated','Synthetic length stop')
  record('malformed_response_not_success',captures['/malformed']['status']=='malformed','Synthetic missing done flag')
  req=urllib.request.Request('http://127.0.0.1:'+str(server.server_port)+'/redirect',data=body)
  try:opener.open(req,timeout=5);blocked=False
  except ValueError:blocked=True
  record('redirect_refused_without_following',blocked and not any(path=='/should-not-follow' for path,_ in seen),'Actual original NoRedirect class and urllib opener')
  req=urllib.request.Request('http://127.0.0.1:'+str(server.server_port)+'/oversized',data=body)
  with opener.open(req,timeout=5) as r:raw=r.read(2*1024*1024+1)
  try:backend.require(len(raw)<=2*1024*1024,'Oversized model response');bounded=False
  except ValueError:bounded=True
  record('model_response_size_bound_refuses_overflow',bounded and len(raw)==2*1024*1024+1,'Synthetic 2 MiB +1 response; no model called')
 finally:server.shutdown();server.server_close();thread.join()
 report={'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','profile':a.profile,'mode':a.label,'checks':checks,'captures':captures,'research_generation_attempts':0,'Ollama_processes_started':0,'scope':'Synthetic local HTTP fixture using actual request serialization/status/redirect code; not a live Qwen outcome or full nested backend worker integration.'};dest=P/'results/transport';dest.mkdir(exist_ok=True);(dest/(a.profile+'_'+a.label+'.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'profile':a.profile,'mode':a.label,'checks':len(checks)}));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
