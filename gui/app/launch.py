"""Launch the fixed CPU-only localhost review demo."""
import os,subprocess,sys
from pathlib import Path
from safety import verify_release, load_config
if __name__=='__main__':
    os.umask(0o077)
    verify_release()
    root=Path(__file__).resolve().parent
    config=sys.argv[1] if len(sys.argv)==2 else str(root/'config.local.json')
    if len(sys.argv)>2:raise SystemExit('Usage: python3 launch.py [absolute-config-path]')
    load_config(config)
    raise SystemExit(subprocess.call([sys.executable,'-B',str(root/'server.py'),'--config',config],env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')))
