"""Explicit bounds and durable storage for the local review demonstration."""
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAX_FILE = 8 * 1024 * 1024
def require(ok, message):
    if not ok:
        raise ValueError(message)
def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, 'Duplicate JSON key')
        result[key] = value
    return result
def decode(raw):
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode()
def digest(raw):
    return hashlib.sha256(raw).hexdigest()
def read(path, limit=MAX_FILE):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), 'Missing or linked application file')
    with path.open('rb') as handle:
        raw = handle.read(limit + 1)
    require(len(raw) <= limit, 'File size limit exceeded')
    return raw
def load(path, limit=MAX_FILE):
    return decode(read(path, limit))
def save(path, value):
    path = Path(path)
    raw = canonical(value) + b'\n'
    require(len(raw) <= MAX_FILE, 'Output size limit exceeded')
    # Unique temp file with exclusive creation; never follow a leftover symlink.
    import tempfile
    fd, name = tempfile.mkstemp(prefix='.'+path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
def verify_release():
    manifest = load(ROOT/'RELEASE_MANIFEST.json')
    require(isinstance(manifest, dict) and bool(manifest), 'Release manifest missing')
    for name, expected in manifest.items():
        path = ROOT/name
        require(not Path(name).is_absolute() and '..' not in Path(name).parts,
                'Invalid release path')
        require(path.resolve().is_relative_to(ROOT), 'Release path escape')
        require(digest(read(path, 16*1024*1024)) == expected, 'Release integrity check failed: '+name)
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and p != ROOT/'RELEASE_MANIFEST.json'}
    require(actual == set(manifest), 'Unlisted or missing application file; run tools/verify_packet.py for details')
    require(not any(p.is_symlink() for p in ROOT.rglob('*')), 'Linked application content refused')
    return len(manifest)

STUDY_CONDITIONS = ('C','BN1','BN2','PN1','PN2','BE1','BE2','PE1','PE2')

def run_plan(mode, condition):
    if mode == 'original':
        require(condition == 'C,PN1', 'Original comparison must be C/PN1')
        return ['C','PN1'], ['U','N']
    if mode == 'trust':
        require(condition in ('C','BN1','PN1'), 'Unknown TrustRAG condition')
        return [condition], ['U','T']
    if mode == 'variants':
        require(condition in STUDY_CONDITIONS, 'Unknown study condition')
        return [condition], ['U','N']
    if mode in ('mitigation','challenge'):
        return [condition], ['U','N','E','CN']
    raise ValueError('Unknown demonstration mode')

def check_selection(data, cases, approved, benign):
    require(isinstance(data, dict) and set(data) == {'case_id', 'mode', 'condition'}, 'Unknown fields')
    require(all(isinstance(v, str) for v in data.values()), 'Expected text selections')
    cid, mode, condition = data['case_id'], data['mode'], data['condition']
    require(cid in cases, 'Unknown case')
    if mode == 'original':
        require(condition == 'C,PN1', 'Original comparison must be C/PN1')
    elif mode == 'trust':
        from trust import catalog
        require(cid in catalog() and condition in ('C','BN1','PN1'), 'Outside fixed TrustRAG panel')
    elif mode == 'variants':
        require(condition in STUDY_CONDITIONS, 'Unknown study condition')
    elif mode == 'mitigation':
        require(cid in benign and condition in ('C', 'BN1', 'PN1'), 'Outside reviewed benign panel')
    elif mode == 'challenge':
        require(cid in approved and condition in ('neutral_append', 'wrong_answer_append', 'instruction_append'),
                'Outside approved challenge panel')
    else:
        raise ValueError('Unknown demonstration mode')

def policy_decision(arm, texts, scores, matrix, native):
    """Use the unchanged Week-6 grouping rule; native sees only texts and query."""
    from policies import prepare_arm
    decision = prepare_arm(arm, texts, scores, matrix)
    representatives = decision['representatives']
    if arm == 'U' or decision['singleton_bypass']:
        kept = representatives
    else:
        indices = native([texts[i] for i in representatives])
        require(isinstance(indices, list) and all(type(i) is int and 0 <= i < len(representatives) for i in indices),
                'Native index outside input')
        require(len(indices) == len(set(indices)) and indices == sorted(indices), 'Native index order invalid')
        kept = [representatives[i] for i in indices]
    return dict(decision, kept=kept, source='fresh_filter' if arm!='U' else 'unfiltered',
                semantic_support='unreviewed')


def load_config(path):
    """Read a private, user-owned configuration without following its final link."""
    import stat
    path = Path(path).absolute()
    require(not path.resolve().is_relative_to(ROOT.parent), 'Keep configuration outside the release; use configure.py to create a separate work folder')
    parent = path.parent.stat()
    require(parent.st_uid == os.getuid() and not parent.st_mode & 0o022,
            'Config folder must belong to you and not be group/other writable; use configure.py')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as handle:
        info = os.fstat(handle.fileno())
        require(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and info.st_nlink == 1,
                'Config must be a regular file owned by you, without links')
        require(info.st_mode & 0o077 == 0, 'Config must be owner-only: chmod 600 your-config.json')
        raw = handle.read(MAX_FILE + 1)
    require(len(raw) <= MAX_FILE, 'Config too large')
    return decode(raw)


def verified_module(path, expected):
    """Verify and execute exactly the same bounded byte sequence."""
    import importlib.util
    path = Path(path)
    raw = read(path, 16 * 1024 * 1024)
    require(digest(raw) == expected, 'Retrieval module identity mismatch')
    spec = importlib.util.spec_from_file_location('frozen_retrieval', path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module
