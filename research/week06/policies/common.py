"""Bounded, deterministic file operations for the Week-6 development runner."""
import hashlib
import json
import os
from pathlib import Path

def require(ok, message):
    if not ok: raise ValueError(message)

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',', ':'),allow_nan=False).encode()

def sha(raw): return hashlib.sha256(raw).hexdigest()

def unique_object(pairs):
    result={}
    for key,value in pairs:
        require(key not in result, 'Duplicate JSON key')
        result[key]=value
    return result

def decode(raw):
    return json.loads(raw,object_pairs_hook=unique_object,parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))

def read(path, limit=64*1024*1024):
    path=Path(path)
    require(path.is_file() and path.stat().st_size<=limit,'Missing or oversized input: '+str(path))
    with path.open('rb') as f: raw=f.read(limit+1)
    require(len(raw)<=limit,'Oversized input')
    return raw

def confined(root, name):
    root=Path(root).resolve(strict=True)
    require(isinstance(name,str) and not Path(name).is_absolute(),'Invalid relative name')
    path=(root/name).resolve(strict=True)
    require(path.is_relative_to(root),'Path escapes root')
    return path

def verified(root,name,digest):
    raw=read(confined(root,name))
    require(sha(raw)==digest,'Hash mismatch: '+name)
    return raw

def new_directory(path, forbidden):
    path=Path(path).resolve()
    require(not path.exists(),'Output already exists')
    require(all(not path.is_relative_to(Path(r).resolve()) for r in forbidden),'Output is inside protected input')
    path.mkdir(parents=True)
    return path

def write_new(path,value):
    raw=json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False).encode()+b'\n'
    with Path(path).open('xb') as f:
        f.write(raw);f.flush();os.fsync(f.fileno())

def indices(values,n):
    require(isinstance(values,list) and all(type(i) is int and 0<=i<n for i in values),'Invalid output index')
    require(len(values)==len(set(values)),'Duplicate output index')
    return values

def code_hashes():
    root=Path(__file__).resolve().parent
    return {p.name:sha(read(p)) for p in sorted(root.glob('*.py'))}
