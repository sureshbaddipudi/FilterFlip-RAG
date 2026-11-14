#!/usr/bin/env python3
"""One generation invocation followed by one offline audit; no automatic retries."""
import os,signal,subprocess,sys,time
import run_task03 as r

def pipeline(root=r.ROOT,spawn=subprocess.Popen):
    r.validate_release(root);parent=root.parent
    status=parent/'FilterFlip_Task03_Pipeline_Status_2026-10-31.json'
    r.need(not status.exists(),'Pipeline status exists; inspect, never relaunch automatically')
    state=dict(status='starting',started_unix=time.time(),retry_policy='No automatic retry or generation relaunch');child=None
    def save():r.snapshot(status,state)
    def halt(signum,frame):
        signal.signal(signal.SIGTERM,signal.SIG_IGN)
        if child and child.poll() is None:
            child.terminate()
            try:child.wait(timeout=20)
            except subprocess.TimeoutExpired:child.kill();child.wait(timeout=10)
        raise InterruptedError('Verified pipeline interrupted; inspect saved attempts')
    signal.signal(signal.SIGTERM,halt)
    try:
        state['status']='generating';save()
        out=parent/'FilterFlip_Task03_Run_2026-10-31';audit=parent/'FilterFlip_Task03_Final_Audit_2026-10-31'
        child=spawn([sys.executable,'-B','-u',str(root/'run_task03.py'),'--out',str(out)],cwd=root,stdin=subprocess.DEVNULL)
        state['runner_pid']=child.pid;save()
        r.need(child.wait(timeout=7230)==0,'Generation stopped; preserve evidence, no retry')
        state['status']='auditing';save()
        child=spawn([sys.executable,'-B',str(root/'audit_task03.py'),'--run',str(out),'--out',str(audit)],cwd=root,stdin=subprocess.DEVNULL)
        r.need(child.wait(timeout=120)==0,'Offline audit stopped; generation is not repeated')
        state.update(status='complete',finished_unix=time.time(),audit=str(audit));save()
    except BaseException as error:
        if child and child.poll() is None:
            child.terminate()
            try:child.wait(timeout=20)
            except subprocess.TimeoutExpired:child.kill();child.wait(timeout=10)
        state.update(status='stopped_requires_inspection',error_type=type(error).__name__,error=str(error),finished_unix=time.time());save();raise
if __name__=='__main__':pipeline()
