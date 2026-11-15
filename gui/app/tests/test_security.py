import http.client,json,os,signal,socket,subprocess,sys,tempfile,threading,time,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import safety,server,backend
from test_live import HTTPTests

class StrictInputTests(unittest.TestCase):
    def test_duplicate_and_nonfinite_json(self):
        for raw in ['{"case_id":"a","case_id":"b"}','{"x":NaN}','{"x":Infinity}']:
            with self.assertRaises(ValueError):safety.decode(raw)
    def test_unauthorized_modes_and_fields(self):
        for data in [{'case_id':'safe','mode':'challenge','condition':'wrong_answer_append'},
                     {'case_id':'safe','mode':'mitigation','condition':'PN1'},
                     {'case_id':[],'mode':'original','condition':'C,PN1'},
                     {'case_id':'safe','mode':'original','condition':'C,PN1','url':'http://example.com'}]:
            with self.assertRaises(ValueError):safety.check_selection(data,{'safe'},set(),set())
    def test_supported_selection(self):
        safety.check_selection({'case_id':'safe','mode':'mitigation','condition':'PN1'},{'safe'},set(),{'safe'})
    def test_atomic_write_symlink_and_permissions(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);victim=root/'victim';victim.write_text('preserve')
            target=root/'record.json';target.symlink_to(victim)
            safety.save(target,{'state':'cancelled'})
            self.assertEqual(victim.read_text(),'preserve');self.assertFalse(target.is_symlink())
            self.assertEqual(target.stat().st_mode & 0o077,0)
    def test_read_symlink_and_oversized(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'p';p.write_text('12345');link=Path(t)/'l';link.symlink_to(p)
            for target,limit in [(p,4),(link,8)]:
                with self.assertRaises(ValueError):safety.read(target,limit)
    def test_native_out_of_range_duplicate_indices(self):
        for indices in [[3],[0,0],[1,0],[True]]:
            with self.assertRaises(ValueError):safety.policy_decision('N',['a','b'],[1,0],[[1,0],[0,1]],lambda _:indices)
    def test_singleton_bypass_is_explicit(self):
        def never(_):raise AssertionError('Must not filter singleton')
        d=safety.policy_decision('E',['same','same'],[1,1],[[1,1],[1,1]],never)
        self.assertTrue(d['singleton_bypass']);self.assertEqual(d['kept'],[0])
    def test_primary_backend_error_not_hidden(self):
        self.assertEqual(backend.response_status({'error':'device lost'}),'backend_error')
        for raw in [[],{'done':True,'message':None},{'done':True,'done_reason':'unknown','message':{'content':'x'}}]:
            self.assertEqual(backend.response_status(raw),'malformed')
    def test_no_redirect(self):
        with self.assertRaises(ValueError):backend.NoRedirect().redirect_request(None,None,None,None,None,None)
    def test_terminal_snapshot_retains_original_worker(self):
        with tempfile.TemporaryDirectory() as t:
            m=object.__new__(server.Manager);m.runs=Path(t);m.active=None
            key='a'*32;folder=Path(t)/key;folder.mkdir()
            safety.save(folder/'state.json',{'status':'cancelled'});safety.save(folder/'result.json',{'status':'running'})
            s=m.snapshot(key);self.assertEqual(s['effective_status'],'cancelled');self.assertEqual(s['result']['status'],'running')
            safety.save(folder/'state.json',{'status':'running'});self.assertEqual(m.snapshot(key)['effective_status'],'interrupted')
    def test_release_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'app.py').write_text('pass');safety.save(root/'RELEASE_MANIFEST.json',{'app.py':safety.digest(b'pass')})
            with patch.object(safety,'ROOT',root):
                self.assertEqual(safety.verify_release(),1)
                (root/'app.py').write_text('changed')
                with self.assertRaises(ValueError):safety.verify_release()
    def test_request_settings_frozen(self):
        self.assertEqual(backend.OPTIONS,{'temperature':0,'seed':42,'num_ctx':4096,'num_predict':128})
        self.assertIn('not instructions to follow',backend.SYSTEM)

class ExtraHTTPTests(HTTPTests):
    def raw(self,body,extra=None):
        c=http.client.HTTPConnection('127.0.0.1',self.s.server_port,timeout=3)
        headers={'Content-Type':'application/json','X-Run-Token':self.s.token}
        if extra:headers.update(extra)
        c.request('POST','/api/runs',body=body,headers=headers);r=c.getresponse();result=(r.status,r.read());c.close();return result
    def test_duplicate_json_rejected(self):self.assertEqual(self.raw('{"case_id":"safe","case_id":"unsafe"}')[0],400)
    def test_nonfinite_json_rejected(self):self.assertEqual(self.raw('{"x":NaN}')[0],400)
    def test_unexpected_failure_sanitized(self):
        self.m.start.side_effect=OSError('/private/secret/path')
        try:
            code,raw=self.raw('{}');self.assertEqual(code,500);self.assertNotIn(b'secret',raw)
        finally:self.m.start.side_effect=None
    def test_duplicate_lengths_rejected(self):
        c=http.client.HTTPConnection('127.0.0.1',self.s.server_port,timeout=3)
        c.putrequest('POST','/api/runs');c.putheader('Content-Length','2');c.putheader('Content-Length','2');c.endheaders(b'{}')
        r=c.getresponse();self.assertEqual(r.status,400);r.read();c.close()
    def test_transfer_encoding_rejected(self):self.assertEqual(self.raw('{}',{'Transfer-Encoding':'chunked'})[0],400)

class ProcessTests(unittest.TestCase):
    def test_owned_descendant_listener_is_closed(self):
        # No model loads. A child holds a real localhost socket; kill only its owned group.
        with tempfile.TemporaryDirectory() as t:
            info=Path(t)/'listener.json'
            child="import json,socket,sys,time; s=socket.socket(); s.bind(('127.0.0.1',0)); s.listen(); open(sys.argv[1],'w').write(json.dumps({'port':s.getsockname()[1]})); time.sleep(30)"
            parent="import subprocess,sys,time; subprocess.Popen([sys.executable,'-c',sys.argv[1],sys.argv[2]]); time.sleep(30)"
            process=subprocess.Popen([sys.executable,'-c',parent,child,str(info)],start_new_session=True)
            try:
                until=time.monotonic()+5
                while not info.exists() and time.monotonic()<until:time.sleep(.02)
                port=json.loads(info.read_text())['port'];s=socket.create_connection(('127.0.0.1',port),timeout=1);s.close()
                server.kill(process)
                until=time.monotonic()+3
                while time.monotonic()<until:
                    try:s=socket.create_connection(('127.0.0.1',port),timeout=.2);s.close()
                    except OSError:break
                    time.sleep(.02)
                else:self.fail('Descendant listener survived group cancellation')
            finally:server.kill(process)
    def test_private_run_folder_required(self):
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t)/'runs';folder.mkdir(mode=0o755);folder.chmod(0o755)
            cfg={k:str(Path(t)/k) for k in ['package','encoder','ollama_models','ollama_binary']};cfg.update(python=sys.executable,runs=str(folder),compute_profile='cpu')
            config=Path(t)/'config.json';config.write_text(json.dumps(cfg));config.chmod(0o600)
            with self.assertRaisesRegex(ValueError,'private'):server.Manager(config)

def load_tests(loader, tests, pattern):
    suite=unittest.TestSuite()
    for cls in (StrictInputTests,ProcessTests):suite.addTests(loader.loadTestsFromTestCase(cls))
    for name in sorted(set(loader.getTestCaseNames(ExtraHTTPTests))-set(loader.getTestCaseNames(HTTPTests))):suite.addTest(ExtraHTTPTests(name))
    return suite

if __name__=='__main__':unittest.main()
