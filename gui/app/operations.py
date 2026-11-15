"""Private bounded security events and an exclusive local run-archive lock."""
import fcntl,json,os,stat,threading,time
from pathlib import Path


def private_fd(path, flags):
    fd=os.open(path, flags | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    st=os.fstat(fd)
    if not stat.S_ISREG(st.st_mode) or st.st_uid!=os.getuid() or st.st_mode & 0o077 or st.st_nlink!=1:
        os.close(fd);raise ValueError('Unsafe operational file permissions')
    return fd


class RunLock:
    def __init__(self, runs):
        self.fd=None
        self.fd=private_fd(Path(runs)/'.server.lock',os.O_CREAT|os.O_RDWR)
        try:fcntl.flock(self.fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BaseException:
            os.close(self.fd);self.fd=None;raise ValueError('Run archive is in use; stop its server first')
    def close(self):
        if self.fd is not None:os.close(self.fd);self.fd=None
    def __del__(self):self.close()


class AuditLog:
    MAX_BYTES=256*1024
    def __init__(self,runs):
        self.path=Path(runs)/'security-events.jsonl';self.lock=threading.Lock();self.degraded=False
    def record(self,method,route,status,run_id=None):
        # Callers supply fixed classifications, never raw hostile paths or headers.
        row={'time_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
             'method':method,'route':route,'status':status,'run_id':run_id}
        raw=(json.dumps(row,separators=(',',':'))+'\n').encode()
        try:
            with self.lock:
                fd=private_fd(self.path,os.O_CREAT|os.O_APPEND|os.O_WRONLY)
                try:rotate=os.fstat(fd).st_size+len(raw)>self.MAX_BYTES
                finally:os.close(fd)
                if rotate:
                    one=self.path.with_suffix('.jsonl.1');two=self.path.with_suffix('.jsonl.2')
                    for old in [one,two]:
                        if old.exists() or old.is_symlink():
                            f=private_fd(old,os.O_RDONLY);os.close(f)
                    if one.exists():os.replace(one,two)
                    os.replace(self.path,one)
                fd=private_fd(self.path,os.O_CREAT|os.O_APPEND|os.O_WRONLY)
                with os.fdopen(fd,'ab') as stream:stream.write(raw);stream.flush()
            self.degraded=False
        except (OSError,ValueError):
            if not self.degraded:print('Security logging unavailable; inspect private work-folder permissions.',flush=True)
            self.degraded=True
