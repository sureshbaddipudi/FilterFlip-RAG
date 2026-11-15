import sys,os,stat,shutil
sys.path.insert(0,sys.argv[1]);import safety
base=sys.argv[2]; good=base+'/work/config.local.json'
def t(name,path,expect_ok):
    try: safety.load_config(path); ok=True; msg=''
    except Exception as e: ok=False; msg=type(e).__name__+': '+str(e)[:70]
    print(('PASS ' if ok==expect_ok else 'FAIL ')+f'{name:42s} ->', 'accepted' if ok else 'refused ('+msg+')')
t('control: configure.py output (0600)',good,True)
d=base+'/cases'; shutil.rmtree(d,ignore_errors=True); os.makedirs(d,mode=0o700)
def mk(n,mode=0o600):
    p=f'{d}/{n}'; shutil.copy(good,p); os.chmod(p,mode); return p
t('group-writable config (0660)',mk('gw',0o660),False)
t('group-readable config (0640)',mk('gr',0o640),False)
t('world-readable config (0644)',mk('wr',0o644),False)
p=mk('real'); os.symlink(p,d+'/link'); t('symlink to a good config',d+'/link',False)
p=mk('hl'); os.link(p,d+'/hl2'); t('hard-linked config (nlink=2)',p,False)
os.makedirs(base+'/gwdir',mode=0o700); os.chmod(base+'/gwdir',0o770); shutil.copy(good,base+'/gwdir/c.json'); os.chmod(base+'/gwdir/c.json',0o600)
t('parent dir group-writable (0770)',base+'/gwdir/c.json',False)
os.mkfifo(d+'/fifo',0o600); t('FIFO instead of a regular file',d+'/fifo',False)
shutil.copy(good,sys.argv[1]+'/../cfg_inside.json'); os.chmod(sys.argv[1]+'/../cfg_inside.json',0o600)
t('config inside the release folder',sys.argv[1]+'/../cfg_inside.json',False)
os.remove(sys.argv[1]+'/../cfg_inside.json')
t('missing file',d+'/nope',False)
open(d+'/big','wb').write(b'{"a":"'+b'x'*(9*1024*1024)+b'"}'); os.chmod(d+'/big',0o600); t('oversized config (9 MB)',d+'/big',False)
open(d+'/dup','w').write('{"a":1,"a":2}'); os.chmod(d+'/dup',0o600); t('duplicate JSON keys',d+'/dup',False)
