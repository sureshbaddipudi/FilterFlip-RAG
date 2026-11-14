#!/usr/bin/env python3
"""Start the single approved v3 queue as an inspectable, logged workspace worker."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import recover_answers as r


def main():
    plan,*_=r.validate_release()
    r.require_execution_authority(plan)
    root=r.ROOT.parent
    record=root/'FilterFlip_Week04_Recovery_v3_Worker_2026-10-31.json'
    console=root/'FilterFlip_Week04_Recovery_v3_Worker_2026-10-31.log'
    out=root/plan['recovery_output_name']
    if record.exists() or console.exists() or out.exists():raise ValueError('Worker/run evidence exists; inspect, never launch again blindly')
    os.umask(0o077)
    with record.open('x') as f:
        json.dump({'status':'launch_pending','release_manifest_sha256':r.digest(r.ROOT/'SHA256_MANIFEST.json'),'out':str(out)},f,indent=2);f.flush();os.fsync(f.fileno())
    with console.open('xb') as log:
        process=subprocess.Popen([sys.executable,'-B','-u',str(r.ROOT/'run_pipeline.py')],cwd=r.ROOT,
                                 stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    state={'pid':process.pid,'pgid':process.pid,'launched_unix':time.time(),'out':str(out),'console':str(console),
           'release_manifest_sha256':r.digest(r.ROOT/'SHA256_MANIFEST.json'),
           'mode':'single bounded workspace worker; no automatic relaunch/retry; inspect journal and exact process ownership',
           'stop_instruction':'Send SIGTERM only to this verified worker PID. Its handler records fault/closure and stops its owned model service. Do not stop system Ollama.'}
    temp=Path(str(record)+'.tmp');r.c.save_new(temp,state);os.replace(temp,record)
    print(json.dumps(state,indent=2))


if __name__=='__main__':main()
