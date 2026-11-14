"""Fixed offline native worker. Imported by no preparation or synthetic test path."""
import argparse
import contextlib
import importlib.metadata
import sys
import time
from pathlib import Path
from common import *

def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',required=True);p.add_argument('--vendor',required=True);p.add_argument('--model',required=True);a=p.parse_args()
    profile=decode(read(a.profile));vendor=Path(a.vendor).resolve();model_path=Path(a.model).resolve()
    for name,digest in profile['vendor_files'].items():verified(vendor,name,digest)
    actual={x.relative_to(vendor).as_posix() for x in (vendor/'ragdefender').rglob('*.py')}
    require(actual==set(profile['vendor_files']),'Unexpected vendor Python source files')
    # Standard HF snapshots contain symlinks into blob storage; exact hashes bind their bytes.
    for name,digest in profile['model_files'].items():require(sha(read(model_path/name,512*1024*1024))==digest,'Model hash mismatch: '+name)
    for name,version in profile['versions'].items():require(importlib.metadata.version(name)==version,'Dependency version mismatch: '+name)
    sys.path.insert(0,str(vendor))
    with contextlib.redirect_stdout(sys.stderr):
        import numpy as np
        import torch
        import ragdefender
        from sentence_transformers import SentenceTransformer
        require(Path(ragdefender.__file__).resolve().parent==(vendor/'ragdefender').resolve(),'Wrong imported vendor')
        torch.set_num_threads(4);torch.manual_seed(0);np.random.seed(0)
        model=SentenceTransformer(str(model_path),device='cpu',local_files_only=True,trust_remote_code=False)
        require(model.max_seq_length==256,'Unexpected encoder window')
        defender=ragdefender.RAGDefender(embedder=model,task_type='single_hop',device='cpu',m=5,p=2)
    print(json.dumps({'status':'ready','versions':profile['versions']}),flush=True)
    while True:
        line=sys.stdin.buffer.readline(512*1024+1)
        if not line:return
        try:
            require(len(line)<=512*1024,'Worker input too large');job=decode(line)
            require(set(job)=={'op','question','texts'},'Unexpected worker fields')
            from policies import validate_texts
            texts=job['texts'];validate_texts(texts)
            require(isinstance(job['question'],str) and len(job['question'])<=10000,'Invalid question')
            sizes=[len(model.tokenizer(t,add_special_tokens=True,truncation=False,verbose=False)['input_ids']) for t in texts]
            require(max(sizes)<=256,'Filter would truncate')
            require(len(model.tokenizer(job['question'],add_special_tokens=True,truncation=False)['input_ids'])<=256,'Query would truncate')
            started=time.monotonic()
            with contextlib.redirect_stdout(sys.stderr):
                if job['op']=='scores':
                    vectors=model.encode([job['question']]+texts,normalize_embeddings=True)
                    result={'scores':(vectors[1:] @ vectors[0]).tolist(),'matrix':(vectors[1:] @ vectors[1:].T).tolist()}
                elif job['op']=='native':
                    safe,removed=defender.defend(job['question'],texts,return_indices=True)
                    removed=indices([int(i) for i in removed],len(texts));kept=[i for i in range(len(texts)) if i not in removed]
                    require(safe==[texts[i] for i in kept],'Native return order mismatch')
                    result={'kept':kept}
                else:raise ValueError('Unknown worker operation')
            result.update(status='ok',seconds=time.monotonic()-started,token_counts=sizes)
            print(json.dumps(result,allow_nan=False),flush=True)
        except Exception as error:
            print(json.dumps({'status':'fault','error_type':type(error).__name__,'error':str(error)[:500]}),flush=True)
            return

if __name__=='__main__':
    try:main()
    except Exception as error:
        print(json.dumps({'status':'fault','error_type':type(error).__name__,'error':str(error)[:500]}),flush=True)
        sys.exit(1)
