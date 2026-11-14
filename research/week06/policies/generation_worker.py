"""Owned local Ollama daemon: no shared-service cancellation or arbitrary URLs."""
import argparse
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from common import *
from answer_requests import MODEL,DIGEST,OPTIONS,SYSTEM

PORT=11435
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise ValueError('Redirects are not permitted')

def validate_request(req):
    require(set(req)=={'model','stream','options','messages'},'Unexpected request fields')
    require(req['model']==MODEL and req['stream'] is False and req['options']==OPTIONS,'Unfrozen model settings')
    require(len(req['messages'])==2 and req['messages'][0]=={'role':'system','content':SYSTEM},'Unfrozen system message')
    require(set(req['messages'][1])=={'role','content'} and req['messages'][1]['role']=='user' and isinstance(req['messages'][1]['content'],str),'Invalid user message')

def validate_response(response,estimated):
    require(response.get('done') is True and response.get('done_reason')=='stop','Incomplete/truncated answer')
    answer=response.get('message',{}).get('content');require(isinstance(answer,str) and answer.strip(),'Empty answer')
    count=response.get('prompt_eval_count')
    require(type(count) is int and abs(count-estimated)<=16,'Prompt-token mismatch')
    require(count+OPTIONS['num_predict']+64<=OPTIONS['num_ctx'],'Context window exceeded')
    return answer

def main():
    p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--binary-sha',required=True);p.add_argument('--models',required=True);a=p.parse_args()
    require(sha(read(a.binary,1024*1024*1024))==a.binary_sha,'Ollama binary changed')
    # Refuse to connect to or stop an existing service on this dedicated port.
    with socket.socket() as probe:
        probe.settimeout(.5);require(probe.connect_ex(('127.0.0.1',PORT))!=0,'Dedicated port is already occupied')
    env=dict(os.environ,OLLAMA_HOST=f'127.0.0.1:{PORT}',OLLAMA_MODELS=str(Path(a.models).resolve()),
             OLLAMA_NUM_PARALLEL='1',OLLAMA_MAX_LOADED_MODELS='1',OLLAMA_NO_CLOUD='1')
    # Inherits this worker's process group; supervisor kills the entire owned group on timeout.
    daemon=subprocess.Popen([str(Path(a.binary).resolve()),'serve'],env=env,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    op=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
    def api(endpoint,payload=None,timeout=10):
        require(endpoint in ('version','tags','chat'),'Unknown API operation')
        req=urllib.request.Request(f'http://127.0.0.1:{PORT}/api/'+endpoint,
          data=None if payload is None else canonical(payload),headers={'Content-Type':'application/json'})
        with op.open(req,timeout=timeout) as response:raw=response.read(2*1024*1024+1)
        require(len(raw)<=2*1024*1024,'Oversized API response');result=decode(raw)
        require(not result.get('error'),'Local API error');return result
    def identity():
        require(daemon.poll() is None,'Owned daemon exited')
        require(api('version')=={'version':'0.34.2'},'Ollama version differs')
        matches=[m for m in api('tags').get('models',[]) if m.get('name')==MODEL]
        require(len(matches)==1 and matches[0]['digest']==DIGEST,'Served model digest differs')
    try:
        deadline=time.monotonic()+30
        while True:
            try:identity();break
            except urllib.error.URLError:
                require(daemon.poll() is None and time.monotonic()<deadline,'Owned daemon unavailable')
                time.sleep(.1)
        print(json.dumps({'status':'ready','port':PORT}),flush=True)
        while True:
            raw=sys.stdin.buffer.readline(512*1024+1)
            if not raw:return
            try:
                require(len(raw)<=512*1024,'Oversized generation job');job=decode(raw)
                require(set(job)=={'op','request','estimated_tokens'} and job['op']=='generate','Invalid generation job')
                validate_request(job['request']);estimated=job['estimated_tokens']
                require(type(estimated) is int and 0<estimated and estimated+128+64<=4096,'Request exceeds token budget')
                identity();started=time.monotonic();response=api('chat',job['request'],timeout=590);identity()
                answer=validate_response(response,estimated)
                print(json.dumps({'status':'ok','answer':answer,'raw_response':response,'seconds':time.monotonic()-started},allow_nan=False),flush=True)
            except Exception as error:
                print(json.dumps({'status':'fault','error_type':type(error).__name__}),flush=True);return
    finally:
        if daemon.poll() is None:
            daemon.terminate()
            try:daemon.wait(timeout=3)
            except subprocess.TimeoutExpired:daemon.kill();daemon.wait(timeout=3)

if __name__=='__main__':
    try:main()
    except Exception as error:
        print(json.dumps({'status':'fault','error_type':type(error).__name__,'error':str(error)[:300]}),flush=True);sys.exit(1)
