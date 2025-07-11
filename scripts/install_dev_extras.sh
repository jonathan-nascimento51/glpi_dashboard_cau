#!/usr/bin/env bash
set -euo pipefail

# Install packages listed under [project.optional-dependencies].dev
python <<'PY'
import subprocess, sys, tomllib
from pathlib import Path

with Path('pyproject.toml').open('rb') as f:
    data = tomllib.load(f)

pkgs = data.get('project', {}).get('optional-dependencies', {}).get('dev', [])
if not pkgs:
    print('No dev optional dependencies found.')
    raise SystemExit(0)

print('Installing optional dev packages:', ' '.join(pkgs))
subprocess.check_call([sys.executable, '-m', 'pip', 'install', *pkgs])
PY
EOF
