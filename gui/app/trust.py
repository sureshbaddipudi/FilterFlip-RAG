"""Bounded TrustRAG stage-1 replay on frozen contexts/embeddings, with fresh decisions.

No saved answer, support judgment or historical kept mask is an input here.
"""
import io,sys,time,warnings,importlib,importlib.metadata,re
from pathlib import Path
from safety import load,read,digest,require
ROOT=Path(__file__).resolve().parent
CONDITIONS=('C','BN1','PN1')
def catalog():
    rows=load(ROOT/'data/trust_contexts.json')
    return {r['case_id'] for r in rows}
def validate_texts(passages):
    require(len(passages)==5,'TrustRAG requires exactly five study passages')
    for passage in passages:
        text=passage['text']
        require(isinstance(text,str) and len(text.encode())<=32768,'Trust passage size exceeded')
        # ROUGE normalizes to lowercase ASCII word/digit tokens before Porter stemming.
        require(all(len(token)<=256 for token in re.findall('[a-z0-9]+',text.lower())), 'Trust stemmer token budget exceeded')

def context(case_id,condition):
    require(condition in CONDITIONS,'Unsupported TrustRAG condition')
    profile=load(ROOT/'trust_profile.json')
    raw=read(ROOT/'data/trust_contexts.json')
    require(digest(raw)==profile['contexts_sha256'],'Trust context identity mismatch')
    from safety import decode
    matches=[r for r in decode(raw) if r['case_id']==case_id and r['condition']==condition]
    require(len(matches)==1,'Case outside fixed TrustRAG panel')
    row=matches[0]
    require(len(row['retrieved'])==5 and len(row['embedding_rows'])==5,'Invalid TrustRAG context')
    validate_texts(row['retrieved'])
    for p in row['retrieved']:require(digest(p['text'].encode())==p['text_sha256'],'Trust passage identity mismatch')
    return row

def engine(profile):
    runtime=ROOT/'trust_runtime'
    for name,expected in profile['runtime_files'].items():
        p=runtime/name
        require(not Path(name).is_absolute() and '..' not in Path(name).parts and p.resolve().is_relative_to(runtime),'Runtime path escape')
        require(digest(read(p))==expected,'Trust runtime identity mismatch: '+name)
    require(digest(read(ROOT/'trust_native.py'))==profile['native_sha256'],'Trust filter identity mismatch')
    # Scoped to the backend process; the installed environment is not modified.
    sys.path.insert(0,str(runtime))
    for name,version in profile['versions'].items():require(importlib.metadata.version(name)==version,'Trust dependency mismatch: '+name)
    for name in ('nltk','rouge_score'):
        module=importlib.import_module(name)
        require(Path(module.__file__).resolve().is_relative_to(runtime),'Unexpected Trust runtime import: '+name)
    return importlib.import_module('trust_native')

def map_output(vectors,texts,out_vectors,out_texts):
    import numpy as np
    require(len(out_vectors)==len(out_texts),'Trust output length mismatch')
    remaining=set(range(len(texts)));kept=[]
    for vec,text in zip(out_vectors,out_texts):
        matches=[i for i in remaining if texts[i]==text and np.array_equal(vectors[i],vec)]
        require(len(matches)==1,'Ambiguous or foreign Trust output')
        kept.append(matches[0]);remaining.remove(matches[0])
    return kept

def compute(case_id,condition):
    row=context(case_id,condition);profile=load(ROOT/'trust_profile.json');native=engine(profile)
    import numpy as np
    from threadpoolctl import threadpool_limits
    raw=read(ROOT/'data/trust_embeddings.npy',16*1024*1024)
    require(digest(raw)==profile['embeddings_sha256'],'Trust embeddings identity mismatch')
    vectors=np.load(io.BytesIO(raw),allow_pickle=False)
    require(vectors.ndim==2 and vectors.shape[1]==768 and vectors.dtype==np.float32 and np.isfinite(vectors).all(),'Invalid Trust embeddings')
    indices=row['embedding_rows'];require(all(type(i) is int and 0<=i<len(vectors) for i in indices),'Invalid embedding row')
    emb=vectors[indices];texts=[p['text'] for p in row['retrieved']]
    start=time.monotonic()
    with threadpool_limits(limits=4),warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        out_emb,out_texts=native.k_mean_filtering(emb,texts,set(),True)
    kept=map_output(emb,texts,out_emb,out_texts)
    timing=time.monotonic()-start
    return row,{'retrieved':row['retrieved'],'retrieval':{'track':'fixed_trustrag_context','notice':'Saved five passages and verified SimCSE embeddings; fresh stage-1 filtering. Retrieval and embeddings are not rerun.'},
        'policies':{'U':{'kept':list(range(5)),'representatives':list(range(5)),'source':'unfiltered_fixed_context','semantic_support':'unreviewed','seconds':0},
                    'T':{'kept':kept,'representatives':list(range(5)),'source':'fresh_trustrag_stage1_filter','semantic_support':'unreviewed','seconds':timing,'warnings':[str(w.message) for w in caught]}},
        'inserted_documents':[],'answers':{},'embedding_rows':indices,'trust_identity':{'source_sha256':profile['source_sha256'],'filter_sha256':profile['native_sha256'],'embeddings_sha256':profile['embeddings_sha256'],'contexts_sha256':profile['contexts_sha256'],'versions':profile['versions']}}
