#!/usr/bin/env bash
set -euo pipefail

TARGET="${HC_TARGET:-backend}"

case "$TARGET" in
  frontend)
    curl -f "http://localhost:${FRONTEND_INTERNAL_PORT:-80}/" >/dev/null
    ;;
  redis)
    redis-cli ping | grep -q PONG
    ;;
  db)
    pg_isready -U "${POSTGRES_USER:-postgres}" >/dev/null
    ;;
  backend)
    curl -f http://localhost:8000/health >/dev/null
    ;;
  *)
    echo "Unknown HC_TARGET: $TARGET" >&2
    exit 1
    ;;
esac
