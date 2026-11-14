"""Task-13 read-only verification of existing v2.5 views. Model starts are blocked."""
import argparse,json,os,sys,threading
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(P/'components/task12/app'))
import server
BANNER=b'<p class="notice">TASK 13 READ-ONLY VERIFICATION: recorded evidence only. Model generation and cancellation are disabled. No fresh answers are computed.</p>'
class ReadOnlyManager(server.Manager):
 def start(self,data):raise RuntimeError('Read-only verification: model generation disabled')
 def cancel(self,key):raise RuntimeError('Read-only verification: no model process exists')
class ReadOnlyHandler(server.Handler):
 def reply(self,code,body,kind='application/json; charset=utf-8'):
  if isinstance(body,bytes)and kind.startswith('text/html'):body=body.replace(b'<body>',b'<body>'+BANNER,1).replace('Local CPU · Fresh inference'.encode(),'Read-only · Models disabled'.encode())
  return super().reply(code,body,kind)
def create(work,port):
 work=Path(work).resolve()
 if work.exists()or work.is_relative_to(P)or P.is_relative_to(work):raise ValueError('Choose a new work folder outside the sealed packet')
 work.mkdir(parents=True,mode=0o700)
 cfg={'python':str(Path(sys.executable).resolve()),'compute_profile':'cpu','runs':str(work/'empty_runs')}
 for k in ('package','encoder','ollama_binary','ollama_models'):cfg[k]=str(work/('UNUSED_'+k))
 config=work/'READONLY_CONFIG.json';config.write_text(json.dumps(cfg,indent=2)+'\n');server.verify_release()
 # Only this verification process is patched. Frozen application files are unchanged.
 with patch.object(server,'Manager',ReadOnlyManager):srv=server.Server(config,port)
 srv.RequestHandlerClass=ReadOnlyHandler
 return srv

def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--port',type=int,default=8769);p.add_argument('--seconds',type=int,default=1800);a=p.parse_args()
 if not 1024<=a.port<=65535 or not 1<=a.seconds<=1800:p.error('Use port 1024–65535 and duration 1–1800 seconds')
 os.umask(0o077);srv=create(a.work,a.port);timer=threading.Timer(a.seconds,srv.shutdown);timer.daemon=True;timer.start()
 print(f'Read-only verification: http://127.0.0.1:{srv.server_port} — models disabled; stops after {a.seconds} seconds',flush=True)
 try:srv.serve_forever()
 except KeyboardInterrupt:pass
 finally:timer.cancel();srv.server_close()
if __name__=='__main__':main()
