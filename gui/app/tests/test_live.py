"""Synthetic HTTP/control tests. These do not execute research inference."""
import http.client,json,os,signal,subprocess,sys,tempfile,threading,unittest
from pathlib import Path
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server,backend

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=Mock();cls.m.active=None;cls.m.cases={'safe':{'case_id':'safe','question':'synthetic'}};cls.m.benign=set();cls.m.approved=set();cls.m.qualifications={}
        with patch.object(server,'Manager',return_value=cls.m):cls.s=server.Server('unused',0)
        cls.thread=threading.Thread(target=cls.s.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.s.shutdown();cls.s.server_close();cls.thread.join()
    def req(self,path,method='GET',data=None,extra=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.s.server_port,timeout=3)
        headers={'Content-Type':'application/json'}
        if extra:headers.update(extra)
        conn.request(method,path,body=None if data is None else json.dumps(data),headers=headers)
        r=conn.getresponse();body=r.read();conn.close();return r.status,body,dict(r.getheaders())
    def test_page_and_csp(self):
        code,body,h=self.req('/');self.assertEqual(code,200);self.assertIn(b'Run live comparison',body);self.assertIn("frame-ancestors 'none'",h['Content-Security-Policy'])
    def test_bootstrap(self):self.assertEqual(self.req('/api/bootstrap')[0],200)
    def test_bad_host(self):self.assertEqual(self.req('/',extra={'Host':'evil.example'})[0],403)
    def test_bad_origin(self):self.assertEqual(self.req('/',extra={'Origin':'https://evil.example'})[0],403)
    def test_cross_site(self):self.assertEqual(self.req('/',extra={'Sec-Fetch-Site':'cross-site'})[0],403)
    def test_csrf_missing(self):self.assertEqual(self.req('/api/runs','POST',{})[0],403)
    def test_csrf_wrong(self):self.assertEqual(self.req('/api/runs','POST',{}, {'X-Run-Token':'wrong'})[0],403)
    def test_large_body(self):self.assertEqual(self.req('/api/runs','POST',{'x':'a'*2000},{'X-Run-Token':self.s.token})[0],400)
    def test_unknown_file(self):
        for p in ['/server.py','/config.local.json','/../../etc/passwd','/%2e%2e/etc/passwd','/?file=/etc/passwd']:
            self.assertEqual(self.req(p)[0],404)
    def test_method(self):self.assertEqual(self.req('/','DELETE')[0],405)
    def test_start_routing(self):
        self.m.start.return_value='a'*32
        self.assertEqual(self.req('/api/runs','POST',{'case_id':'safe','mode':'original','condition':'C,PN1'},{'X-Run-Token':self.s.token})[0],202)
    def test_busy(self):
        self.m.start.side_effect=RuntimeError('busy')
        try:self.assertEqual(self.req('/api/runs','POST',{}, {'X-Run-Token':self.s.token})[0],409)
        finally:self.m.start.side_effect=None
    def test_cancel_routing(self):self.assertEqual(self.req('/api/cancel','POST',{'run_id':'a'*32},{'X-Run-Token':self.s.token})[0],200)
    def test_duplicate_host(self):
        c=http.client.HTTPConnection('127.0.0.1',self.s.server_port,timeout=3);c.putrequest('GET','/');c.putheader('Host','evil.example');c.endheaders();r=c.getresponse();self.assertEqual(r.status,403);r.read();c.close()
class ControlTests(unittest.TestCase):
    def test_no_arbitrary_browser_arguments(self):
        m=object.__new__(server.Manager);m.cases={'safe':{}};m.approved=set();m.benign=set()
        for data in [{'case_id':'evil','mode':'original','condition':'C,PN1'},{'case_id':'safe','mode':'original','condition':'C,PN1','command':'echo bad'},{'case_id':'safe','mode':'original','condition':'PN2'}]:
            with self.assertRaises(ValueError):m.start(data)
    def test_invalid_run_paths(self):
        m=object.__new__(server.Manager)
        for key in ['../x','a'*31,'b'*33,'not-a-run']:
            with self.assertRaises(ValueError):m.snapshot(key)
    def test_cancel_rejects_invalid_or_inactive_run(self):
        m=object.__new__(server.Manager);m.lock=threading.Lock();m.active=None;m.cancel_requested=False
        for key in [None,[],{},'','../x','a'*31,'A'*32,'a'*32]:
            with self.subTest(key=key):
                with self.assertRaises(ValueError):m.cancel(key)
                self.assertFalse(m.cancel_requested)
    def test_truncation_not_success(self):
        self.assertEqual(backend.response_status({'done':True,'done_reason':'length','message':{'content':'partial'}}),'truncated')
        self.assertEqual(backend.response_status({'done':False,'message':{}}),'malformed')
        self.assertEqual(backend.response_status({'done':True,'done_reason':'stop','message':{'content':'fresh'},'eval_count':1}),'ok')
    def test_owned_process_cancellation(self):
        p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'],start_new_session=True)
        server.kill(p);self.assertIsNotNone(p.poll())
    def test_frozen_request(self):
        r=backend.request('synthetic',['one','two']);self.assertEqual(r['options']['num_predict'],128);self.assertIn('one\n\ntwo',r['messages'][1]['content'])
if __name__=='__main__':unittest.main()
