# MySQL Quickstart

A **Development Setup** section in the README now covers the entire installation process. After completing those steps you can switch the database to MySQL.

## 1. Create the database

```sql
CREATE DATABASE glpi_dashboard CHARACTER SET utf8mb4;
CREATE USER 'dashboard'@'%' IDENTIFIED BY 'senhaSegura';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER ON glpi_dashboard.* TO 'dashboard'@'%';
FLUSH PRIVILEGES;
```

## 2. Environment variables

Add the MySQL connection details to `.env`:

```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=glpi_dashboard
DB_USER=dashboard
DB_PASSWORD=senhaSegura
```

Then run the initialization script and start the app:

```bash
PYTHONPATH=src python scripts/setup/init_db.py --drop-all
python dashboard_app.py
```

Open <http://127.0.0.1:8050> to verify everything is working.
