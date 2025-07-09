#!/bin/sh
set -euo pipefail

# Leitura opcional de variáveis por arquivos (Docker secrets ou mounts)
if [ -n "${DB_USER_FILE:-}" ] && [ -f "$DB_USER_FILE" ]; then
  DB_USER="$(cat "$DB_USER_FILE")"
fi

if [ -n "${DB_PASSWORD_FILE:-}" ] && [ -f "$DB_PASSWORD_FILE" ]; then
  DB_PASSWORD="$(cat "$DB_PASSWORD_FILE")"
fi

: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"
: "${DB_NAME:?DB_NAME is required}"

export PGPASSWORD="$POSTGRES_PASSWORD"

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres <<SQL

-- Criação do usuário principal da aplicação, se não existir
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
      CREATE USER "${DB_USER}" PASSWORD '${DB_PASSWORD}';
   END IF;
END
\$\$;

-- Criação de roles usadas pela aplicação
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'migration_user') THEN
      CREATE ROLE migration_user NOLOGIN;
   END IF;
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_readwrite') THEN
      CREATE ROLE app_readwrite NOLOGIN;
   END IF;
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_readonly') THEN
      CREATE ROLE app_readonly NOLOGIN;
   END IF;
END
\$\$;

-- Criação do banco de dados da aplicação, se não existir
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}') THEN
      CREATE DATABASE "${DB_NAME}" OWNER "${DB_USER}";
   END IF;
END
\$\$;

-- Permissões padrão para o usuário da aplicação
GRANT app_readwrite TO "${DB_USER}";

ALTER DEFAULT PRIVILEGES FOR ROLE migration_user
   GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_readwrite;

ALTER DEFAULT PRIVILEGES FOR ROLE migration_user
   GRANT SELECT ON TABLES TO app_readonly;

ALTER DEFAULT PRIVILEGES FOR ROLE migration_user
   GRANT USAGE, SELECT ON SEQUENCES TO app_readwrite;

ALTER DEFAULT PRIVILEGES FOR ROLE migration_user
   GRANT SELECT ON SEQUENCES TO app_readonly;

SQL

echo "✅ Roles, banco de dados e permissões foram inicializados com sucesso."
