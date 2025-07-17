#!/bin/bash
set -e
set -o pipefail

# As variáveis POSTGRES_USER e POSTGRES_DB são usadas pela imagem base do Postgres
# para criar o usuário e o banco de dados. Este script assume que eles já existem
# e se conecta diretamente ao banco de dados da aplicação para configurar
# roles e permissões adicionais.

: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"

# A senha é lida automaticamente pela imagem base, não precisamos exportá-la aqui.

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<SQL

-- Criação de roles específicas da aplicação, se não existirem
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

-- Concede a role de leitura/escrita para o usuário principal da aplicação
GRANT app_readwrite TO "${POSTGRES_USER}";

-- Define privilégios padrão para objetos criados pelo usuário de migração.
-- Isso garante que o usuário da aplicação tenha as permissões corretas
-- em novas tabelas e sequências criadas futuramente.
ALTER DEFAULT PRIVILEGES FOR ROLE migration_user
   GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_readwrite;

ALTER DEFAULT PRIVILEGES FOR ROLE migration_user
   GRANT SELECT ON TABLES TO app_readonly;

ALTER DEFAULT PRIVILEGES FOR ROLE migration_user
   GRANT USAGE, SELECT ON SEQUENCES TO app_readwrite;

ALTER DEFAULT PRIVILEGES FOR ROLE migration_user
   GRANT SELECT ON SEQUENCES TO app_readonly;

SQL

echo "✅ Roles e permissões personalizadas foram configuradas com sucesso em '${POSTGRES_DB}'."
