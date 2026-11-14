#!/usr/bin/env python3
"""Launch once as an owned logged workspace worker, with no automatic retry."""
import os,subprocess,sys,time
import run_task03 as r

def launch():
    r.validate_release();parent=r.ROOT.parent
    record=parent/'FilterFlip_Task03_Worker_2026-10-31.json';console=parent/'FilterFlip_Task03_Worker_2026-10-31.log'
    out=parent/'FilterFlip_Task03_Run_2026-10-31';status=parent/'FilterFlip_Task03_Pipeline_Status_2026-10-31.json'
    r.need(not any(p.exists() for p in [record,console,out,status]),'Existing execution evidence; inspect before any launch')
    os.umask(0o077);r.save_new(record,dict(status='launch_pending',release_manifest_sha256=r.sha(r.ROOT/'SHA256_MANIFEST.json')))
    with console.open('xb') as log:
        child=subprocess.Popen([sys.executable,'-B','-u',str(r.ROOT/'pipeline.py')],cwd=r.ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    state=dict(pid=child.pid,pgid=child.pid,release=str(r.ROOT),out=str(out),console=str(console),launched_unix=time.time(),release_manifest_sha256=r.sha(r.ROOT/'SHA256_MANIFEST.json'),stop_instruction='SIGTERM only this verified pipeline PID; it stops its child and owned service. Never stop system Ollama.',retry_policy='Single launch, no automatic retry')
    r.snapshot(record,state);print(__import__('json').dumps(state,indent=2))
if __name__=='__main__':launch()
