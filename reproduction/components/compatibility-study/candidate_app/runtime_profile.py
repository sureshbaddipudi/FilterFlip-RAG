"""Task 9 candidate-only dependency/local-guard identity checks. No adoption implied."""
from pathlib import Path
import hashlib,importlib.metadata,sys,sysconfig

def verify_runtime_profile(profile):
 for name,expected in profile['versions'].items():
  if importlib.metadata.version(name)!=expected:raise ValueError('Dependency mismatch: '+name)
 identity=profile.get('candidate_identity')
 if not isinstance(identity,dict):raise ValueError('Explicit candidate identity required')
 if identity.get('separate_virtual_environment_required') is not True or sys.prefix==sys.base_prefix:raise ValueError('Separate candidate virtual environment required')
 purelib=Path(sysconfig.get_path('purelib'));relative=Path(identity['local_guard_relative_file'])
 if relative.is_absolute() or '..' in relative.parts:raise ValueError('Invalid local guard path')
 target=purelib/relative
 if not target.resolve().is_relative_to(purelib.resolve()) or not target.is_file():raise ValueError('Local guard outside candidate environment')
 if hashlib.sha256(target.read_bytes()).hexdigest()!=identity['local_guard_sha256']:raise ValueError('Candidate local guard mismatch')
 for name,versions in identity['expected_candidate_upgrades'].items():
  if importlib.metadata.version(name)!=versions['candidate']:raise ValueError('Selected candidate dependency mismatch: '+name)
 return {'profile':identity['name'],'versions':profile['versions'],'local_guard_sha256':identity['local_guard_sha256']}
