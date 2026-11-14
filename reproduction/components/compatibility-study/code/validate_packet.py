#!/usr/bin/env python3
"""Offline standard-library verification of recorded Task 9 evidence. No models/network/imported app."""
from pathlib import Path
import hashlib,json,re,sys
P=Path(__file__).resolve().parent.parent

def digest(file):
 h=hashlib.sha256()
 with file.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def validate():
 checks=0;errors=[]
 def check(ok,label):
  nonlocal checks
  checks+=1
  if not ok:errors.append(label)
 load=lambda f:json.loads((P/f).read_text());canon=lambda d:json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
 sources=load('SOURCE_MANIFEST.json');check(len(sources)==332,'332 exact source snapshots')
 for f,m in sources.items():check(digest(P/f)==m['sha256'],'unchanged source '+f)
 manifest=load('candidate_app/RELEASE_MANIFEST.json');check(len(manifest)==157,'separate candidate release inventory')
 for f,h in manifest.items():check(digest(P/'candidate_app'/f)==h,'candidate app manifest '+f)
 for m in load('CANDIDATE_BUILD_DIFF.json')['changes']:check(digest(P/'candidate_app'/m['file'])==m['candidate_sha256'],'tested candidate build hash '+m['file'])
 for name,h in load('validation/EXECUTION_BEGIN.json')['code_hashes'].items():check(digest(P/'code'/name)==h,'runtime code unchanged since begin '+name)
 check(digest(P/'VERIFICATION_PLAN.json')==load('validation/EXECUTION_BEGIN.json')['verification_plan_sha256'],'plan frozen before runtime execution')
 execution=load('validation/EXECUTION_COMPLETE.json');check(execution['status']=='COMPLETE' and len(execution['stages'])==10,'all ten primary execution stages completed')
 for r in execution['stages']:check(r['exit_code']==0 and r['timed_out'] is False,'successful execution '+r['label'])
 for mode in ['normal','optimized']:
  r=load('results/SECURITY_CHECKS_'+mode+'.json');check(r['status']=='PASS' and r['count']==len(r['checks'])==17 and all(c['passed'] for c in r['checks']),'all targeted security checks '+mode)
  check(r['scientific_model_weights_loaded']==0 and r['custom_code_files_executed']==0,'benign rejection scope '+mode)
 for label in ['baseline','candidate']:
  for mode in ['normal','optimized']:
   text=(P/'validation'/str('app_'+label+'_'+mode+'.log')).read_text();check(bool(re.search(r'Ran 42 tests in .*\n\nOK',text)),'42 app tests '+label+' '+mode)
   r=load('results/transport/'+label+'_'+mode+'.json');check(r['status']=='PASS' and len(r['checks'])==7 and all(c['passed'] for c in r['checks']) and r['research_generation_attempts']==0 and r['Ollama_processes_started']==0,'seven synthetic transport checks '+label+' '+mode)
  snap=P/'validation'/str(label+'_environment_snapshot.json');pres=load('validation/PRESERVATION_'+label+'.json');check(pres['status']=='PASS' and not pres['changed'] and pres['complete_file_and_symlink_map_identical'] and digest(snap)==pres['before_snapshot_sha256']==pres['after_snapshot_sha256'],'full environment preservation '+label)
  snapshot=load('validation/'+label+'_environment_snapshot.json');check(len(snapshot['files'])==pres['entries'],'preserved entry count '+label)
  runtime=load('results/profiles/'+label+'/COMPLETE.json');check(runtime['status']=='COMPLETE' and runtime['contexts']==75 and runtime['generation_attempts']==0 and runtime['model_constructions']==1 and runtime['counts']['encode_calls']<=1000 and runtime['active_seconds']<=1800,'bounded completed research profile '+label)
  identity=load('results/profiles/'+label+'/IDENTITY.json');profile=load('profiles/'+label+'.json');check(identity['versions']==profile['versions'] and identity['model_files']==profile['model_files'] and identity['cpu_threads']==4 and identity['encoder_window']==256 and identity['embedding_dimension']==384,'recorded runtime settings '+label)
  check('No broken requirements found.' in (P/'validation'/str('pip_check_'+label+'.log')).read_text(),'pip check '+label)
 helper='lib/python3.11/site-packages/sentence_transformers/util/misc.py';local=load('profiles/candidate.json')['candidate_identity'];check(load('validation/candidate_environment_snapshot.json')['files'][helper]['sha256']==local['local_guard_sha256']==load('inputs/task05/candidate/LOCAL_GUARD.json')['after_sha256'],'observed candidate local helper binding')
 check(bool(re.search(r'Ran 5 tests in .*\n\nOK',(P/'validation/comparison_tests_v2.log').read_text())),'five comparator controls pass after recorded setup correction')
 left=load('results/profiles/baseline/CONTEXTS.json');right=load('results/profiles/candidate/CONTEXTS.json');check(len(left)==len(right)==75,'75 paired contexts')
 check(digest(P/'results/profiles/baseline/PROBE_EMBEDDINGS.npy')==digest(P/'results/profiles/candidate/PROBE_EMBEDDINGS.npy'),'saved probe arrays bit-identical')
 check(load('results/profiles/baseline/PROBES.json')==load('results/profiles/candidate/PROBES.json'),'probe text/token/dimension identity')
 unique=set();positions=0
 for l,r in zip(left,right):
  key=l['case_id']+'/'+l['condition'];check(l['case_id']==r['case_id'] and l['condition']==r['condition'],'paired identity '+key)
  check([(x.get('chunk_id',x['record_id']),x['text']) for x in l['retrieved']]==[(x.get('chunk_id',x['record_id']),x['text']) for x in r['retrieved']],'exact ordered retrieved identity '+key)
  check(l['copy_chunks']==r['copy_chunks'] and l['token_ids']==r['token_ids'],'copy/chunk/token identity '+key)
  check(l['policies']==r['policies'],'exact four-policy decisions '+key);check(l['requests']==r['requests'],'exact request/token IDs '+key)
  for arm,a in l['requests'].items():
   positions+=1;unique.add(a['request_sha256']);check(hashlib.sha256(canon(a['request'])).hexdigest()==a['request_sha256'],'canonical request '+key+'/'+arm)
  for field in ['query_vector','copy_vectors','scores','matrix']:check(l[field]==r[field],'recorded numeric equality '+key+'/'+field)
 check(positions==300 and len(unique)==146,'300 logical /146 unique request identities; zero generated answers')
 comparison=load('results/research_comparison/SUMMARY.json');check(comparison['status']=='PASS_BOUNDED_COMPATIBILITY' and not comparison['errors'] and comparison['discrepancies']==0,'saved numeric comparison passes')
 differences=load('results/ARCHIVAL_ID_DIFFERENCES.json');check(len(differences)==5 and all(r['same_ordered_text'] and r['native_kept_match'] and r['U_request_match'] and r['N_request_match'] for r in differences),'historical identity differences preserved without changed text/requests')
 check(load('validation/SOURCE_ASSET_PRESERVATION.json')['status']=='PASS','named source/asset preservation recorded')
 status=load('TASK09_STATUS.json');check(status['task_complete'] is True and status['generation_attempts']==0 and status['candidate_adoption']=='not performed' and status['human_risk_acceptance']=='not recorded','task completion distinct from adoption/acceptance')
 check(status['accepted_primary']=='8/51/0 unchanged' and status['R110']=='uncertain unchanged' and status['task10_started'] is False,'historical science and next-task boundary preserved')
 for f in P.glob('*.md'):
  for dest in re.findall(r'\]\(([^)]+)\)',f.read_text()):
   if not dest.startswith(('http:','https:','#')):check((f.parent/dest).exists(),'report local link '+f.name+' -> '+dest)
 if not (P/'SHA256_MANIFEST.json').exists():errors.append('Final manifest missing')
 else:
  sealed=load('SHA256_MANIFEST.json');actual={f.relative_to(P).as_posix() for f in P.rglob('*') if f.is_file() and f!=P/'SHA256_MANIFEST.json'};check(set(sealed)==actual,'exact bundle inventory')
  for f,h in sealed.items():check(digest(P/f)==h,'sealed file '+f)
 return {'status':'PASS' if not errors else 'FAIL','checks':checks,'errors':errors,'scope':'Recorded integrity/security execution/paired compatibility/preservation only. No model run, deployment or new human scientific/risk acceptance.'}
if __name__=='__main__':
 try:r=validate()
 except Exception as e:r={'status':'FAIL','errors':[type(e).__name__+': '+str(e)]}
 print(json.dumps(r,indent=2));raise SystemExit(0 if r['status']=='PASS' else 1)
