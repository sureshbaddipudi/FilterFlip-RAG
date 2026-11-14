#!/usr/bin/env python3
"""Standard-library offline integrity and saved-record checks; no model/NumPy imports."""
from pathlib import Path
import ast,difflib,hashlib,json,math,re,sys
from urllib.parse import unquote,urlparse
P=Path(__file__).resolve().parent.parent
CHECKS=[]
def check(ok,name):
 if not ok:raise ValueError(name)
 CHECKS.append(name)
def reject_constant(value):raise ValueError('Non-finite JSON constant: '+value)
def load(rel):return json.loads((P/rel).read_text(),parse_constant=reject_constant)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def local(rel):
 f=(P/rel).resolve();check(f.is_relative_to(P) and f.is_file(),'packet file: '+rel);return f
def valid_number(value):return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>=0

def main():
 sources=load('SOURCE_MANIFEST.json');check(len(sources)==32,'32 preserved source records')
 old_manifest=load('inputs/original_release/SHA256_MANIFEST.json');pres=load('validation/SOURCE_PRESERVATION.json')
 check(len(old_manifest)==pres['original_packet_entries_checked']==415,'original sealed coverage 415')
 check(pres['all_original_packet_entries_unchanged'] and pres['all_copied_inputs_and_original_sources_match'],'construction source preservation')
 old_manifest_hash=sha(P/'inputs/original_release/SHA256_MANIFEST.json')
 check(old_manifest_hash==pres['original_task09_manifest_before_sha256']==pres['original_task09_manifest_after_sha256'],'original manifest unchanged')
 for rel,row in sources.items():
  check(sha(local(rel))==row['sha256'],'unchanged copy: '+rel)
  old_rel=str(Path(row['source']).relative_to(pres['original_task09_path']))
  expected=old_manifest_hash if old_rel=='SHA256_MANIFEST.json' else old_manifest[old_rel]
  check(row['sha256']==expected,'source binding to original sealed release: '+rel)
 original=(P/'inputs/original_code/compare_research.py').read_text();corrected=(P/'code/compare_research.py').read_text()
 patch=''.join(difflib.unified_diff(original.splitlines(True),corrected.splitlines(True),fromfile='Task09_original/code/compare_research.py',tofile='Task09_correction_v2/code/compare_research.py'))
 check(patch==(P/'COMPARATOR_V2.patch').read_text(),'exact original-to-v2 patch')
 for path in (P/'code').glob('*.py'):ast.parse(path.read_text());check(True,'Python parses: '+path.name)
 plan=load('VERIFICATION_PLAN.json');caseids=[r['case_id'] for r in plan['case_selection']]
 expected={(cid,co) for cid in caseids for co in plan['conditions']};expected.update((plan['challenge_case'],co) for co in plan['challenge_conditions'])
 check(len(caseids)==8 and len(expected)==75,'eight planned cases /75 contexts')
 selected=[load('inputs/selected_cases/'+cid.replace(':','_')+'.json') for cid in caseids]
 probes=list(dict.fromkeys([r['case']['question'] for r in selected]+[p['text'] for r in selected for c in r['conditions'].values() for p in c['passages']]))
 cached={(r['case']['dataset'],p['chunk_id']) for r in selected for c in r['conditions'].values() for p in c['passages'] if p['copied_from'] is None}
 check(len(probes)==75 and len(cached)==40,'independent expected probe inventories')
 for label in ['baseline','candidate']:
  root='inputs/saved_profiles/'+label+'/'
  contexts=load(root+'CONTEXTS.json');keys=[(r['case_id'],r['condition']) for r in contexts]
  check(len(keys)==len(set(keys))==75 and set(keys)==expected,'actual planned keys: '+label)
  cache=load(root+'FROZEN_INDEX_PROBE_COMPARISON.json');ck=[(r['dataset'],r['chunk_id']) for r in cache]
  check(len(ck)==len(set(ck))==40 and set(ck)==cached,'actual cached probe inventory: '+label)
  tol=plan['embedding_tolerance']
  check(all(valid_number(r['max_absolute']) and valid_number(r['mean_absolute']) and r['mean_absolute']<=r['max_absolute']<=tol['maximum_absolute'] and r['mean_absolute']<=tol['mean_absolute'] for r in cache),'actual finite cached tolerance values: '+label)
  complete=load(root+'COMPLETE.json');count=complete['counts']['encode_calls']
  check(complete['status']=='COMPLETE' and complete['contexts']==75 and complete['generation_attempts']==0 and complete['model_constructions']==1,'actual completion: '+label)
  check(type(count) is int and 0<=count<=plan['maximum_encoder_encode_calls_per_profile'],'actual encode bound: '+label)
  check(valid_number(complete['active_seconds']) and complete['active_seconds']<=plan['maximum_wall_seconds_per_profile'],'actual time bound: '+label)
  probe=load(root+'PROBES.json');check(probe['texts']==probes and probe['embedding_shape']==[75,384] and len(probe['token_ids'])==75,'actual probe records: '+label)
 normal=load('results/normal/SUMMARY.json');optimized=load('results/optimized/SUMMARY.json');historical=load('inputs/original_result/SUMMARY.json')
 check(normal==optimized,'mode summaries identical')
 check(normal['status']=='PASS_BOUNDED_COMPATIBILITY' and normal['comparator_version']==2 and not normal['errors'] and normal['discrepancies']==0,'corrected saved-profile pass')
 check(len(normal['checks'])==35 and all(x['passed'] for x in normal['checks']),'all35 required gates pass')
 required=[]
 for label in ['baseline','candidate']:
  required.extend(label+x for x in [' exact planned case/context keys',' exact planned probe text inventory',' complete valid probe token records',' planned probe dimensions/window',' actual probe array has planned dimensions',' exact planned cached-index probe inventory',' valid cached-index deviations within frozen tolerances',' recorded execution within frozen bounds'])
 check(set(required).issubset({x['check'] for x in normal['checks']}),'missing-gate regressions represented in actual comparison')
 execution=load('validation/OFFLINE_EXECUTION.json')
 for mode in ['normal','optimized']:
  for n in ['CONTEXT_COMPARISONS.json','DISCREPANCIES.json']:
   check(sha(P/'results'/mode/n)==sha(P/'inputs/original_result'/n),'byte-identical original output: '+mode+'/'+n)
  e=next(e for e in execution['executions'] if e['mode']==mode)
  check(e['exit_code']==0 and e['comparator_sha256']==sha(P/'code/compare_research.py') and e['summary_sha256']==sha(P/'results'/mode/'SUMMARY.json'),'recorded comparison execution binding: '+mode)
 for field in execution['unchanged_scientific_summary_fields']:check(normal[field]==historical[field],'unchanged scientific summary: '+field)
 for label in ['baseline','candidate']:
  for field,v in historical['frozen_index_probe_comparison'][label].items():check(normal['frozen_index_probe_comparison'][label][field]==v,'unchanged cached result: '+label+'/'+field)
 check(execution['normal_and_optimized_outputs_byte_equal'] and execution['model_loads']==execution['encoder_calls']==execution['answer_generation_attempts']==0,'offline-only execution record')
 for name,optimization in [('TEST_NORMAL.json',0),('TEST_OPTIMIZED.json',1)]:
  tests=load('validation/'+name)
  check(tests['status']=='PASS' and tests['tests_run']==31 and not tests['failures'] and not tests['errors'] and tests['python_optimization']==optimization,'31 tests passed: '+name)
  check(tests['temporary_copy_scenarios']==len(tests['scenarios'])==40,'40 copied-record scenarios: '+name)
  for s in tests['scenarios']:
   check(s['actual_status']==s['expected_status'],'regression status: '+name+'/'+s['name'])
   if s['expected_status']=='FAIL_COMPATIBILITY':check(bool(s['failed_gates']),'negative scenario gates: '+name+'/'+s['name'])
  index={s['name']:s for s in tests['scenarios']}
  for n in ['unplanned_case_both','cache_maximum_and_mean_exceeded','runtime_limit_candidate','encode_limit_candidate']:
   s=index[n];check(s['historical_status']=='PASS_BOUNDED_COMPATIBILITY' and s['actual_status']=='FAIL_COMPATIBILITY' and s['CLI_exit_checked'],'reproduced old false pass and corrected CLI failure: '+name+'/'+n)
 st=load('CORRECTION_STATUS.json')
 check(st['correction_complete'] and st['version']==2 and st['required_comparator_gates']==35,'correction completion')
 for k in ['new_encoder_loads','new_encoder_calls','new_answer_generation_attempts','services_started','dependency_installations','application_changes','Desktop_writes','frozen_release_edits','scientific_review_record_changes']:check(st[k]==0,'scope action count: '+k)
 check(st['accepted_primary']=='8/51/0 unchanged' and st['R110']=='uncertain unchanged' and st['existing_scientific_review_attribution']=='unchanged','scientific results and attribution retained')
 check(st['next_task']==11 and st['next_task_state']=='not started','Task11 not started')
 for path in P.glob('*.md'):
  for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',path.read_text()):
   target=unquote(target.strip('<>').split('#',1)[0])
   if target and not urlparse(target).scheme:local(target)
 manifest=load('SHA256_MANIFEST.json');actual={str(f.relative_to(P)):sha(f) for f in P.rglob('*') if f.is_file() and f!=P/'SHA256_MANIFEST.json'}
 check(actual==manifest,'all packet files match manifest, including nested original manifest')
 return {'status':'PASS','checks_passed':len(CHECKS),'bound_source_records':32,'original_task09_manifest_entries':415,'saved_contexts_per_profile':75,'cached_index_probes_per_profile':40,'regression_tests_per_mode':31,'temporary_copy_scenarios_per_mode':40,'comparator_gates':35,'scope':'Standard-library integrity/record checks, including independent saved F1 gates; no NumPy replay, model loading, new experiments or scientific adjudication.'}
if __name__=='__main__':
 try:print(json.dumps(main(),indent=2))
 except Exception as e:print(json.dumps({'status':'FAIL','error':str(e),'checks_passed':len(CHECKS)},indent=2));sys.exit(1)
