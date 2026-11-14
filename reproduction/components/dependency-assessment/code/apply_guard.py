#!/usr/bin/env python3
"""Apply only the reviewed local guard in an active, separate virtual environment."""
from pathlib import Path
import argparse,sys,sysconfig,hashlib,json
BEFORE='02a12ff3a946fcc91bb9f5f4a241d3f1212bfa1b0aa5e72570153a174ab94047'
AFTER='2012543e3832281d3fada834e25cd085b007bb028099c1d90d9362a5c582d162'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--packet',type=Path,default=Path(__file__).resolve().parent.parent)
a=parser.parse_args()
if sys.prefix==sys.base_prefix:raise SystemExit('Refusing: use a separate virtual environment, never the accepted base environment')
site=Path(sysconfig.get_path('purelib')).resolve();prefix=Path(sys.prefix).resolve()
if not site.is_relative_to(prefix):raise SystemExit('Refusing site-packages outside the virtual environment')
f=site/'sentence_transformers/util/misc.py'
if f.is_symlink() or not f.resolve().is_relative_to(prefix):raise SystemExit('Refusing linked/outside helper')
raw=f.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
if sha(raw)==AFTER:
 print('Reviewed local guard already present');raise SystemExit(0)
if sha(raw)!=BEFORE:raise SystemExit('Unrecognized upstream helper bytes; no change made')
meta=json.loads((a.packet/'candidate/LOCAL_GUARD.json').read_text())
if meta['before_sha256']!=BEFORE or meta['after_sha256']!=AFTER:raise SystemExit('Packet patch identity differs')
needle='    if model_name_or_path is not None and (trust_remote_code or os.path.exists(model_name_or_path)):'
replacement=('    # FilterFlip candidate guard v1: explicit trust for non-builtin module classes.\n'
 '    # The upstream 5.6 release warns but still implicitly trusts local directories.\n'
 '    if not trust_remote_code:\n'
 '        raise ValueError("Custom module classes require explicit trust_remote_code=True")\n\n'+needle)
text=raw.decode()
if text.count(needle)!=1:raise SystemExit('Expected exactly one helper branch')
changed=text.replace(needle,replacement).encode()
if sha(changed)!=AFTER:raise SystemExit('Unexpected resulting helper bytes; no change made')
f.write_bytes(changed)
print('Applied candidate-only local guard v1; disclose this local package modification. Scientific compatibility remains pending.')
