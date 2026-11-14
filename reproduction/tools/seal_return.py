"""Seal a separate teammate return; no messaging or source packet edits."""
import argparse,json,zipfile
from pathlib import Path
from packet_common import P,inventory,sha
from validate_review_return import validate
from verify_handover import verify
p=argparse.ArgumentParser();p.add_argument('--return-dir',type=Path,required=True);p.add_argument('--zip',type=Path,required=True);p.add_argument('--allow-incomplete',action='store_true');p.add_argument('--trusted-zip-sha256');p.add_argument('--received-zip',type=Path);a=p.parse_args()
verify();root=a.return_dir.resolve();dest=a.zip.resolve()
if root.is_relative_to(P)or P.is_relative_to(root)or dest.is_relative_to(P)or dest.is_relative_to(root)or dest.exists()or Path(str(dest)+'.sha256').exists()or (root/'SHA256_MANIFEST.json').exists():raise ValueError('Use an unsealed separate return and new ZIP outside it')
state=validate(root,a.trusted_zip_sha256,a.received_zip)
if state['completion']=='PENDING'and not a.allow_incomplete:raise ValueError('Return is pending; report a blocker with --allow-incomplete only when intended')
(root/'RETURN_STATE.json').write_text(json.dumps(state,indent=2)+'\n');m=inventory(root);(root/'SHA256_MANIFEST.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for f in sorted(root.rglob('*')):
  if f.is_symlink():raise ValueError('No return symlinks')
  if f.is_file():z.write(f,root.name+'/'+str(f.relative_to(root)))
with zipfile.ZipFile(dest)as z:
 if z.testzip():raise ValueError('ZIP CRC failure')
sidecar=Path(str(dest)+'.sha256')
with sidecar.open('x')as f:f.write(sha(dest)+'  '+dest.name+'\n')
print(json.dumps({'zip':str(dest),'sha256':sha(dest),'return_state':state['completion'],'verification_result':state['verification_result'],'received_zip_verification':state['received_zip_verification'],'final_acceptance':'pending Suresh'},indent=2))
