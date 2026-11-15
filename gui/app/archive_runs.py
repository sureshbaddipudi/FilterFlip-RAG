"""Explicit offline archive: dry-run by default; no automatic evidence deletion."""
import argparse,json,os,re
from pathlib import Path
from safety import load_config,load,require,save,verify_release
from operations import RunLock
TERMINAL={'completed','cancelled','failed','timed_out','resource_limit','interrupted'}
def archive(config,destination,ids,apply=False):
    cfg=load_config(config);runs=Path(cfg['runs']).resolve();dest=Path(destination).absolute()
    require(runs.is_dir() and runs.stat().st_uid==os.getuid() and not runs.stat().st_mode & 0o077,'Private run folder required')
    require(not dest.exists() and not dest.is_symlink(),'Choose a new archive destination')
    parent=dest.parent.resolve();require(parent.is_dir() and parent.stat().st_uid==os.getuid() and not parent.stat().st_mode & 0o022,'Archive parent must be user-owned and not group/other writable')
    dest=parent/dest.name
    for p in [Path(__file__).resolve().parent.parent,runs]+[Path(cfg[k]).resolve() for k in ('package','encoder','ollama_models')]:
        require(not dest.is_relative_to(p) and not p.is_relative_to(dest),'Archive overlaps code, inputs or active runs')
    require(parent.stat().st_dev==runs.stat().st_dev,'Archive must be on the same filesystem for atomic moves')
    require(ids and len(ids)==len(set(ids)) and all(isinstance(i,str) and re.fullmatch('[0-9a-f]{32}',i) for i in ids),'Supply unique full run IDs')
    lock=RunLock(runs)
    try:
        for key in ids:
            folder=runs/key;require(folder.is_dir() and not folder.is_symlink(),'Missing or linked run')
            state=load(folder/'state.json');require(state.get('run_id')==key and state.get('status') in TERMINAL,'Only recorded terminal jobs can be archived')
            require(not any(p.is_symlink() for p in folder.rglob('*')),'Linked run content refused')
        result={'action':'archive' if apply else 'preview','run_ids':ids,'destination':str(dest),'moved':[]}
        if apply:
            dest.mkdir(mode=0o700);save(dest/'ARCHIVE_RECEIPT.json',result)
            for key in ids:
                os.rename(runs/key,dest/key);result['moved'].append(key);save(dest/'ARCHIVE_RECEIPT.json',result)
        return result
    finally:lock.close()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--destination',required=True);p.add_argument('--run-id',action='append',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
    os.umask(0o077);verify_release();print(json.dumps(archive(a.config,a.destination,a.run_id,a.apply),indent=2))
