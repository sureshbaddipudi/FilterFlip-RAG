"""Pinned public checkpoint files and local integrity checks."""
import hashlib
import json
from pathlib import Path

MODEL_ID = 'sentence-transformers/paraphrase-MiniLM-L6-v2'
REVISION = 'c9a2bfebc254878aee8c3aca9e6844d5bbb102d1'
FILES = ['config.json','config_sentence_transformers.json','modules.json',
         'sentence_bert_config.json','model.safetensors','tokenizer.json',
         'tokenizer_config.json','special_tokens_map.json','vocab.txt','1_Pooling/config.json']


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def verify_record(path):
    record=json.loads(Path(path).read_text())
    if record['model_id']!=MODEL_ID or record['revision']!=REVISION:
        raise ValueError('Unexpected checkpoint identity.')
    snapshot=Path(record['snapshot'])
    if snapshot.name!=REVISION or set(record['sha256'])!=set(FILES):
        raise ValueError('Unexpected snapshot/file manifest.')
    for name,expected in record['sha256'].items():
        if digest(snapshot/name)!=expected:
            raise ValueError('Checkpoint file changed: '+name)
    if json.loads((snapshot/'sentence_bert_config.json').read_text())['max_seq_length']!=128:
        raise ValueError('Checkpoint native window is not 128.')
    return snapshot,record
