#!/usr/bin/env python3
"""Check annotation structure and source quotes; never automatically judge truth."""
import argparse
import hashlib
import json
from pathlib import Path

def compact(s):return ' '.join(s.split())

def validate(labels,candidates):
    allowed={c['case_id']:c for c in candidates if c['screen_status']=='pending_support_review'}
    errors=[];counts={'eligible':0,'exclude':0,'pending':0}
    if not isinstance(labels,list):return ['Labels must be a JSON array.'],counts
    if any(not isinstance(r,dict) for r in labels):return ['Every label must be an object.'],counts
    ids=[r.get('case_id') for r in labels]
    if len(ids)!=len(set(ids)) or set(ids)!=set(allowed):
        return ['The labels must contain exactly the frozen candidate IDs, once each.'],counts
    fields=['reviewer','decision','target_document_id','expected_answer','support_quote','source_qualification','exclusion_reason','notes']
    for r in labels:
        cid=r['case_id'];c=allowed[cid]
        if any(not isinstance(r.get(k),str) for k in fields):errors.append(cid+': missing or non-string field');continue
        if not isinstance(r.get('answer_aliases'),list) or any(not isinstance(x,str) for x in r['answer_aliases']):
            errors.append(cid+': answer_aliases must be a list of strings');continue
        decision=r['decision']
        if decision not in counts:errors.append(cid+': unknown decision');continue
        counts[decision]+=1
        if decision=='pending':continue
        if not r['reviewer'].strip():errors.append(cid+': reviewer required')
        if decision=='exclude':
            if not r['exclusion_reason'].strip():errors.append(cid+': source-based exclusion reason required')
            continue
        docs={d['document_id']:d['text'] for d in c['qrel_documents']}
        if r['target_document_id'] not in docs:errors.append(cid+': target document not in frozen qrels');continue
        if not r['expected_answer'].strip():errors.append(cid+': expected answer required')
        quote=compact(r['support_quote'])
        if not quote or quote not in compact(docs[r['target_document_id']]):
            errors.append(cid+': support quote must occur in the chosen source (whitespace differences allowed)')
    return errors,counts

def main():
    p=argparse.ArgumentParser();p.add_argument('labels',type=Path);p.add_argument('--require-complete',action='store_true');a=p.parse_args()
    root=Path(__file__).resolve().parent
    candidates=json.loads((root/'screened/candidates.json').read_text())
    errors,counts=validate(json.loads(a.labels.read_text()),candidates)
    print(json.dumps({'counts':counts,'errors':errors,'labels_sha256':hashlib.sha256(a.labels.read_bytes()).hexdigest(),
        'meaning':'Structure/source-quote check only. Does not certify semantic support or independent review.'},indent=2))
    if errors or (a.require_complete and counts['pending']):raise SystemExit(1)

if __name__=='__main__':main()
