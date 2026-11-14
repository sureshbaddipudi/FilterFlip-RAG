"""Policy boundary: texts and numeric scores only; no evaluator metadata."""
import math
from common import require, sha

def validate_texts(texts):
    require(isinstance(texts,list) and 1<=len(texts)<=6,'Expected one to six texts')
    require(all(isinstance(t,str) and 0<len(t)<=50000 for t in texts),'Invalid text')

def exact_groups(texts):
    validate_texts(texts)
    groups=[];lookup={}
    for i,t in enumerate(texts):
        # String equality, including whitespace and Unicode, is the criterion.
        if t not in lookup:lookup[t]=len(groups);groups.append([])
        groups[lookup[t]].append(i)
    return groups

def near_groups(texts,scores,matrix):
    validate_texts(texts);n=len(texts)
    require(len(scores)==n and len(matrix)==n,'Score shape mismatch')
    values=list(scores)+[v for row in matrix for v in row]
    require(all(type(v) in (int,float) and math.isfinite(v) for v in values),'Nonfinite score')
    require(all(len(row)==n for row in matrix),'Similarity shape mismatch')
    require(all(-1.00001<=v<=1.00001 for v in values),'Not cosine scores')
    require(all(abs(matrix[i][j]-matrix[j][i])<=1e-5 for i in range(n) for j in range(n)),'Asymmetric matrix')
    order=sorted(range(n),key=lambda i:(-scores[i],sha(texts[i].encode()),i))
    groups=[]
    for i in order:
        for group in groups:
            if all(matrix[i][j]>=0.95 for j in group):group.append(i);break
        else:groups.append([i])
    return order,groups

def prepare_arm(arm,texts,scores,matrix):
    validate_texts(texts)
    if arm=='E':groups=exact_groups(texts);reps=[g[0] for g in groups]
    elif arm in ('CN','O'):
        order,groups=near_groups(texts,scores,matrix)
        reps=order if arm=='O' else [g[0] for g in groups]
    elif arm in ('N','U'):groups=[[i] for i in range(len(texts))];reps=list(range(len(texts)))
    else:raise ValueError('Unknown policy')
    return {'representatives':reps,'groups':groups,'singleton_bypass':arm in ('E','CN') and len(reps)==1}
