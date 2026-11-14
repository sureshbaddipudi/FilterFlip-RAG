#!/usr/bin/env python3
"""Read-only integrity and fresh offline recomputation of the Task 8 packet."""
from pathlib import Path
import hashlib,json,re,sys,tempfile
from analyse import analyse,verify_sources
P=Path(__file__).resolve().parent.parent

def validate():
 checks=0;errors=[]
 def check(ok,label):
  nonlocal checks
  checks+=1
  if not ok:errors.append(label)
 load=lambda f:json.loads((P/f).read_text())
 check(verify_sources(P)==174,'all 174 unchanged input snapshots/archive bindings')
 with tempfile.TemporaryDirectory(prefix='filterflip_task08_') as d:
  out=Path(d)/'analysis';result=analyse(P,out)
  check({f.name for f in out.iterdir()}=={f.name for f in (P/'expected').iterdir()},'exact derived result file inventory')
  for f in out.iterdir():check(f.read_bytes()==(P/'expected'/f.name).read_bytes(),'fresh byte-identical offline result '+f.name)
 check(result['reproduction_requests']==579 and result['copy_case_panel_pairs']==944 and result['trust_contexts']==36,'three analysis workstream sizes')
 pairs=load('expected/COPY_PAIR_SUMMARIES.json')
 for r in pairs:
  for field,s in r['fields'].items():
   check(sum(s['states'].values())==r['planned_case_pairs'],'full denominator '+r['left']+'/'+r['right']+'/'+r['panel']+'/'+r['stratum']+'/'+field)
   check(sum(s['complete_value_transitions'].values())==s['states'].get('complete_pair',0),'paired transition partition '+r['left']+'/'+r['right']+'/'+r['panel']+'/'+r['stratum']+'/'+field)
 status=load('TASK08_STATUS.json');check(status['task_complete'] is True and status['new_model_calls']==0 and status['new_human_reviews_created']==0,'completed offline analysis only')
 check(status['accepted_primary']=='8/51/0 unchanged' and status['R110']=='uncertain unchanged','historical scientific findings retained')
 check(status['cross_record_field_discrepancies_preserved']==1 and status['identical_text_minor_label_notes_preserved']==2,'quality differences not silently repaired')
 check(status['task09_started'] is False,'Task 9 separate')
 tests=load('validation/TEST_RESULTS.json');check(tests['distinct_tests']==7 and tests['normal']['status']=='PASS' and tests['optimized']['status']=='PASS','normal and optimized tests recorded')
 for f in P.glob('*.md'):
  for dest in re.findall(r'\]\(([^)]+)\)',f.read_text()):
   if not dest.startswith(('https:','http:','#')):check((f.parent/dest).exists(),'document link '+f.name+' -> '+dest)
 for name in ['copy_exposure_endpoints','trustrag_support_core']:
  png=P/'figures'/str(name+'.png');svg=P/'figures'/str(name+'.svg');check(png.read_bytes().startswith(b'\x89PNG\r\n\x1a\n') and '<svg' in svg.read_text(),'standalone scientific figures '+name)
 if not (P/'SHA256_MANIFEST.json').exists():errors.append('Final packet manifest missing')
 else:
  manifest=load('SHA256_MANIFEST.json');actual={f.relative_to(P).as_posix() for f in P.rglob('*') if f.is_file() and f!=P/'SHA256_MANIFEST.json'};check(set(manifest)==actual,'exact packet manifest inventory')
  for f,h in manifest.items():check(hashlib.sha256((P/f).read_bytes()).hexdigest()==h,'packet SHA256 '+f)
 return {'status':'PASS' if not errors else 'FAIL','checks':checks,'errors':errors,'fresh_offline_results':'byte-identical to expected','original_source_records':174,'scope':'Integrity and deterministic computational analysis, not a new scientific adjudication or human sign-off.'}
if __name__=='__main__':
 try:r=validate()
 except Exception as e:r={'status':'FAIL','errors':[type(e).__name__+': '+str(e)]}
 print(json.dumps(r,indent=2));sys.exit(0 if r['status']=='PASS' else 1)
