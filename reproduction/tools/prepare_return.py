"""Create new blank human return forms outside the pristine packet."""
import argparse,json
from pathlib import Path
from packet_common import P,load,sha
from verify_handover import verify

def prepare(out,received_zip=None):
 out=Path(out).resolve()
 if out.exists()or out.is_relative_to(P)or P.is_relative_to(out):raise ValueError('Choose a new return directory outside the packet')
 report=verify();report['verification_stage']='before';out.mkdir(parents=True,mode=0o700)
 for source,dest in [('VERIFICATION_RETURN_TEMPLATE.json','VERIFICATION_RETURN.json'),('TASK12_ANSWER_REVIEW_TEMPLATE.json','TASK12_ANSWER_REVIEW.json')]:
  d=load(P/'review'/source);d['packet_manifest_sha256']=sha(P/'SHA256_MANIFEST.json');
  if dest=='VERIFICATION_RETURN.json'and received_zip is not None:d['received_zip_sha256']=sha(Path(received_zip))
  (out/dest).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 (out/'pristine_before.json').write_text(json.dumps(report,indent=2)+'\n')
 (out/'DISCREPANCIES.json').write_text('[]\n')
 return {'return_directory':str(out),'human_decisions_prefilled':0,'packet_modified':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--received-zip',type=Path);a=p.parse_args();print(json.dumps(prepare(a.out,a.received_zip),indent=2))
