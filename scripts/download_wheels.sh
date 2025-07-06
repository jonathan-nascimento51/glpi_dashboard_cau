#!/usr/bin/env bash
set -euo pipefail

DIR=${1:-./wheels}

pip download -r requirements.txt -r requirements-dev.txt -d "$DIR"

cat <<EOM
Packages saved to $DIR
Install offline with:
pip install --no-index --find-links="$DIR" -r requirements.txt -r requirements-dev.txt
EOM

