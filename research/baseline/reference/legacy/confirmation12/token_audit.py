import hashlib
import json
def sha(data): return hashlib.sha256(data).hexdigest()

def token_audit(embedder,rows,window):
    """Record actual tokenizer inputs, with no embedding inference."""
    embedder.max_seq_length=window
    unique={d['sha256']:d for r in rows for d in r['retrieved']}
    entries={}
    for h,d in unique.items():
        text=d['text'].strip()
        if getattr(embedder[0],'do_lower_case',False):text=text.lower()
        full=embedder.tokenizer.encode(text,add_special_tokens=True,truncation=False)
        features=embedder.tokenize([d['text']])
        used=features['input_ids'][0].tolist()
        mask=features['attention_mask'][0].tolist()
        used=[token for token,m in zip(used,mask) if m]
        if len(used)>window:raise ValueError('Tokenizer exceeded selected window.')
        entries[h]=dict(full_tokens=len(full),used_tokens=len(used),truncated=len(full)>window,
                        full_token_ids_sha256=sha(json.dumps(full).encode()),
                        used_token_ids=used,
                        decoded_used_tokens=embedder.tokenizer.decode(used,skip_special_tokens=False))
    contexts=[dict(case_id=r['case_id'],condition=r['condition'],variant=r.get('variant'),
                  any_truncated=any(entries[d['sha256']]['truncated'] for d in r['retrieved']),
                  target_truncated=next((entries[d['sha256']]['truncated'] for d in r['retrieved'] if d['id']==r['target_id']),None)) for r in rows]
    return dict(window=window,max_full_tokens=max(e['full_tokens'] for e in entries.values()),
                unique_passages=len(entries),truncated_unique_passages=sum(e['truncated'] for e in entries.values()),
                truncated_contexts=sum(c['any_truncated'] for c in contexts),entries=entries,contexts=contexts)
