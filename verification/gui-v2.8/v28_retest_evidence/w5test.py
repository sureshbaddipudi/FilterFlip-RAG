import sys,os,hashlib,tempfile
sys.path.insert(0,sys.argv[1]);import safety
d=tempfile.mkdtemp();p=d+'/mod.py'
good=b"VALUE='verified'\n";evil=b"VALUE='TAMPERED'\n"
open(p,'wb').write(good);h=hashlib.sha256(good).hexdigest()
print('1 normal load:',safety.verified_module(p,h).VALUE)
# TOCTOU: attacker swaps the file on disk right AFTER the verified read
real=safety.read
def swapping_read(path,limit=safety.MAX_FILE):
    raw=real(path,limit); open(path,'wb').write(evil); return raw
safety.read=swapping_read
m=safety.verified_module(p,h);print('2 swap after read -> executed:',m.VALUE,'| disk now:',open(p,'rb').read().decode().strip())
safety.read=real; open(p,'wb').write(evil)
try: safety.verified_module(p,h);print('3 tampered before read: LOADED (BAD)')
except ValueError as e:print('3 tampered before read: refused ->',e)
