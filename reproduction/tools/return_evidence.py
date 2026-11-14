"""F2: evidence contracts for a complete report, separate from verification success."""
import math,re
from pathlib import Path
from packet_common import P,load,sha,local,inventory
HEX=re.compile(r'[0-9a-fA-F]{64}\Z')
def digest(value):return isinstance(value,str)and bool(HEX.fullmatch(value))
def plan():return load(P/'provenance/OFFLINE_PLAN.json')
def specs(features):
 if not isinstance(features,dict)or set(features)!={'node','numpy'}or any(type(v)is not bool for v in features.values()):raise ValueError('Invalid execution feature branches')
 return [r for r in plan()['steps']if 'when_numpy'not in r or r['when_numpy']==features['numpy']]
def expected_names(spec):
 if 'output_set'in spec:
  s=plan()['output_sets'][spec['output_set']];return {s['output_root']+'/'+n for n in s['files']}
 return set(spec.get('output_files',[]))
def existing_outputs(root,spec):
 if 'output_set'in spec:
  s=plan()['output_sets'][spec['output_set']];folder=Path(root)/s['output_root']
  return {s['output_root']+'/'+n:h for n,h in inventory(folder).items()}if folder.exists()else{}
 return {n:sha(local(root,n))for n in spec.get('output_files',[])if(Path(root)/n).is_file()}
def integrity_report(report,expected_manifest,stage=None):
 if not isinstance(report,dict)or report.get('packet_manifest_sha256')!=expected_manifest:raise ValueError('Integrity report lacks expected packet binding')
 if stage is not None and report.get('verification_stage')!=stage:raise ValueError('Integrity evidence has missing/wrong before/after stage')
 status=report.get('integrity')
 if status=='PASS':
  if report.get('files')!=len(load(P/'SHA256_MANIFEST.json'))or report.get('sealed_components')!=15 or report.get('review_records')!=20:raise ValueError('Integrity PASS report has wrong inventory')
 elif status=='FAIL':
  if not isinstance(report.get('error'),str)or not report['error'].strip():raise ValueError('Integrity failure needs its error')
 else:raise ValueError('Invalid integrity evidence status')
 return status

def checked_log(root,row):
 name=row.get('log');h=row.get('log_sha256')
 if not name or not digest(h):raise ValueError('Executed check needs log and SHA-256: '+row['name'])
 f=local(root,name)
 if f.stat().st_size==0 or sha(f)!=h:raise ValueError('Missing/empty/changed execution log: '+row['name'])

def check_step(root,row,spec,lookup,expected_manifest):
 status=row.get('status');name=spec['name'];kind=spec['kind']
 if status not in ('PASS','FAIL','NOT_RUN'):raise ValueError('Invalid execution status: '+name)
 if status=='NOT_RUN':
  if not isinstance(row.get('reason'),str)or not row['reason'].strip():raise ValueError('Explain NOT_RUN: '+name)
  if row.get('exit_code')is not None or row.get('outputs'):raise ValueError('NOT_RUN cannot claim executed outputs: '+name)
  if row.get('log'):checked_log(root,row)
 else:
  if kind=='not_run':raise ValueError('Unavailable-tool branch cannot claim execution')
  checked_log(root,row)
  if kind=='command':
   rc=row.get('exit_code')
   if type(rc)is not int or (status=='PASS')!=(rc==0):raise ValueError('Command status/exit mismatch: '+name)
  outputs=row.get('outputs')
  if not isinstance(outputs,dict):raise ValueError('Missing output bindings: '+name)
  actual=existing_outputs(root,spec)
  if outputs!=actual:raise ValueError('Missing/changed/unbound outputs: '+name)
  for n,h in outputs.items():
   if not digest(h)or sha(local(root,n))!=h:raise ValueError('Output hash mismatch: '+name)
  if status=='PASS'and set(outputs)!=expected_names(spec):raise ValueError('Required output inventory absent: '+name)
  if kind=='comparison'and status=='PASS':
   s=plan()['output_sets'][spec['output_set']]
   for n,h in s['files'].items():
    if sha(local(P,s['expected_packet_root']+'/'+n))!=h or outputs[s['output_root']+'/'+n]!=h:raise ValueError('PASS comparison differs from frozen expected output: '+name)
  if kind=='integrity':
   report=load(local(root,'pristine_after.json'))
   if integrity_report(report,expected_manifest,'after')!=status:raise ValueError('Pristine-after status contradiction')
  if status=='PASS'and name.startswith('comparator31_'):
   d=load(local(root,spec['output_files'][0]))
   if d.get('status')!='PASS'or d.get('tests_run')!=31 or d.get('temporary_copy_scenarios')!=40:raise ValueError('Comparator regression result incomplete')
  if status=='PASS'and name=='saved_rehearsal507':
   d=load(local(root,'REHEARSAL_AUDIT.json'))
   if d.get('audit')!='PASS'or d.get('checks')!=507 or d.get('jobs')!=5 or d.get('complete_answers')!=20:raise ValueError('Saved-rehearsal audit incomplete')
 if kind=='comparison':
  parent=lookup.get(spec['requires'])
  if parent is None:raise ValueError('Missing upstream execution step')
  if parent['status']!='PASS'and status!='NOT_RUN':raise ValueError('Comparison cannot pass an unexecuted/failed upstream')
  if parent['status']=='PASS'and status=='NOT_RUN':raise ValueError('Successful upstream needs a comparison result')

def validate_execution(root,execution,expected_manifest):
 root=Path(root);p=plan()
 if not isinstance(execution,dict)or execution.get('schema_version')!=2:raise ValueError('Execution ledger schema version 2 required')
 if execution.get('packet_manifest_sha256')!=expected_manifest:raise ValueError('Execution ledger packet mismatch')
 if execution.get('plan_sha256')!=sha(P/'provenance/OFFLINE_PLAN.json')or execution.get('driver_sha256')!=sha(P/'tools/reproduce_offline.py'):raise ValueError('Execution plan/driver binding mismatch')
 for field in p['action_fields']:
  if type(execution.get(field))is not int or execution[field]!=0:raise ValueError('Unexpected action count: '+field)
 rows=execution.get('steps')
 if not isinstance(rows,list):raise ValueError('Execution steps must be a list')
 expected=specs(execution.get('features'));names=[r.get('name')for r in rows];wanted=[r['name']for r in expected]
 if any(not isinstance(n,str)for n in names)or len(names)!=len(set(names))or not set(names).issubset(wanted):raise ValueError('Duplicate/unknown execution steps')
 partial=execution.get('overall')=='IN_PROGRESS'
 if names!=(wanted[:len(names)]if partial else wanted):raise ValueError('Missing or reordered planned execution checks')
 before=execution.get('integrity_before_file');h=execution.get('integrity_before_sha256')
 if not before or not digest(h)or sha(local(root,before))!=h:raise ValueError('Missing/changed before-integrity evidence')
 report=load(local(root,before));integrity_report(report,expected_manifest,'before')
 if execution.get('integrity_before')!=report:raise ValueError('Before-integrity report binding mismatch')
 lookup={r['name']:r for r in rows}
 for row,spec in zip(rows,expected):check_step(root,row,spec,lookup,expected_manifest)
 if not execution['features']['node']:
  for name in ('javascript_syntax','recorded59_dom'):
   if name in lookup and lookup[name]['status']!='NOT_RUN':raise ValueError('Missing Node cannot claim JS execution')
 if not execution['features']['numpy']and 'comparator_numpy_replay'in lookup and lookup['comparator_numpy_replay']['status']!='NOT_RUN':raise ValueError('Missing NumPy branch must be NOT_RUN')
 computed='FAIL'if any(r['status']=='FAIL'for r in rows)else'PASS_WITH_NOT_RUN'if any(r['status']=='NOT_RUN'for r in rows)else'PASS'
 if not partial and execution.get('overall')!=computed:raise ValueError('Execution overall contradicts check results')
 return {'complete_inventory':not partial,'result':'IN_PROGRESS'if partial else computed,'planned_steps':len(wanted),'recorded_steps':len(rows),'missing_steps':wanted[len(rows):]}
