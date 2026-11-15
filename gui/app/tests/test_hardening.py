"""Regression checks for config, verified loading, audit and offline archiving."""
import hashlib,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import safety,operations,archive_runs
class HardeningTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name);self.runs=self.p/'runs';self.runs.mkdir(mode=0o700)
  self.cfg={k:str(self.p/k) for k in ['package','encoder','ollama_models','ollama_binary','python']};self.cfg.update(runs=str(self.runs),compute_profile='cpu');self.config=self.p/'config.json';safety.save(self.config,self.cfg)
 def tearDown(self):self.tmp.cleanup()
 def test_private_config_accepted(self):self.assertEqual(safety.load_config(self.config),self.cfg)
 def test_group_read_or_write_config_refused(self):
  for mode in [0o640,0o664,0o644,0o666]:
   self.config.chmod(mode)
   with self.assertRaises(ValueError):safety.load_config(self.config)
 def test_config_link_refused(self):
  link=self.p/'link';link.symlink_to(self.config)
  with self.assertRaises((ValueError,OSError)):safety.load_config(link)
 def test_group_writable_parent_refused(self):
  self.p.chmod(0o770)
  with self.assertRaises(ValueError):safety.load_config(self.config)
  self.p.chmod(0o700)
 def test_config_wrong_owner_refused(self):
  with patch.object(safety.os,'getuid',return_value=os.getuid()+1):
   with self.assertRaises(ValueError):safety.load_config(self.config)
 def test_verified_loader_uses_the_hashed_bytes_after_path_changes(self):
  file=self.p/'retr.py';raw=b'VALUE=7\n';file.write_bytes(raw)
  real=safety.read
  def replaced(p,*args):
   data=real(p,*args);file.write_bytes(b'raise RuntimeError("replacement must not execute")\n');return data
  with patch.object(safety,'read',side_effect=replaced):module=safety.verified_module(file,hashlib.sha256(raw).hexdigest())
  self.assertEqual(module.VALUE,7)
 def test_verified_loader_rejects_mismatch_without_execution(self):
  file=self.p/'retr.py';file.write_text('raise RuntimeError("executed")')
  with self.assertRaisesRegex(ValueError,'identity'):safety.verified_module(file,'0'*64)
 def test_audit_rotation_is_private_and_bounded(self):
  log=operations.AuditLog(self.runs);log.MAX_BYTES=256
  for i in range(60):log.record('POST','/api/runs',403)
  files=list(self.runs.glob('security-events*'));self.assertEqual(len(files),3)
  for p in files:
   self.assertLessEqual(p.stat().st_size,256);self.assertEqual(p.stat().st_mode&0o077,0)
   for line in p.read_text().splitlines():self.assertEqual(set(json.loads(line)),{'time_utc','method','route','status','run_id'})
 def test_audit_link_does_not_overwrite_target(self):
  target=self.p/'target';target.write_text('preserve');(self.runs/'security-events.jsonl').symlink_to(target)
  log=operations.AuditLog(self.runs);log.record('POST','other',400);self.assertTrue(log.degraded);self.assertEqual(target.read_text(),'preserve')
 def terminal(self):
  key='a'*32;folder=self.runs/key;folder.mkdir();safety.save(folder/'state.json',{'run_id':key,'status':'completed'});(folder/'answer.txt').write_text('original evidence');return key,folder
 def test_archive_preview_does_not_move_evidence(self):
  key,f=self.terminal();d=self.p/'archive';archive_runs.archive(self.config,d,[key]);self.assertTrue(f.exists());self.assertFalse(d.exists())
 def test_archive_apply_preserves_evidence(self):
  key,f=self.terminal();before=(f/'answer.txt').read_bytes();d=self.p/'archive';archive_runs.archive(self.config,d,[key],True)
  self.assertFalse(f.exists());self.assertEqual((d/key/'answer.txt').read_bytes(),before);self.assertEqual(safety.load(d/'ARCHIVE_RECEIPT.json')['moved'],[key])
 def test_archive_refuses_running_server_lock(self):
  key,f=self.terminal();lock=operations.RunLock(self.runs)
  try:
   with self.assertRaises(ValueError):archive_runs.archive(self.config,self.p/'archive',[key],True)
   self.assertTrue(f.exists())
  finally:lock.close()
 def test_archive_refuses_nonterminal_or_link(self):
  key,f=self.terminal();safety.save(f/'state.json',{'run_id':key,'status':'running'})
  with self.assertRaises(ValueError):archive_runs.archive(self.config,self.p/'archive',[key],True)
  safety.save(f/'state.json',{'run_id':key,'status':'completed'});(f/'link').symlink_to(self.config)
  with self.assertRaises(ValueError):archive_runs.archive(self.config,self.p/'archive',[key],True)
 def test_archive_refuses_traversal_and_destination_reuse(self):
  with self.assertRaises(ValueError):archive_runs.archive(self.config,self.p/'archive',['../config'],True)
  key,_=self.terminal()
  with self.assertRaises(ValueError):archive_runs.archive(self.config,self.p,[key],True)
 def test_findings_count_and_scope(self):
  d=safety.load(safety.ROOT/'data/findings.json',16*1024*1024);self.assertEqual(len(d['primary']),8);self.assertEqual(len(d['trust']),12);self.assertEqual(sum(len(c['contexts']) for c in d['trust']),36)
  for c in d['trust']:
   self.assertEqual(set(x['condition'] for x in c['contexts']),{'C','BN1','PN1'})
   for x in c['contexts']:self.assertEqual(sum(p['kept'] for p in x['passages']),x['T_kept'])

class SecurityHTTPTests(unittest.TestCase):
 def setUp(self):
  import server,threading
  self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
  cfg={k:str(self.p/k) for k in ['package','encoder','ollama_binary','ollama_models','runs']};cfg.update(python=sys.executable,compute_profile='cpu');safety.save(self.p/'config.json',cfg)
  self.server=server.Server(self.p/'config.json',0);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
 def tearDown(self):self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()
 def req(self,path,body=None,token=None):
  import http.client
  c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=3);headers={'Content-Type':'application/json'}
  if token:headers['X-Run-Token']=token
  c.request('POST' if body is not None else 'GET',path,json.dumps(body) if body is not None else None,headers);r=c.getresponse();result=(r.status,r.read(),dict(r.getheaders()));c.close();return result
 def test_rejected_requests_logged_without_raw_secrets(self):
  self.assertEqual(self.req('/api/cancel',{'run_id':'private-body'},'PRIVATE-TOKEN')[0],403)
  self.assertEqual(self.req('/not-found-PRIVATE-PATH')[0],404)
  text=(self.p/'runs/security-events.jsonl').read_text();self.assertNotIn('PRIVATE',text);self.assertNotIn('private-body',text);self.assertIn('403',text);self.assertIn('404',text)
 def test_extra_cancel_fields_consistently_rejected(self):
  self.assertEqual(self.req('/api/cancel',{'run_id':'a'*32,'extra':1},self.server.token)[0],400)
 def test_new_route_headers_and_no_model_work(self):
  import server
  with patch.object(server.subprocess,'Popen',side_effect=AssertionError('No inference')):
   status,body,headers=self.req('/api/findings');self.assertEqual(status,200);self.assertEqual(len(json.loads(body)['trust']),12)
   self.assertEqual(headers['Cross-Origin-Opener-Policy'],'same-origin');self.assertIn('camera=()',headers['Permissions-Policy']);self.assertIsNone(self.server.manager.active)
