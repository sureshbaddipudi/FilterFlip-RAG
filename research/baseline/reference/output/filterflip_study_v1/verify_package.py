#!/usr/bin/env python3
"""Read-only integrity check for the shipped preparation package."""
import hashlib
import json
from pathlib import Path

def main():
    root=Path(__file__).resolve().parent
    manifest=json.loads((root/'FROZEN_MANIFEST.json').read_text())
    errors=[]
    for rel,expected in manifest['files'].items():
        p=(root/rel).resolve()
        if not p.is_relative_to(root):errors.append('Invalid manifest path: '+rel);continue
        if not p.is_file():errors.append('Missing: '+rel);continue
        if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:errors.append('Changed: '+rel)
    c=json.loads((root/'screened/candidates.json').read_text())
    print(json.dumps({'checked_files':len(manifest['files']),'errors':errors,
        'candidate_count':len(c),'pending_source_review':sum(r['screen_status']=='pending_support_review' for r in c),
        'meaning':'Integrity of the frozen preparation files only; no attack results or validated answer labels.'},indent=2))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
