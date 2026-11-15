"""Read-only verification of this separate GUI supplement; no models or network."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 try:
  m=json.loads((R/'SHA256_MANIFEST.json').read_text())
  if not isinstance(m,dict) or not m:raise ValueError('Empty or invalid manifest')
  for name in m:
   if Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('Invalid manifest path')
  files=list(R.rglob('*'))
  actual={f.relative_to(R).as_posix() for f in files if f.is_file() and f!=R/'SHA256_MANIFEST.json' and '__pycache__' not in f.parts}
  problems={'missing':sorted(set(m)-actual),'unexpected':sorted(actual-set(m)),
            'linked':sorted(f.relative_to(R).as_posix() for f in files if f.is_symlink()),'modified':[]}
  for name,h in m.items():
   f=R/name
   if name in actual and not f.is_symlink() and f.resolve().is_relative_to(R) and hashlib.sha256(f.read_bytes()).hexdigest()!=h:problems['modified'].append(name)
  if any(problems.values()):
   print(json.dumps(problems,indent=2));raise SystemExit('FAIL: packet verification')
 except (OSError,ValueError,TypeError) as e:raise SystemExit('FAIL: cannot verify packet: '+str(e))
 print(json.dumps({'integrity':'PASS','files':len(m),'model_calls':0,'version':json.loads((R/'RELEASE_STATUS.json').read_text())['version']}))
