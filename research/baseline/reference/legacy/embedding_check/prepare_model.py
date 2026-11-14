#!/usr/bin/env python3
"""Download only the pinned paraphrase checkpoint; no installation or inference."""
import argparse
import json
from pathlib import Path
from model_files import MODEL_ID,REVISION,FILES,digest,verify_record


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record',type=Path,default=Path('results/embedding_setup/paraphrase_model.json'))
    args=parser.parse_args()
    if args.record.exists():
        snapshot,_=verify_record(args.record)
        print('Existing pinned checkpoint verified:',snapshot)
        return
    from huggingface_hub import snapshot_download
    print('Downloading pinned paraphrase-MiniLM files (approximately 91 MB of weights).',flush=True)
    snapshot=Path(snapshot_download(repo_id=MODEL_ID,revision=REVISION,
                  allow_patterns=FILES,max_workers=2,token=False))
    if snapshot.name!=REVISION:
        raise ValueError('Resolved snapshot revision differs.')
    record=dict(model_id=MODEL_ID,revision=REVISION,snapshot=str(snapshot.resolve()),
                sha256={name:digest(snapshot/name) for name in FILES})
    if json.loads((snapshot/'sentence_bert_config.json').read_text())['max_seq_length']!=128:
        raise ValueError('Unexpected native input window.')
    args.record.parent.mkdir(parents=True,exist_ok=True)
    with args.record.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(record,indent=2)+'\n')
    print('Checkpoint saved and hashed. Native input window: 128 tokens.')
    print('No model inference performed. Record:',args.record)


if __name__=='__main__':
    main()
