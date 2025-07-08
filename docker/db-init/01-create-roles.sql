-- Role definitions for GLPI Dashboard database
-- migration_user: used by database migrations to alter schema objects
-- app_readwrite: read/write access for application runtime
-- app_readonly: read-only access for reporting and analytics

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'migration_user') THEN
        CREATE ROLE migration_user;
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_readwrite') THEN
        CREATE ROLE app_readwrite;
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_readonly') THEN
        CREATE ROLE app_readonly;
    END IF;
END$$;

-- assign privileges to application user
GRANT app_readwrite TO "user";
GRANT migration_user TO "user";

-- allow migration role to create objects
GRANT CREATE, USAGE ON SCHEMA public TO migration_user;

-- grant privileges on existing tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_readwrite;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;

-- ensure future tables inherit privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_readwrite;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_readonly;
