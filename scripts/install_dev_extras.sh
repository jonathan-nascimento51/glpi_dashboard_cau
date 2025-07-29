#!/usr/bin/env bash
set -euo pipefail

# Install packages from [project.optional-dependencies]
python - "$@" <<'PY'
import subprocess, sys, tomllib
from pathlib import Path

groups = sys.argv[1:] or ["dev"]

with Path("pyproject.toml").open("rb") as f:
    data = tomllib.load(f)

optional = data.get("project", {}).get("optional-dependencies", {})
pkgs = []
for g in groups:
    pkgs.extend(optional.get(g, []))

if not pkgs:
    print("No optional dependencies found for", ", ".join(groups))
    raise SystemExit(0)

print("Installing optional packages from", ", ".join(groups) + ":", " ".join(pkgs))
subprocess.check_call([sys.executable, "-m", "pip", "install", *pkgs])
PY
