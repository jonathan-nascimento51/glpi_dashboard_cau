DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'user') THEN
      CREATE USER "user" PASSWORD 'password';
   END IF;
END
$$;

DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'glpi_dashboard') THEN
      CREATE DATABASE glpi_dashboard OWNER "user";
   END IF;
END
$$;
