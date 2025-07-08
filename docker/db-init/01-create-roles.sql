DO $$
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
$$;

-- Grant the application login user membership in the read/write role
GRANT app_readwrite TO "user";

-- Tables created by migration_user should be accessible to application roles
ALTER DEFAULT PRIVILEGES FOR ROLE migration_user
   GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_readwrite;
ALTER DEFAULT PRIVILEGES FOR ROLE migration_user
   GRANT SELECT ON TABLES TO app_readonly;
ALTER DEFAULT PRIVILEGES FOR ROLE migration_user
   GRANT USAGE, SELECT ON SEQUENCES TO app_readwrite;
ALTER DEFAULT PRIVILEGES FOR ROLE migration_user
   GRANT SELECT ON SEQUENCES TO app_readonly;
