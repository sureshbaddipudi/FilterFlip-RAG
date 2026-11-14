#!/usr/bin/env python3
"""Fetch pinned public data; preserve native files and lossless JSONL. No inference."""
import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

SOURCES = {
    'NanoNQ': '77540146379abf95df8326a3c5bb9eb21c7146c3',
    'NanoMSMARCO': '7b8ff22f2771dc65ac5b439f222eb19a1f56abda',
}
TRUST_COMMIT = '11dcea0262d14b0e38e22e1d7ddce4a151e82a61'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

def fetch(url, path, limit=10_000_000):
    request = urllib.request.Request(url, headers={'User-Agent':'FilterFlip-research-preparation/1.0'})
    with urllib.request.urlopen(request, timeout=60) as response:
        data=response.read(limit+1)
    if len(data)>limit:
        raise ValueError('Download exceeds bounded size: '+url)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)
    return {'url':url,'path':str(path),'bytes':len(data),'sha256':digest(path)}

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    import pyarrow, pyarrow.parquet as pq
    manifest={'schema':1,'scope':'Source acquisition only; no retrieval/filter/generator outcomes',
              'pyarrow_version':pyarrow.__version__,'datasets':{},'comparator':{}}
    for name,revision in SOURCES.items():
        folder=a.out/name;folder.mkdir()
        base=f'https://huggingface.co/datasets/zeta-alpha-ai/{name}/resolve/{revision}'
        card=fetch(base+'/README.md',folder/'README.md')
        entry={'repo':'zeta-alpha-ai/'+name,'revision':revision,'card':card,'splits':{}}
        for split in ['corpus','queries','qrels']:
            item=fetch(base+'/'+split+'/train-00000-of-00001.parquet',folder/(split+'.parquet'))
            table=pq.read_table(folder/(split+'.parquet'))
            rows=table.to_pylist()
            jsonfile=folder/(split+'.jsonl')
            with jsonfile.open('x',encoding='utf-8') as f:
                for row in rows:f.write(json.dumps(row,ensure_ascii=False)+'\n')
            item.update(rows=len(rows),columns=table.column_names,jsonl_sha256=digest(jsonfile))
            entry['splits'][split]=item
        manifest['datasets'][name]=entry
        save(a.out/'acquisition.json',manifest)
        print(name,{k:v['rows'] for k,v in entry['splits'].items()},flush=True)
    folder=a.out/'TrustRAG';folder.mkdir()
    files=[]
    for file in ['README.md','defend_module.py','main_trustrag.py']:
        files.append(fetch(f'https://raw.githubusercontent.com/HuichiZhou/TrustRAG/{TRUST_COMMIT}/{file}',folder/file))
    manifest['comparator']={'repo':'https://github.com/HuichiZhou/TrustRAG','commit':TRUST_COMMIT,
                            'files':files,'executed':False}
    # Paths in the portable manifest are relative to the acquisition root.
    for entry in manifest['datasets'].values():
        for item in [entry['card']]+list(entry['splits'].values()):
            item['path']=str(Path(item['path']).relative_to(a.out))
    for item in files:item['path']=str(Path(item['path']).relative_to(a.out))
    save(a.out/'acquisition.json',manifest)

if __name__=='__main__':main()
