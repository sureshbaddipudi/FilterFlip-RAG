"""Offline technical audit. Does not generate or classify answers."""
import argparse,hashlib,json,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--packet',required=True);p.add_argument('--runs',required=True);p.add_argument('--guard-events',required=True);p.add_argument('--source-app',required=True);p.add_argument('--out',required=True);a=p.parse_args()
P=Path(a.packet);A=P/'app';S=Path(a.source_app);checks=[]
def require(ok,what):
 if not ok:raise ValueError(what)
 checks.append(what)
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sys.path.insert(0,str(A));import backend
plan=read(P/'REHEARSAL_PLAN.json');old=read(P/'inputs/v24_RELEASE_MANIFEST.json');new=read(A/'RELEASE_MANIFEST.json')
require(read(S/'RELEASE_MANIFEST.json')==old,'frozen source manifest unchanged')
for name,h in old.items():require(sha(S/name)==h,'frozen source unchanged: '+name)
require(set(old)==set(new),'same manifested application file set')
for name,h in new.items():require(sha(A/name)==h,'v2.5 manifest: '+name)
require({n for n in old if old[n]!=new[n]}=={'static/index.html','static/app.js','README.md','HANDOVER.md','CHANGELOG.md'},'only five permitted text/document files differ')
for source,record in read(P/'inputs/SOURCE_BINDINGS.json').items():
 require(record['sha256']==sha(P/record['snapshot']),'source binding: '+record['snapshot'])
states=sorted(((f.parent,read(f))for f in Path(a.runs).glob('*/state.json')),key=lambda pair:pair[1]['started_at'])
require(len(states)==5,'exactly five live job directories')
guard=[json.loads(line)for line in Path(a.guard_events).read_text().splitlines()]
admitted=[e for e in guard if e['stage']=='admitted_once'];created=[e for e in guard if e['stage']=='run_created']
require(len(admitted)==len(created)==5,'exactly five guarded admissions and starts')
rows=[];raw_bindings={};expected_versions={'ragdefender':'0.2.0','sentence-transformers':'5.1.0','transformers':'4.51.3','torch':'2.8.0+cpu','numpy':'2.4.6','scikit-learn':'1.9.1'}
for n,((folder,state),(mode,co))in enumerate(zip(states,plan['sequence']),1):
 result=read(folder/'result.json');events=[json.loads(line)for line in (folder/'events.jsonl').read_text().splitlines()];calls=[e for e in events if e['stage']=='Generating fresh answer']
 require(state['case_id']==plan['case_id'] and state['mode']==mode and state['condition']==co,'planned selection '+str(n))
 require(created[n-1]['run_id']==folder.name and admitted[n-1]['number']==n,'guard job binding '+str(n))
 require(state['status']==result['status']=='completed' and state['exit_code']==0,'completed job '+str(n))
 require(state['semantic_review']==result['semantic_review']=='pending','new semantic review pending '+str(n))
 require(result['generation_attempts']==len(calls)==len(list(folder.glob('response_*.bin')))==4,'four actual attempts and captures '+str(n))
 require(result['compute_profile']=='cpu' and result['model']==backend.MODEL and result['model_digest']==backend.DIGEST and result['options']==backend.OPTIONS,'fixed CPU/model/options '+str(n))
 require(result['identity']['backend_sha256']==sha(A/'backend.py') and result['identity']['versions']==expected_versions,'executed backend and pinned versions '+str(n))
 expected={'C':['U','N'],'PN1':['U','N']}if mode=='original'else{co:['U','N','E','CN']}
 require(set(result['conditions'])==set(expected),'planned evidence conditions '+str(n))
 answers=[];j=0
 for condition,arms in expected.items():
  c=result['conditions'][condition];require(set(c['answers'])==set(c['policies'])==set(arms),'complete policy panel '+str(n)+' '+condition)
  require(c['policies']['U']['kept']==list(range(len(c['retrieved']))),'unfiltered evidence preserved '+str(n)+' '+condition)
  if mode=='challenge':require(len(c['retrieved'])==6 and sum(bool(p.get('challenge_added'))for p in c['retrieved'])==1,'one forced sixth passage '+str(n))
  for arm in arms:
   j+=1;v=c['answers'][arm];raw=folder/f'response_{j:02d}.bin';response=read(raw);request=v['request'];h=hashlib.sha256(backend.canonical(request)).hexdigest()
   require(v['status']=='ok' and v['source']=='fresh_generation' and v['semantic_review']=='pending','fresh complete answer '+str(n)+' '+condition+'/'+arm)
   require(response==v['raw_response'] and response['message']['content']==v['text'] and backend.response_status(response)=='ok','raw byte capture matches saved answer '+str(n)+' '+condition+'/'+arm)
   require(v['request_sha256']==calls[j-1]['request_sha256']==h and calls[j-1]['condition']==condition and calls[j-1]['mode']==arm,'durable attempt/request binding '+str(n)+' '+condition+'/'+arm)
   require(request==backend.request(result['question'],[c['retrieved'][i]['text']for i in c['policies'][arm]['kept']]),'request contains exactly selected evidence '+str(n)+' '+condition+'/'+arm)
   require(abs(response['prompt_eval_count']-v['estimated_tokens'])<=16 and v['estimated_tokens']+128+64<=4096,'token/context limits '+str(n)+' '+condition+'/'+arm)
   require(0<=v['seconds']<=590,'response time bound '+str(n)+' '+condition+'/'+arm)
   raw_bindings[folder.name+'/'+raw.name]=sha(raw);answers.append({'condition':condition,'policy':arm,'text':v['text'],'request_sha256':h,'seconds':v['seconds'],'semantic_review':'pending'})
 require(state['finished_at']-state['started_at']<=2400,'job time bound '+str(n))
 rows.append({'number':n,'run_id':folder.name,'mode':mode,'condition':co,'status':'completed','generation_attempts':4,'started_at':state['started_at'],'finished_at':state['finished_at'],'seconds':state['finished_at']-state['started_at'],'answers':answers})
ready=next(e for e in guard if e['stage']=='server_ready');stopped=[e for e in guard if e['stage']=='server_stopped']
require(len(stopped)==1,'owned server stopped exactly once');require(stopped[0]['elapsed_seconds']<=7200,'aggregate two-hour budget')
report={'audit':'PASS','checks':len(checks),'jobs':5,'attempts':20,'complete_answers':20,'automatic_retries':0,'semantic_review':'pending','fresh_human_acceptance':False,'run_rows':rows,'raw_sha256':raw_bindings,'guard_elapsed_seconds':stopped[0]['elapsed_seconds'],'new_scientific_judgments':0,'browser_download_button':'NOT RUN; exports are direct GET snapshots of the same endpoint, labelled separately','checks_passed':checks}
Path(a.out).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k]for k in ('audit','checks','jobs','attempts','complete_answers','semantic_review','guard_elapsed_seconds')}))
