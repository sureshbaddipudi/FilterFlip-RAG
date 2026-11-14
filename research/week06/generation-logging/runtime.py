"""Linux process cancellation and durable, hash-chained attempt accounting."""
import os
import selectors
import signal
import subprocess
import time
from pathlib import Path
from common import *

class Worker:
    def __init__(self, command, timeout):
        require(os.name=='posix','This development worker requires POSIX process groups')
        env=dict(os.environ,HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',PYTHONNOUSERSITE='1')
        self.process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
                                      start_new_session=True,env=env)
        self.buffer=b''
        try:
            require(self.receive(timeout).get('status')=='ready','Worker failed startup validation')
        except BaseException:self.close();raise
    def receive(self,timeout):
        deadline=time.monotonic()+timeout
        with selectors.DefaultSelector() as selector:
            selector.register(self.process.stdout,selectors.EVENT_READ)
            while b'\n' not in self.buffer:
                left=deadline-time.monotonic()
                if left<=0 or not selector.select(left):self.close();raise TimeoutError('Worker killed at deadline')
                chunk=os.read(self.process.stdout.fileno(),65536)
                require(bool(chunk),'Worker exited without a complete response');self.buffer+=chunk
                require(len(self.buffer)<=512*1024,'Worker response too large')
        line,self.buffer=self.buffer.split(b'\n',1)
        result=decode(line);require(isinstance(result,dict),'Invalid worker response');return result
    def request(self,job,timeout):
        try:
            self.process.stdin.write(canonical(job)+b'\n');self.process.stdin.flush()
            result=self.receive(timeout);require(result.get('status')=='ok','Worker fault: '+str(result.get('error_type','unknown')))
            return result
        except BaseException:self.close();raise
    def close(self):
        # Kill the owned group even if its leader exited before its children.
        try:os.killpg(self.process.pid,signal.SIGKILL)
        except ProcessLookupError:pass
        self.process.wait(timeout=5)
        for pipe in (self.process.stdin,self.process.stdout):
            if pipe and not pipe.closed:pipe.close()

class Journal:
    def __init__(self,path,identity,phase='filter'):
        require(phase in ('filter','generation'),'Unknown phase')
        self.phase=phase
        self.path=Path(path);self.events=[];self.last='0'*64
        if self.path.exists():
            raw=read(self.path)
            require(not raw or raw.endswith(b'\n'),'Truncated journal; preserve and investigate')
            for line in raw.splitlines():
                event=decode(line);h=event.pop('sha256')
                require(event['previous']==self.last and sha(canonical(event))==h,'Journal integrity mismatch')
                self.events.append(event);self.last=h
            require(self.events and self.events[0]['identity']==identity and self.events[0]['phase']==phase,'Run identity changed')
        else:self.append('identity',identity=identity,phase=phase)
        starts=sum(e['kind']=='session_start' for e in self.events)
        ends=sum(e['kind']=='session_end' for e in self.events)
        require(starts==ends,'Unfinished session; no blind resume after interruption')
        require(not any(e['kind']=='fault' for e in self.events),'Faulted run requires investigation/amendment')
        begun={e['id'] for e in self.events if e['kind']=='begin'}
        done={e['id'] for e in self.events if e['kind']=='done'}
        require(begun==done,'Uncertain attempt; no automatic retry')
        self.started=None
    def append(self,kind,**fields):
        event=dict(kind=kind,previous=self.last,**fields);digest=sha(canonical(event))
        with self.path.open('ab') as f:
            f.write(canonical(dict(event,sha256=digest))+b'\n');f.flush();os.fsync(f.fileno())
        self.events.append(event);self.last=digest
    def start(self):
        self.started=time.monotonic();self.append('session_start')
    def finish(self):
        self.append('session_end',seconds=time.monotonic()-self.started);self.started=None
    def remaining(self):
        used=sum(e['seconds'] for e in self.events if e['kind']=='session_end')
        if self.started is not None:used+=time.monotonic()-self.started
        limit=7200 if self.phase=='filter' else 14400
        require(used<limit,'Phase time budget exhausted')
        return limit-used
    def call(self,worker,job_id,job,force=False):
        require(job['op'] in ({'native','scores'} if self.phase=='filter' else {'generate'}),'Operation not permitted in phase')
        request_hash=sha(canonical(job))
        for e in self.events:
            if e['kind']=='done' and e['id']==job_id:
                require(e['request_hash']==request_hash,'Job identity changed');return e['response'],True
        if not force:
            for e in self.events:
                if e['kind']=='done' and e['request_hash']==request_hash:
                    return e['response'],True
        self.remaining()
        bounded_op='native' if self.phase=='filter' else 'generate'
        cap=1050 if self.phase=='filter' else 228
        attempts=sum(e['kind']=='begin' and e['op']==bounded_op for e in self.events)
        require(job['op']!=bounded_op or attempts<cap,'Phase attempt cap reached')
        self.append('begin',id=job_id,op=job['op'],request_hash=request_hash)
        try:
            response=worker.request(job,min(120 if self.phase=='filter' else 600,self.remaining()))
            if job['op']=='native':indices(response.get('kept'),len(job['texts']))
            require(type(response.get('seconds')) in (int,float) and response['seconds']>=0,'Invalid timing')
            self.append('done',id=job_id,request_hash=request_hash,response=response)
            return response,False
        except BaseException as error:
            self.append('fault',id=job_id,error_type=type(error).__name__)
            raise
