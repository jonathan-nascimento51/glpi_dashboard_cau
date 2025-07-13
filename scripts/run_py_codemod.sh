#!/usr/bin/env bash
# Run Rope-based refactoring to move a Python file and update imports.
# Usage: ./scripts/run_py_codemod.sh <old_file> <new_dir>
# Example:
#   ./scripts/run_py_codemod.sh src/shared/utils/resilience/circuit_breaker.py src/backend/adapters/resilience/

set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <old_file> <new_dir>" >&2
  exit 1
fi

OLD_FILE=$1
NEW_DIR=$2
BASENAME=$(basename "$OLD_FILE")
NEW_PATH="$NEW_DIR/$BASENAME"

mkdir -p "$NEW_DIR"

python ./scripts/refactor_move.py . "$OLD_FILE" "$NEW_PATH"
