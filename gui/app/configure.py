"""Create a separate machine-local configuration by reusing existing assets."""
import argparse, json, os, sys
from pathlib import Path
from safety import load, save, require, verify_release

def configure(source,work):
    verify_release()
    source=Path(source).resolve();work=Path(work).resolve()
    cfg=load(source);root=Path(__file__).resolve().parent
    require(not work.exists(),'Choose a new work folder; existing folders are never overwritten')
    require(not work.is_relative_to(root.parent) and not root.parent.is_relative_to(work),'Work folder must be outside the app')
    for key in ('python','package','encoder','ollama_binary','ollama_models'):
        value=cfg.get(key)
        require(isinstance(value,str) and Path(value).is_absolute() and Path(value).exists(),'Missing existing asset: '+key)
    require(cfg.get('compute_profile')=='cpu','Existing pinned CPU configuration required')
    for key in ('package','encoder','ollama_models'):
        asset=Path(cfg[key]).resolve()
        require(not work.is_relative_to(asset) and not asset.is_relative_to(work),'Work folder overlaps input assets')
    os.umask(0o077);work.mkdir(parents=True,mode=0o700)
    cfg={key:cfg[key] for key in ('python','package','encoder','ollama_binary','ollama_models')}
    cfg.update(compute_profile='cpu',runs=str(work/'runs'))
    (work/'runs').mkdir(mode=0o700);dest=work/'config.local.json';save(dest,cfg)
    return dest
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--from-config',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args()
    print('Created configuration:',configure(a.from_config,a.work))
