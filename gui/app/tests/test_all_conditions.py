"""Model-free regression checks for all-condition evidence and live job routing."""
import hashlib,http.client,json,sys,tempfile,threading,time,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server,safety,study,configure
class StudyTests(unittest.TestCase):
 def test_all_531_saved_contexts_and_2124_logical_answer_panel_positions(self):
  catalog=safety.load(study.ROOT/'data/STUDY_CATALOG.json');self.assertEqual(len(catalog),59)
  contexts=answers=0
  for cid in catalog:
   d=study.load_study(cid)
   self.assertEqual(set(d['conditions']),set(safety.STUDY_CONDITIONS))
   for co,c in d['conditions'].items():
    contexts+=1;self.assertEqual(len(c['passages']),5)
    self.assertEqual(c['kept_indices'],[i for i,p in enumerate(c['passages']) if p['kept']])
    self.assertEqual(set(c['kept_indices'])|set(c['removed_indices']),set(range(5)))
    for p in c['passages']:self.assertEqual(hashlib.sha256(p['text'].encode()).hexdigest(),p['text_sha256'])
    for mode,r in c['responses'].items():
     self.assertEqual(r['call_id'],cid+'__'+co+'__'+mode)
     for panel in ['reference','reproduction']:
      self.assertIn('status',r[panel]);self.assertIsInstance(r[panel]['answer'],str);answers+=1
  self.assertEqual(contexts,531);self.assertEqual(answers,2124)
 def test_study_paths_cannot_be_browser_paths(self):
  for value in ['../config.local.json','%2e%2e','/etc/passwd','NanoNQ:test1009/../../']:
   with self.assertRaises(ValueError):study.load_study(value)
 def test_truncated_and_cross_record_uncertainty_preserved(self):
  d=study.load_study('NanoNQ:test306')
  for co in ['C','PN1','PN2','PE1','PE2']:self.assertEqual(d['conditions'][co]['responses']['filtered']['reproduction']['status'],'truncated')
  d=study.load_study('NanoNQ:test1618')
  c=next(r for r in d['review_records'] if r['record_type']=='secondary_condition' and r['condition']=='PN2')
  self.assertEqual(c['reproduction']['filtered_core_usable'],'no')
  r=next(r for r in d['review_records'] if r['record_type']=='reproduction_response' and any(l['condition']=='PN2' and l['mode']=='filtered' for l in r['logical_links']))
  self.assertEqual(r['judgment']['core_usable'],'uncertain')
 def test_live_plan_all_nine_and_legacy_bounds(self):
  for co in safety.STUDY_CONDITIONS:
   safety.check_selection({'case_id':'safe','mode':'variants','condition':co},{'safe'},set(),set())
   conditions,arms=safety.run_plan('variants',co);self.assertEqual(conditions,[co]);self.assertEqual(arms,['U','N'])
  self.assertEqual(safety.run_plan('original','C,PN1'),(['C','PN1'],['U','N']))
  self.assertEqual(safety.run_plan('mitigation','PN1'),(['PN1'],['U','N','E','CN']))
  for co in ['ALL','PN3','PE0','C,PN2','../x','neutral_append']:
   with self.assertRaises(ValueError):safety.check_selection({'case_id':'safe','mode':'variants','condition':co},{'safe'},set(),set())
  with self.assertRaises(ValueError):safety.check_selection({'case_id':'safe','mode':'mitigation','condition':'PN2'},{'safe'},set(),{'safe'})
 def test_new_configuration_is_external_and_never_overwrites(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);cfg={k:str(root/k) for k in ['python','package','encoder','ollama_binary','ollama_models']}
   for k in cfg:Path(cfg[k]).touch()
   cfg.update(runs=str(root/'old_runs'),compute_profile='cpu');src=root/'old.json';src.write_text(json.dumps(cfg));before=src.read_bytes()
   new=root/'new';dest=configure.configure(src,new)
   self.assertEqual(src.read_bytes(),before);self.assertEqual(safety.load(dest)['runs'],str(new/'runs'))
   self.assertEqual((new/'runs').stat().st_mode&0o077,0)
   with self.assertRaises(ValueError):configure.configure(src,new)
   with self.assertRaises(ValueError):configure.configure(src,study.ROOT/'newwork')
 def test_real_http_serves_all_cases_without_starting_worker(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);cfg={k:str(root/k) for k in ['python','package','encoder','ollama_binary','ollama_models']};cfg.update(runs=str(root/'runs'),compute_profile='cpu');src=root/'cfg.json';src.write_text(json.dumps(cfg));src.chmod(0o600)
   s=server.Server(src,0);thread=threading.Thread(target=s.serve_forever,daemon=True);thread.start()
   try:
    with patch.object(server.subprocess,'Popen',side_effect=AssertionError('No process allowed in saved inspection')):
     for cid in s.manager.cases:
      conn=http.client.HTTPConnection('127.0.0.1',s.server_port,timeout=4);conn.request('GET','/api/study/'+cid);resp=conn.getresponse();d=json.loads(resp.read());conn.close();self.assertEqual(resp.status,200);self.assertEqual(d['case']['case_id'],cid);self.assertEqual(len(d['conditions']),9)
     self.assertIsNone(s.manager.active);self.assertEqual([p for p in (root/'runs').iterdir() if p.name!='.server.lock'],[])
   finally:s.shutdown();s.server_close();thread.join()
 def test_all_nine_real_manager_worker_arguments(self):
  # Actual process admission/serialization; the child is synthetic and cannot load a model.
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);worker=root/'backend.py';worker.write_text("import json,pathlib,sys; a=sys.argv; out=pathlib.Path(a[a.index('--out')+1]); (out/'synthetic_args.json').write_text(json.dumps(a))")
   cfg={k:str(root/k) for k in ['package','encoder','ollama_binary','ollama_models']};cfg.update(python=sys.executable,runs=str(root/'runs'),compute_profile='cpu');src=root/'cfg.json';src.write_text(json.dumps(cfg));src.chmod(0o600);m=server.Manager(src)
   with patch.object(server,'ROOT',root):
    for co in safety.STUDY_CONDITIONS:
     key=m.start({'case_id':'NanoNQ:test1009','mode':'variants','condition':co});deadline=time.monotonic()+5
     while m.active and time.monotonic()<deadline:time.sleep(.02)
     if m.active:m.cancel(key);self.fail('Synthetic worker did not finish')
     self.assertEqual(m.snapshot(key)['effective_status'],'completed')
     args=json.loads((m.runs/key/'synthetic_args.json').read_text());self.assertEqual(args[args.index('--condition')+1],co);self.assertEqual(args[args.index('--mode')+1],'variants')
if __name__=='__main__':unittest.main()
