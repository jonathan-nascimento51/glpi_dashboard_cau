#!/bin/bash
# Run jscodeshift import refactoring for each file pair in a mapping file.
# Usage: ./scripts/run_ts_codemod.sh [mapping.json]

set -euo pipefail

MAP=${1:-scripts/refactor/file_map.json}

if ! command -v jq >/dev/null; then
  echo "jq is required" >&2
  exit 1
fi

jq -r 'to_entries[] | "\(.key)\t\(.value)"' "$MAP" | while IFS=$'\t' read -r OLD_FILE NEW_FILE; do
  mkdir -p "$(dirname "$NEW_FILE")"
  git mv "$OLD_FILE" "$NEW_FILE"

  npx jscodeshift -t ./scripts/update-imports.js ./src \
    --parser=tsx \
    --extensions=ts,tsx \
    --oldPath="$OLD_FILE" \
    --newPath="$NEW_FILE"

done
