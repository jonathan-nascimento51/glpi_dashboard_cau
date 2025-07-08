#!/bin/sh
set -euo pipefail

# Ensure required environment variables are present
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"
: "${DB_NAME:?DB_NAME is required}"

export PGPASSWORD="$POSTGRES_PASSWORD"

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres <<SQL
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
      CREATE USER "${DB_USER}" PASSWORD '${DB_PASSWORD}';
   END IF;
END
$$;

DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}') THEN
      CREATE DATABASE "${DB_NAME}" OWNER "${DB_USER}";
   END IF;
END
$$;
SQL

echo "Database \"$DB_NAME\" and user \"$DB_USER\" ensured"
