#!/usr/bin/env bash
# Healthcheck script for PostgreSQL.
# Verifies the database is accepting connections using pg_isready.
set -euo pipefail

PGHOST="${POSTGRES_HOST:-localhost}"
PGUSER="${POSTGRES_USER:-postgres}"
PGDB="${POSTGRES_DB:-$PGUSER}"

exec pg_isready --host="$PGHOST" --username="$PGUSER" --dbname="$PGDB"
