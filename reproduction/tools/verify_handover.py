"""Read-only portable packet verification. No historical commands are executed."""
import argparse,json,sys
from pathlib import Path
from packet_common import P,load,sha,local,verify_tree

def verify(root=P):
 root=Path(root);count=verify_tree(root);components=load(root/'provenance/COMPONENTS.json');n=0
 for c in components:
  folder=root/c['destination'];manifest=local(folder,c['manifest'])
  if sha(manifest)!=c['manifest_sha256']:raise ValueError('Component manifest binding: '+c['id'])
  if verify_tree(folder,c['manifest'])!=c['manifest_entries']:raise ValueError('Component count: '+c['id'])
  n+=1
 for s in load(root/'provenance/SOURCE_SNAPSHOTS.json'):
  if sha(local(root,s['snapshot']))!=s['sha256']:raise ValueError('Metadata snapshot: '+s['snapshot'])
 form=load(root/'review/TASK12_ANSWER_REVIEW_TEMPLATE.json');catalog=load(root/'review/REVIEW_RECORDS.json')
 if len(catalog)!=20 or len({r['record_id']for r in catalog})!=20:raise ValueError('Review coverage')
 if [r['record_id']for r in form['records']]!=[r['record_id']for r in catalog]:raise ValueError('Template record identities')
 if form['reviewer']is not None or form['assistance_disclosure']is not None or any(r['review_state']!='pending'for r in form['records']):raise ValueError('Template falsely pre-reviewed')
 status=load(root/'TASK13_STATUS.json')
 if status['task_complete']is not False or status['teammate_verification']!='pending external return':raise ValueError('Unrecorded teammate completion claimed')
 return {'integrity':'PASS','packet_manifest_sha256':sha(root/'SHA256_MANIFEST.json'),'files':count,'sealed_components':n,'review_records':20,'model_calls':0,'external_source_paths_required':False,'task13_teammate_verification':'pending'}
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['before','after']);a=p.parse_args(argv)
 try:
  result=verify()
  if a.stage:result['verification_stage']=a.stage
  print(json.dumps(result,indent=2));return 0
 except Exception as e:
  result={'integrity':'FAIL','error':str(e),'packet_manifest_sha256':sha(P/'SHA256_MANIFEST.json')if(P/'SHA256_MANIFEST.json').is_file()else None}
  if a.stage:result['verification_stage']=a.stage
  print(json.dumps(result,indent=2));return 1
if __name__=='__main__':sys.exit(main())
