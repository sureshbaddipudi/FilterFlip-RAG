"""Build release manifests during authoring; not an instruction to reseal received files."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];A=R/'app'
def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()
app={f.relative_to(A).as_posix():digest(f) for f in sorted(A.rglob('*')) if f.is_file() and f.name!='RELEASE_MANIFEST.json' and '__pycache__' not in f.parts}
(A/'RELEASE_MANIFEST.json').write_text(json.dumps(app,indent=2)+'\n')
manifest={f.relative_to(R).as_posix():digest(f) for f in sorted(R.rglob('*')) if f.is_file() and f!=R/'SHA256_MANIFEST.json' and '__pycache__' not in f.parts}
(R/'SHA256_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Sealed',len(app),'app files and',len(manifest),'packet files')
