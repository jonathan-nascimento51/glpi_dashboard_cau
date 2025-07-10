#!/usr/bin/env bash
set -euo pipefail

# Locate the frontend directory
FRONTEND_DIR="$(cd "$(dirname "$0")/.." && pwd -P)"

# Map paths correctly for Docker on Windows/WSL
if command -v cygpath >/dev/null; then
    WIN_PATH="$(cygpath -w "$FRONTEND_DIR")"
    HOST_PATH="${WIN_PATH//\\/\/}"
elif command -v wslpath >/dev/null; then
    HOST_PATH="$(wslpath -m "$FRONTEND_DIR")"
else
    HOST_PATH="$FRONTEND_DIR"
fi

echo "🔄 Removing node_modules and package-lock.json..."
rm -rf "$FRONTEND_DIR/node_modules" "$FRONTEND_DIR/package-lock.json"

echo "🐳 Running npm install inside Docker..."
docker run --rm \
  -v "${HOST_PATH}:/app" \
  node:20-alpine \
  sh -c "cd /app && npm install --legacy-peer-deps --prefer-offline --no-audit --progress=false"

# Fix ownership if running as root
if [[ "$(id -u)" -eq 0 && -n "${SUDO_UID:-}" ]]; then
    echo "🔧 Fixing file ownership..."
    chown -R "${SUDO_UID}:${SUDO_GID:-$SUDO_UID}" "$FRONTEND_DIR"
elif [[ "$(id -u)" -ne 0 ]]; then
    echo "🔧 Fixing file ownership..."
    chown -R "$(id -u):$(id -g)" "$FRONTEND_DIR"
fi

echo "✅ package-lock.json regenerated in: $FRONTEND_DIR"
