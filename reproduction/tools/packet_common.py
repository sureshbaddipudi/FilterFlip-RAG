"""Small standard-library integrity helpers; no network, model or write actions."""
from pathlib import Path
import hashlib,json,re
P=Path(__file__).resolve().parent.parent
RESERVED={'.git','.agents','.aws','.codex'}
def load(path):
 def pairs(items):
  d={}
  for k,v in items:
   if k in d:raise ValueError('Duplicate JSON key: '+k)
   d[k]=v
  return d
 return json.loads(Path(path).read_text(),object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON: '+x)))
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb')as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def local(root,name,exists=True):
 root=Path(root).resolve();q=Path(name)
 if not isinstance(name,str)or q.is_absolute()or '..'in q.parts:raise ValueError('Invalid relative path: '+str(name))
 p=root/q
 if not p.resolve().is_relative_to(root)or any((root/Path(*q.parts[:i])).is_symlink()for i in range(1,len(q.parts)+1)):raise ValueError('Path escape/symlink: '+name)
 if exists and not p.is_file():raise ValueError('Missing file: '+name)
 return p

def inventory(root):
 root=Path(root)
 return {str(f.relative_to(root)):sha(f)for f in root.rglob('*')if f.is_file()and f.relative_to(root).parts[0]not in RESERVED}
def verify_tree(root,manifest_name='SHA256_MANIFEST.json'):
 root=Path(root);m=load(root/manifest_name)
 if not isinstance(m,dict):raise ValueError('Manifest must be an object')
 for name,h in m.items():
  if not re.fullmatch('[0-9a-f]{64}',h)or sha(local(root,name))!=h:raise ValueError('Hash mismatch: '+name)
 
 for f in root.rglob('*'):
  if f.relative_to(root).parts[0]not in RESERVED and f.is_symlink():raise ValueError('Unexpected symlink: '+str(f))
 actual=inventory(root);actual.pop(manifest_name,None)
 if actual!=m:raise ValueError('Manifest file inventory differs at '+str(root))
 return len(m)
