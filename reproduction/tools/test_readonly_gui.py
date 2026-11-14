"""Synthetic transport checks of the read-only wrapper; no research inference."""
import http.client,json,tempfile,threading,unittest
from pathlib import Path
from unittest.mock import patch
from serve_readonly_gui import create,BANNER,server
class ReadOnlyChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.s=create(Path(cls.tmp.name)/'new_work',0);cls.t=threading.Thread(target=cls.s.serve_forever,daemon=True);cls.t.start()
 @classmethod
 def tearDownClass(cls):cls.s.shutdown();cls.s.server_close();cls.t.join();cls.tmp.cleanup()
 def request(self,path,method='GET',data=None):
  c=http.client.HTTPConnection('127.0.0.1',self.s.server_port,timeout=3);c.request(method,path,None if data is None else json.dumps(data),{'Content-Type':'application/json','X-Run-Token':self.s.token});r=c.getresponse();b=r.read();c.close();return r.status,b
 def test_banner(self):
  status,b=self.request('/');self.assertEqual(status,200);self.assertIn(BANNER,b);self.assertIn(b'Semester walkthrough v2.5',b)
 def test_bootstrap_and_recorded_case(self):
  status,b=self.request('/api/bootstrap');d=json.loads(b);self.assertEqual(status,200);self.assertEqual(len(d['cases']),59);self.assertIsNone(d['active'])
  status,b=self.request('/api/reference/NanoNQ:test1009');self.assertEqual(status,200);self.assertEqual(json.loads(b)['expected_answer'],'Nicole Gale Anderson')
 def test_generation_blocked_before_worker(self):
  with patch.object(server.subprocess,'Popen',side_effect=AssertionError('No process permitted'))as p:
   status,b=self.request('/api/runs','POST',{'case_id':'NanoNQ:test1009','mode':'original','condition':'C,PN1'});self.assertEqual(status,409);self.assertIn(b'generation disabled',b);p.assert_not_called()
  self.assertEqual(list(self.s.manager.runs.iterdir()),[])
 def test_cancel_blocked(self):self.assertEqual(self.request('/api/cancel','POST',{'run_id':'a'*32})[0],409)
 def test_no_saved_fresh_run_fallback(self):self.assertEqual(self.request('/api/runs/'+'a'*32)[0],404)
if __name__=='__main__':unittest.main()
