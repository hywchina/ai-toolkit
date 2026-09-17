"""Verify an optional pre-populated build base before reusing its dependencies."""
import importlib.metadata as metadata
import json
import subprocess
import sys
from pathlib import Path
from pip._vendor.packaging.requirements import Requirement

missing = []
for line in Path('requirements.txt').read_text().splitlines():
    if not line or line.startswith('#'):
        continue
    req = Requirement(line)
    try:
        dist = metadata.distribution(req.name)
    except metadata.PackageNotFoundError:
        missing.append(line)
        continue
    if req.url:
        direct = json.loads(dist.read_text('direct_url.json') or '{}')
        if direct.get('vcs_info', {}).get('commit_id') != req.url.rsplit('@', 1)[1]:
            missing.append(line)
    else:
        if dist.version not in req.specifier:
            missing.append(line)
if missing:
    if '--install' in sys.argv:
        # All transitive dependencies are frozen. Install only mismatches, without
        # re-fetching an already matching Git source dependency or GPU wheel.
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', '--no-deps', *missing], check=True)
        subprocess.run([sys.executable, __file__], check=True)
        sys.exit(0)
    raise SystemExit('Frozen dependency mismatches: ' + ', '.join(missing))
print('All frozen dependencies match')
