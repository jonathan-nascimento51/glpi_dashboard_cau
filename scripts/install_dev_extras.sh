#!/usr/bin/env bash
set -euo pipefail

# Install packages listed under [project.optional-dependencies]
# Usage: ./scripts/install_dev_extras.sh [group]
# Defaults to "dev" if no group is provided.
GROUP="${1:-dev}"

python - "$GROUP" <<'PY'
import subprocess, sys, tomllib
from pathlib import Path

group = sys.argv[1]
with Path('pyproject.toml').open('rb') as f:
    data = tomllib.load(f)

pkgs = data.get('project', {}).get('optional-dependencies', {}).get(group, [])
if not pkgs:
    print(f'No {group} optional dependencies found.')
    raise SystemExit(0)

print(f'Installing optional {group} packages:', ' '.join(pkgs))
subprocess.check_call([sys.executable, '-m', 'pip', 'install', *pkgs])
PY
