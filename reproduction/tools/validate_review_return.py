"""F2 correction: return completeness, evidence outcome and final acceptance are distinct."""
import argparse,datetime,json,sys
from pathlib import Path
from packet_common import P,load,sha,local
from verify_handover import verify
from return_evidence import digest,integrity_report,validate_execution
FIELDS={'support':{'sufficient','partial','absent','uncertain','not_reviewed'},'core_usable':{'yes','no','uncertain','not_reviewed'},'answer_category':{'correct_supported','correct_unsupported','incorrect','abstention','mixed','uncertain','not_reviewed'},'extra_error':{'yes','no','uncertain','not_reviewed'},'instruction_followed':{'yes','no','uncertain','not_applicable','not_reviewed'}}
BINDINGS=('record_id','run_id','condition','policy','request_sha256','raw_response_sha256')
def validate(root,trusted_zip_sha256=None,received_zip=None):
 root=Path(root).resolve();verification=load(local(root,'VERIFICATION_RETURN.json'));answers=load(local(root,'TASK12_ANSWER_REVIEW.json'));disputes=load(local(root,'DISCREPANCIES.json'));pending=[];manifest=sha(P/'SHA256_MANIFEST.json')
 if not isinstance(disputes,list):raise ValueError('DISCREPANCIES.json must be a list')
 for label,form in [('verification',verification),('answers',answers)]:
  if form['packet_manifest_sha256']!=manifest:raise ValueError('Return belongs to a different packet manifest')
  if form.get('packet_version')!=load(P/'TASK13_STATUS.json')['version']:raise ValueError('Return package version mismatch')
  for f in ('reviewer','review_date','assistance_disclosure'):
   if not isinstance(form.get(f),str)or not form[f].strip():pending.append(label+'.'+f)
  if form.get('review_date'):datetime.date.fromisoformat(form['review_date'])
 claimed=verification.get('received_zip_sha256');receipt='CLAIM_ONLY_NOT_AUTHENTICATED'
 if claimed is None:pending.append('received_zip_sha256');receipt='MISSING_RECEIPT_CHECKSUM'
 elif not digest(claimed):raise ValueError('Received ZIP SHA-256 must be 64 hexadecimal characters')
 if trusted_zip_sha256 is not None:
  if not digest(trusted_zip_sha256):raise ValueError('Invalid trusted delivery checksum')
  if claimed is not None and claimed.lower()!=trusted_zip_sha256.lower():raise ValueError('Received ZIP checksum differs from trusted delivery checksum')
  if claimed is not None:receipt='MATCHES_TRUSTED_DELIVERY_CHECKSUM'
 if received_zip is not None:
  actual=sha(Path(received_zip))
  if claimed is not None and claimed.lower()!=actual:raise ValueError('Received ZIP checksum differs from supplied archive')
  if claimed is not None:receipt='MATCHES_BOTH_SUPPLIED_ARCHIVE_AND_TRUSTED_CHECKSUM'if trusted_zip_sha256 is not None else'MATCHES_SUPPLIED_ARCHIVE_ONLY'
 catalog=load(P/'review/REVIEW_RECORDS.json');expected={r['record_id']:r for r in catalog};records=answers['records'];ids=[r['record_id']for r in records]
 if len(ids)!=len(set(ids))or set(ids)!=set(expected):raise ValueError('Missing/duplicate/unknown answer review identity')
 for r in records:
  if any(r[k]!=expected[r['record_id']][k]for k in BINDINGS):raise ValueError('Changed source binding: '+r['record_id'])
  if r['review_state']not in ('pending','reviewed','evidence_incomplete'):raise ValueError('Invalid review state')
  for f,choices in FIELDS.items():
   if r[f]not in choices:raise ValueError('Invalid '+f)
  if r['review_state']=='pending':pending.append(r['record_id'])
  elif r['review_state']=='reviewed'and any(r[f]=='not_reviewed'for f in FIELDS):raise ValueError('Reviewed row has unreviewed fields')
  if (r['review_state']=='evidence_incomplete'or any(r[f]=='uncertain'for f in FIELDS))and not r.get('comments','').strip():raise ValueError('Explain uncertainty/incompleteness: '+r['record_id'])
  if not isinstance(r['evidence_passage_numbers'],list)or any(type(n)is not int or n<1 or n>6 for n in r['evidence_passage_numbers']):raise ValueError('Invalid cited passage numbers')
 expected_checks=set(load(P/'review/VERIFICATION_RETURN_TEMPLATE.json')['checks'])
 if set(verification['checks'])!=expected_checks:raise ValueError('Verification checklist fields changed')
 for name,row in verification['checks'].items():
  status=row['status']
  if status not in ('PASS','FAIL','NOT_RUN','pending'):raise ValueError('Invalid check status')
  if status=='pending':pending.append(name)
  if status in ('FAIL','NOT_RUN')and not row.get('notes','').strip():raise ValueError('Explain FAIL/NOT_RUN: '+name)
  evidence=row.get('evidence')
  if evidence:
   f=local(root,evidence)
   if f.stat().st_size==0:raise ValueError('Empty checklist evidence: '+name)
  elif status in ('PASS','FAIL'):pending.append('evidence:'+name)
  if name in ('pristine_integrity_before','pristine_integrity_after')and evidence and status in ('PASS','FAIL'):
   if integrity_report(load(f),manifest,'before'if name=='pristine_integrity_before'else'after')!=status:raise ValueError('Checklist integrity status contradicts its report')
  if name=='saved_Task12_answer_review'and evidence and f!=local(root,'TASK12_ANSWER_REVIEW.json'):raise ValueError('Answer-review evidence must be the actual bound answer form')
 if verification.get('recommendation')not in (None,'accept_with_listed_limitations','request_changes','unable_to_verify'):raise ValueError('Invalid recommendation')
 if verification.get('recommendation')is None:pending.append('recommendation')
 row=verification['checks']['offline_reproduction'];ledger=verification.get('execution_ledger');execution_info=None
 if ledger and (root/ledger).exists():
  ledgerfile=local(root,ledger);execution=load(ledgerfile);execution_info=validate_execution(ledgerfile.parent,execution,manifest)
  if not execution_info['complete_inventory']:pending.append('execution_in_progress')
  if row.get('evidence')and local(root,row['evidence'])!=ledgerfile:raise ValueError('Offline checklist must reference the actual execution ledger')
  expected_status={'PASS':'PASS','FAIL':'FAIL','PASS_WITH_NOT_RUN':'NOT_RUN','IN_PROGRESS':'pending'}[execution_info['result']]
  if row['status']!='pending' and not(execution_info['result']=='IN_PROGRESS'and row['status']in ('FAIL','NOT_RUN'))and row['status']!=expected_status:raise ValueError('Offline checklist contradicts execution result')
 elif row['status']!='NOT_RUN':pending.append('execution_ledger')
 statuses=[r['status']for r in verification['checks'].values()]
 outcome='PENDING'if pending else'FAIL'if'FAIL'in statuses else'NOT_RUN'if all(s=='NOT_RUN'for s in statuses)else'PASS_WITH_NOT_RUN'if'NOT_RUN'in statuses else'PASS'
 return {'schema':'VALID','completion':'PENDING'if pending else'COMPLETE_RETURN','verification_result':outcome,'received_zip_verification':receipt,'review_records':len(records),'uncertain_or_incomplete_rows':sum(r['review_state']=='evidence_incomplete'or any(r[f]=='uncertain'for f in FIELDS)for r in records),'pending_fields':sorted(set(pending)),'execution':execution_info,'recommendation':verification.get('recommendation'),'scientific_correctness_verified_by_tool':False,'Suresh_final_acceptance':'pending separate decision'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--return-dir',type=Path,required=True);p.add_argument('--trusted-zip-sha256');p.add_argument('--received-zip',type=Path);a=p.parse_args()
 try:
  verify();result=validate(a.return_dir,a.trusted_zip_sha256,a.received_zip);print(json.dumps(result,indent=2));sys.exit(2 if result['completion']=='PENDING'else 0)
 except Exception as e:print(json.dumps({'schema':'INVALID','error':str(e)},indent=2));sys.exit(1)
