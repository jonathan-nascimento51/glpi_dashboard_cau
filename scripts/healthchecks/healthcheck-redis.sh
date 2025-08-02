#!/usr/bin/env bash
# Healthcheck script for Redis.
# Sends a PING command and expects a PONG response.
set -euo pipefail

REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping | grep -q PONG
