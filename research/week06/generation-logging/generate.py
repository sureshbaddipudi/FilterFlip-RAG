"""Execute a frozen answer queue on an owned local service after offline preflight."""
import argparse
from pathlib import Path
import sys
from common import *
from runtime import Worker,Journal
from generation_worker import validate_request

def main(a):
    queue=Path(a.queue).resolve();package=Path(a.package).resolve()
    manifest=decode(read(queue/'REQUEST_MANIFEST.json'))
    require(manifest['code']==code_hashes(),'Generation code changed after queue freeze')
    require(manifest['fresh_attempt_cap']==228 and manifest['wall_seconds_cap']==14400,'Unexpected limits')
    for name,digest in manifest['files'].items():verified(queue,name,digest)
    for name,digest in manifest['source_files'].items():verified(package/'reference',name,digest)
    requests=decode(read(queue/'new_requests.json'));require(len(requests)<=228,'Too many new requests')
    model_store=Path(a.models).resolve(strict=True)
    require(not model_store.is_relative_to(package),'Use the live local Ollama cache, not frozen reference storage')
    hashes=decode(read(package/'REFERENCE_SHA256.json'))
    prefix='output/filterflip_study_v1_answers/tokenizer/'
    for name in ('vocab.json','merges.txt'):verified(package/'reference',prefix+name,hashes[prefix+name])
    from transformers import Qwen2Tokenizer
    tokenizer=Qwen2Tokenizer(vocab_file=str(package/'reference'/prefix/'vocab.json'),merges_file=str(package/'reference'/prefix/'merges.txt'),
       eos_token='<|im_end|>',additional_special_tokens=['<|im_start|>','<|im_end|>'])
    estimates={}
    for h,req in requests.items():
        validate_request(req);require(sha(canonical(req))==h,'Request hash mismatch')
        system,user=req['messages']
        prompt=f"<|im_start|>system\n{system['content']}<|im_end|>\n<|im_start|>user\n{user['content']}<|im_end|>\n<|im_start|>assistant\n"
        n=len(tokenizer.encode(prompt,add_special_tokens=False));require(n+128+64<=4096,'Prompt does not fit')
        estimates[h]=n
    binary=Path(a.ollama_binary).resolve(strict=True);binary_sha=sha(read(binary,1024*1024*1024))
    identity={'queue_sha256':sha(read(queue/'REQUEST_MANIFEST.json')),'code':code_hashes(),
      'ollama_binary_sha256':binary_sha,'model_store':str(model_store),'tokenizer_files':{n:hashes[prefix+n] for n in ('vocab.json','merges.txt')}}
    forbidden=[queue,package,model_store,Path(__file__).resolve().parent]
    out=Path(a.out).resolve()
    if a.resume:require(out.is_dir() and all(not out.is_relative_to(x) for x in forbidden),'Invalid resume directory')
    else:out=new_directory(out,forbidden)
    lock=out/'RUN.lock'
    with lock.open('x') as f:f.write('Exclusive owned local generation\n')
    j=None;worker=None
    try:
        j=Journal(out/'journal.jsonl',identity,phase='generation')
        finished={e['id'] for e in j.events if e['kind']=='done'}
        if set(requests)<=finished:
            if not (out/'generated_answers.json').exists():
                write_new(out/'generated_answers.json',{'identity':identity,'answers':{e['id']:e['response'] for e in j.events if e['kind']=='done'},'independent_review':'pending'})
            print('All requests already complete; no inference.');return
        j.start()
        worker=Worker([sys.executable,'-u',str(Path(__file__).with_name('generation_worker.py')),
          '--binary',str(binary),'--binary-sha',binary_sha,'--models',str(model_store),'--response-log',str(out/'received_responses.jsonl')],min(60,j.remaining()))
        count=0
        for h,req in sorted(requests.items()):
            if h in finished:continue
            j.call(worker,h,{'op':'generate','request':req,'estimated_tokens':estimates[h]});count+=1
            if a.stop_after_requests and count>=a.stop_after_requests:break
        completed={e['id']:e['response'] for e in j.events if e['kind']=='done'}
        if set(completed)==set(requests) and not (out/'generated_answers.json').exists():
            write_new(out/'generated_answers.json',{'identity':identity,'answers':completed,'independent_review':'pending'})
        print(f'Saved {len(completed)}/{len(requests)} new answers. Human outcome review pending.')
    except BaseException as error:
        if j and j.started is not None:j.append('fault',id='generation',error_type=type(error).__name__)
        raise
    finally:
        if worker:worker.close()
        if j and j.started is not None:j.finish()
        lock.unlink()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['queue','package','out','models','ollama-binary']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--resume',action='store_true');p.add_argument('--stop-after-requests',type=int)
    a=p.parse_args()
    if a.stop_after_requests is not None:require(a.stop_after_requests>0,'Stop count must be positive')
    main(a)
