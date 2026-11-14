#!/usr/bin/env python3
"""Run the single bounded recovery and its offline audit without a chat process handle."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import recover_answers as r


def main():
    plan,*_=r.validate_release();r.require_execution_authority(plan)
    root=r.ROOT.parent
    status=root/'FilterFlip_Week04_Recovery_v3_Pipeline_Status_2026-10-31.json'
    if status.exists():raise ValueError('Pipeline status exists; inspect before any relaunch')
    child=None;state={'status':'starting','started_unix':time.time(),'generation_retry_policy':'No automatic retry or relaunch'}
    def save():
        temp=Path(str(status)+'.tmp');r.c.save_new(temp,state);os.replace(temp,status)
    def stop(signum,frame):
        signal.signal(signal.SIGTERM,signal.SIG_IGN)
        if child and child.poll() is None:
            child.terminate()
            try:child.wait(timeout=30)
            except subprocess.TimeoutExpired:child.kill();child.wait(timeout=10)
        raise InterruptedError('Operator stopped verified pipeline; preserve evidence, no automatic retry')
    signal.signal(signal.SIGTERM,stop)
    try:
        state['status']='generating';save()
        child=subprocess.Popen([sys.executable,'-B','-u',str(r.ROOT/'recover_answers.py'),'--out',str(root/plan['recovery_output_name'])],cwd=r.ROOT,stdin=subprocess.DEVNULL)
        state['runner_pid']=child.pid;save()
        result=child.wait(timeout=plan['new_active_seconds_cap']+60)
        if result:raise RuntimeError('Recovery stopped with exit code '+str(result)+'; inspect preserved evidence')
        state['status']='auditing';save()
        audit=root/'FilterFlip_Week04_Recovery_Final_Audit_v3_2026-10-31'
        child=subprocess.Popen([sys.executable,'-B',str(r.ROOT/'audit_week04_recovery_v3.py'),'--release',str(r.ROOT),'--run',str(root/plan['recovery_output_name']),'--out',str(audit)],cwd=r.ROOT,stdin=subprocess.DEVNULL)
        if child.wait(timeout=120):raise RuntimeError('Offline final audit failed; generation is not repeated')
        state.update(status='complete',audit=str(audit),finished_unix=time.time());save()
        print('Recovery queue and offline final audit finished. Human semantic review remains pending.',flush=True)
    except BaseException as error:
        if child and child.poll() is None:
            child.terminate()
            try:child.wait(timeout=30)
            except subprocess.TimeoutExpired:child.kill();child.wait(timeout=10)
        state.update(status='stopped_requires_inspection',error_type=type(error).__name__,error=str(error),finished_unix=time.time());save()
        raise


if __name__=='__main__':main()
