"""TrustRAG scope, data, identity and order regression tests; no model calls."""
import sys,json,tempfile,unittest,http.client,threading
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import safety,trust,backend,server
class TrustTests(unittest.TestCase):
 def test_all_36_choices_and_two_answer_limit(self):
  for cid in trust.catalog():
   for co in trust.CONDITIONS:
    safety.check_selection({'case_id':cid,'mode':'trust','condition':co},{cid:{}},set(),set())
    self.assertEqual(safety.run_plan('trust',co),([co],['U','T']))
 def test_outside_panel_and_conditions_refused(self):
  for cid,co in [('NanoNQ:test306','PN1'),('NanoNQ:test1009','PN2'),('NanoNQ:test1009','../PN1'),('NanoNQ:test1009','neutral_append')]:
   with self.assertRaises(ValueError):safety.check_selection({'case_id':cid,'mode':'trust','condition':co},{cid:{}},set(),set())
 def test_context_has_no_answers_or_judgments_or_kept_mask(self):
  rows=safety.load(trust.ROOT/'data/trust_contexts.json');self.assertEqual(len(rows),36)
  for row in rows:
   self.assertEqual(set(row),{'case_id','condition','question','retrieved','embedding_rows'})
   self.assertEqual(row,trust.context(row['case_id'],row['condition']))
 def test_stemmer_token_and_passage_budgets(self):
  with self.assertRaisesRegex(ValueError,'token budget'):trust.validate_texts([{'text':'y'*257}]*5)
  with self.assertRaisesRegex(ValueError,'size'):trust.validate_texts([{'text':'a '*17000}]*5)
  trust.validate_texts([{'text':'Short fixed evidence.'}]*5)
 def test_tampered_context_refused(self):
  real=safety.read
  def changed(p,*a):
   raw=real(p,*a)
   return raw+b' ' if Path(p).name=='trust_contexts.json' else raw
  with patch.object(trust,'read',side_effect=changed):
   with self.assertRaisesRegex(ValueError,'identity'):trust.context('NanoNQ:test1009','C')
 def test_tampered_native_refused_before_import(self):
  profile=safety.load(trust.ROOT/'trust_profile.json');profile['native_sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'filter identity'):trust.engine(profile)
 def test_output_order_preserved_and_empty_allowed(self):
  import numpy as np
  emb=np.array([[1,2],[3,4],[5,6]])
  self.assertEqual(trust.map_output(emb,['a','b','c'],emb[[2,0]],['c','a']),[2,0])
  self.assertEqual(trust.map_output(emb,['a','b','c'],[],[]),[])
 def test_foreign_or_ambiguous_output_refused(self):
  import numpy as np
  emb=np.array([[1,2],[1,2]])
  for texts,outtext in [(['a','a'],['a']),(['a','b'],['unknown'])]:
   with self.assertRaises(ValueError):trust.map_output(emb,texts,emb[:1],outtext)
 def test_empty_and_reordered_requests_use_actual_context(self):
  c={'retrieved':[{'text':'a'},{'text':'b'},{'text':'c'}],'policies':{'T':{'kept':[2,0]}}}
  self.assertEqual(backend.context_request('q',c,'T'),backend.request('q',['c','a']))
  c['policies']['T']['kept']=[];self.assertEqual(backend.context_request('q',c,'T'),backend.request('q',[]))
  self.assertIn('<document>\n\n</document>',backend.context_request('q',c,'T')['messages'][1]['content'])
 def test_invalid_kept_indices_fail_closed(self):
  for indices in [[0,0],[-1],[True],[2]]:
   with self.assertRaises(ValueError):backend.context_request('q',{'retrieved':[{'text':'a'}],'policies':{'T':{'kept':indices}}},'T')
 def test_original_native_pipeline_scientific_body_preserved(self):
  # Specific request protocol remains unchanged; generation labels never enter it.
  req=backend.request('q',['evidence']);self.assertEqual(req['options'],{'temperature':0,'seed':42,'num_ctx':4096,'num_predict':128});self.assertEqual(req['model'],'qwen2.5:3b')
 def test_project_records_cover_all_tasks_and_draft_report(self):
  d=safety.load(trust.ROOT/'data/project.json');self.assertEqual([x['number'] for x in d['tasks']],[str(i) for i in range(1,14)])
  self.assertIn('pending',d['tasks'][10]['status']);self.assertEqual(len(d['security']),4)
class TrustHTTPTests(unittest.TestCase):
 def test_bootstrap_scope_and_readonly_project_routes(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);cfg={k:str(p/k) for k in ['package','encoder','ollama_binary','ollama_models','runs']};cfg.update(python=sys.executable,compute_profile='cpu');safety.save(p/'cfg.json',cfg)
   s=server.Server(p/'cfg.json',0);thread=threading.Thread(target=s.serve_forever,daemon=True);thread.start()
   try:
    with patch.object(server.subprocess,'Popen',side_effect=AssertionError('No model allowed')):
     def get(path):
      c=http.client.HTTPConnection('127.0.0.1',s.server_port,timeout=8);c.request('GET',path);r=c.getresponse();raw=r.read();status=r.status;c.close();return status,raw
     code,raw=get('/api/bootstrap');d=json.loads(raw);self.assertEqual(sum(bool(c['trust']) for c in d['cases']),12)
     code,raw=get('/api/project');self.assertEqual(code,200);self.assertEqual(len(json.loads(raw)['tasks']),13)
     code,raw=get('/semester-report.pdf');self.assertEqual(code,200);self.assertTrue(raw.startswith(b'%PDF'))
     code,raw=get('/api/project/../../config.local.json');self.assertEqual(code,404)
   finally:s.shutdown();s.server_close();thread.join()
