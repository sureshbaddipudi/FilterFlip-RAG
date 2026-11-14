"""Version 1.1 fixed offline driver with complete evidence inventory; no inference."""
import argparse,json,os,shutil,subprocess,sys,time
from pathlib import Path
from packet_common import P,sha
from verify_handover import verify
from return_evidence import plan,specs,existing_outputs,validate_execution

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--numpy-python');ap.add_argument('--node');a=ap.parse_args();out=a.out.resolve()
 if out.exists()or out.is_relative_to(P)or P.is_relative_to(out):raise ValueError('Choose a new output directory outside the pristine packet')
 integrity=verify();integrity['verification_stage']='before';before=sha(P/'SHA256_MANIFEST.json');out.mkdir(parents=True,mode=0o700)
 for d in ('logs','tmp','cache'):(out/d).mkdir()
 env=dict(os.environ,TMPDIR=str(out/'tmp'),XDG_CACHE_HOME=str(out/'cache'),PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
 for key in ('PYTHONPATH','PYTHONHOME','PYTHONSAFEPATH','NODE_OPTIONS'):env.pop(key,None)
 py=sys.executable;started=time.monotonic();steps=[];node=a.node or shutil.which('node');node=node if node and(Path(node).is_file()or shutil.which(node))else None;npy=a.numpy_python or py
 try:
  probe=subprocess.run([npy,'-I','-B','-c','import numpy;print(numpy.__version__)'],env=env,stdin=subprocess.DEVNULL,capture_output=True,timeout=30);numpy_available=probe.returncode==0;probe_text=probe.stdout+probe.stderr
 except (OSError,subprocess.TimeoutExpired)as e:numpy_available=False;probe_text=str(e).encode()
 (out/'numpy_probe.log').write_bytes(probe_text or b'No probe output\n')
 features={'node':node is not None,'numpy':numpy_available};lookup={s['name']:s for s in specs(features)}
 (out/'pristine_before.json').write_text(json.dumps(integrity,indent=2)+'\n')
 header={'schema_version':2,'packet_manifest_sha256':before,'plan_sha256':sha(P/'provenance/OFFLINE_PLAN.json'),'driver_sha256':sha(Path(__file__)),'features':features,'model_calls':0,'encoder_loads':0,'downloads':0,'installations':0,'human_scientific_judgments':0,'integrity_before':integrity,'integrity_before_file':'pristine_before.json','integrity_before_sha256':sha(out/'pristine_before.json')}
 def record(name,status,**kw):
  steps.append(dict(name=name,status=status,**kw));(out/'EXECUTION.json').write_text(json.dumps(dict(header,overall='IN_PROGRESS',steps=steps),indent=2)+'\n');print(json.dumps({'step':name,'status':status}),flush=True)
 def skip(name,reason):record(name,'NOT_RUN',reason=reason)
 def run(name,args,cwd=P,timeout=240):
  if time.monotonic()-started>1200:skip(name,'Aggregate offline-check deadline reached');return False
  stamp=time.monotonic();log=out/'logs'/f'{len(steps)+1:02d}_{name}.log'
  try:r=subprocess.run(args,cwd=cwd,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout);data=r.stdout;rc=r.returncode
  except subprocess.TimeoutExpired as e:data=(e.stdout or b'')+b'\nOFFLINE CHECK TIMEOUT\n';rc=124
  except OSError as e:data=str(e).encode();rc=127
  log.write_bytes(('COMMAND '+json.dumps(list(map(str,args)))+'\nEXIT '+str(rc)+'\n').encode()+data)
  record(name,'PASS'if rc==0 else'FAIL',exit_code=rc,seconds=time.monotonic()-stamp,command=list(map(str,args)),log=str(log.relative_to(out)),log_sha256=sha(log),outputs=existing_outputs(out,lookup[name]));return rc==0
 def command(name,rel,*extra,opt=False,cwd=P):return run(name,[py,'-B',*(['-O']if opt else[]),str(P/rel),*map(str,extra)],cwd)
 def compare(name,upstream_pass):
  if not upstream_pass:skip(name,'Upstream '+lookup[name]['requires']+' did not pass; comparison not executed');return
  s=plan()['output_sets'][lookup[name]['output_set']];actual=existing_outputs(out,lookup[name]);expected={s['output_root']+'/'+n:h for n,h in s['files'].items()};ok=actual==expected
  log=out/'logs'/f'{len(steps)+1:02d}_{name}.json';log.write_text(json.dumps({'check':name,'status':'PASS'if ok else'FAIL','actual':actual,'expected':expected},indent=2)+'\n')
  record(name,'PASS'if ok else'FAIL',matched_files=len(actual),expected_relative=s['expected_packet_root'],log=str(log.relative_to(out)),log_sha256=sha(log),outputs=actual)
 for key,script in [('task04','validate_mapping.py'),('task05','validate_packet.py'),('task06','validate_packet.py'),('task07','validate_acceptance.py'),('task08','validate_packet.py'),('task09_v2','validate_packet.py'),('report','validate_report.py')]:command(key+'_integrity',f'components/{key}/code/{script}',*(['--check-package']if key=='task04'else[]))
 command('app_manifest','components/task12/app/verify_release.py')
 for optimized in (False,True):
  suffix='optimized'if optimized else'normal'
  run('app42_'+suffix,[py,'-I','-B',*(['-O']if optimized else[]),'-m','unittest','discover','-s',str(P/'components/task12/app/tests'),'-v'],P/'components/task12/app')
  command('handover_controls_'+suffix,'tools/test_handover_tools.py',opt=optimized);command('readonly5_'+suffix,'tools/test_readonly_gui.py',opt=optimized);command('task02_tests_'+suffix,'components/task02/code/test_analysis.py',opt=optimized);command('task08_tests_'+suffix,'components/task08/code/test_analysis.py',opt=optimized)
 if node:
  run('javascript_syntax',[node,'--check',str(P/'components/task12/app/static/app.js')]);run('recorded59_dom',[node,str(P/'components/task12/code/check_recorded_view.cjs'),str(P/'components/task12/app')])
 else:
  for n in ('javascript_syntax','recorded59_dom'):skip(n,'No existing Node executable supplied/found; no installation attempted')
 compare('week06_expected',command('week06_analysis','components/week06_analysis/analyze.py','--check','--out',out/'week06'))
 compare('task02_expected',command('task02_analysis','components/task02/code/analyse_task02_variants.py','--inputs',P/'components/task02/inputs','--out',out/'task02'))
 compare('task08_expected',command('task08_analysis','components/task08/code/analyse.py','--out',out/'task08'))
 if numpy_available:
  for optimized in (False,True):
   suffix='optimized'if optimized else'normal';flags=[npy,'-I','-B',*(['-O']if optimized else[])]
   compare('comparator_expected_'+suffix,run('comparator35_'+suffix,flags+[str(P/'components/task09_v2/code/compare_research.py'),'--runs',str(P/'components/task09_v2/inputs/saved_profiles'),'--out',str(out/('comparison_'+suffix))]))
   run('comparator31_'+suffix,flags+[str(P/'components/task09_v2/code/test_comparison.py'),'--work-root',str(out/('comparison_controls_'+suffix)),'--result',str(out/('COMPARATOR_TEST_'+suffix+'.json'))])
 else:skip('comparator_numpy_replay','Existing Python with NumPy unavailable; no installation attempted; saved-record integrity still checked')
 compare('report_data_expected',command('report_data','components/report/code/generate_report_data.py','--output-root',out/'report_data'))
 command('saved_rehearsal507','tools/audit_saved_rehearsal.py','--packet',P/'components/task12','--runs',P/'components/task12/runs','--guard-events',P/'components/task12/runtime/guard_events.jsonl','--source-app',P/'baseline/v24','--out',out/'REHEARSAL_AUDIT.json')
 try:after=verify();after['verification_stage']='after';ok=sha(P/'SHA256_MANIFEST.json')==before
 except Exception as e:after={'integrity':'FAIL','packet_manifest_sha256':before,'verification_stage':'after','error':str(e)};ok=False
 (out/'pristine_after.json').write_text(json.dumps(after,indent=2)+'\n');log=out/'logs/pristine_after.json';log.write_text(json.dumps(after,indent=2)+'\n');record('pristine_after','PASS'if ok else'FAIL',log=str(log.relative_to(out)),log_sha256=sha(log),outputs=existing_outputs(out,lookup['pristine_after']))
 statuses=[s['status']for s in steps];overall='FAIL'if'FAIL'in statuses else'PASS_WITH_NOT_RUN'if'NOT_RUN'in statuses else'PASS'
 result=dict(header,overall=overall,elapsed_seconds=time.monotonic()-started,steps=steps,scope='Saved-data verification and synthetic controls; no scientific inference or human acceptance')
 (out/'EXECUTION.json').write_text(json.dumps(result,indent=2)+'\n');validate_execution(out,result,before);print(json.dumps({'overall':overall,'steps':len(steps),'out':str(out)},indent=2));return 1 if overall=='FAIL'else 2 if overall=='PASS_WITH_NOT_RUN'else 0
if __name__=='__main__':sys.exit(main())
