"""Exercise actual Manager process lifecycle with synthetic local workers, never models."""
import contextlib,json,sys,tempfile,threading,time,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server,safety

class LifecycleTests(unittest.TestCase):
    def manager(self,root):
        m=object.__new__(server.Manager);m.runs=root/'runs';m.runs.mkdir();m.config_path=root/'config.json';m.config_path.write_text('{}')
        m.cfg={'python':sys.executable};m.cases={'safe':{}};m.approved=set();m.benign=set()
        m.lock=threading.Lock();m.active=None;m.process=None;m.cancel_requested=False
        return m
    def wait(self,m):
        until=time.monotonic()+6
        while m.active and time.monotonic()<until:time.sleep(.02)
        self.assertIsNone(m.active)
    def run_fixture(self,script,callback=None,**limits):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'backend.py').write_text(script);m=self.manager(root)
            with patch.object(server,'ROOT',root),(patch.multiple(server,**limits) if limits else contextlib.nullcontext()):
                key=m.start({'case_id':'safe','mode':'original','condition':'C,PN1'})
                try:
                    if callback:callback(m,key)
                    self.wait(m);return m.snapshot(key)
                finally:
                    if m.active:m.cancel(m.active);self.wait(m)
    def test_timeout_becomes_terminal(self):
        snap=self.run_fixture('import time; time.sleep(30)',JOB_SECONDS=.3)
        self.assertEqual(snap['effective_status'],'timed_out');self.assertIn('finished_at',snap['state'])
    def test_resource_limit_preserves_partial_output(self):
        script="import pathlib,sys,time; p=pathlib.Path(sys.argv[sys.argv.index('--out')+1]); (p/'partial.txt').write_text('x'*1024); time.sleep(30)"
        snap=self.run_fixture(script,MAX_RUN_BYTES=512)
        self.assertEqual(snap['effective_status'],'resource_limit')
    def test_cancel_and_second_job_refusal(self):
        def callback(m,key):
            with self.assertRaises(RuntimeError):m.start({'case_id':'safe','mode':'original','condition':'C,PN1'})
            m.cancel(key)
        snap=self.run_fixture('import time; time.sleep(30)',callback)
        self.assertEqual(snap['effective_status'],'cancelled')
    def test_failed_worker_does_not_become_completed(self):
        snap=self.run_fixture('raise RuntimeError("synthetic fault")')
        self.assertEqual(snap['effective_status'],'failed');self.assertNotEqual(snap['state']['exit_code'],0)

if __name__=='__main__':unittest.main()
