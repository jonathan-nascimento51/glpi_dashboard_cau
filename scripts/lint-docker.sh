#!/bin/bash
set -euo pipefail

# Validate COPY/ADD paths in Dockerfiles
missing=0
repo_root=$(git rev-parse --show-toplevel)
for dockerfile in $(find . -name Dockerfile -not -path "*/node_modules/*" -not -path "*/.venv/*" -not -path "./labs/prototypes/*"); do
  context=$(dirname "$dockerfile")
  awk '/^(COPY|ADD)/ {for(i=2;i<NF;i++){gsub(/"/,"",$i); if($i!~/^--/){print $i}}}' "$dockerfile" | while read -r src; do
    [[ "$src" = /* ]] && continue
    if ! compgen -G "$context/$src" > /dev/null && ! compgen -G "$repo_root/$src" > /dev/null; then
      echo "Missing path $src in $dockerfile" >&2
      missing=1
    fi
  done
done

# Validate build contexts in docker-compose files
for compose in $(find . -name 'docker-compose*.yml' -not -path './labs/prototypes/*'); do
  docker_compose_dir=$(dirname "$compose")
  python - <<PY > /tmp/lint_py_output
import yaml, pathlib
from pathlib import Path
with open("$compose") as fh:
    data = yaml.safe_load(fh)
for svc, conf in (data.get('services') or {}).items():
    build = conf.get('build')
    if build:
        if isinstance(build, dict):
            ctx = build.get('context', '.')
            df = build.get('dockerfile', 'Dockerfile')
        else:
            ctx = build
            df = 'Dockerfile'
        path = (Path("$docker_compose_dir")/ctx).resolve()
        if not (path/df).exists():
            print(f"No Dockerfile in {path} for {svc}")
    for vol in conf.get('volumes', []) or []:
        host = str(vol).split(':')[0]
        if host.startswith('./'):
            p = (Path("$docker_compose_dir")/host).resolve()
            if not p.exists():
                print(f"Volume path {p} referenced in {svc} does not exist")
PY
  if [ -s /tmp/lint_py_output ]; then
    cat /tmp/lint_py_output >&2
    missing=1
  fi
  rm -f /tmp/lint_py_output
done

exit $missing
