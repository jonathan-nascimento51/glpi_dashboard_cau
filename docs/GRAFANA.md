# Grafana Usage Guide

This project ships a Grafana container for local metrics visualization. The standard development stack is launched with `docker compose up`.

## 1. Container startup

Grafana listens on port **3001** and exposes the UI at <http://localhost:3001>. Default credentials are **admin / admin**; you will be asked to set a new password on first login.

The service definition lives in `docker-compose.override.yml` and mounts a persistent volume named `grafana_data`.

## 2. Dashboard JSON

Import the sample dashboard from `resources/grafana_dashboard.json`. It plots backend request metrics as described in [docs/observability.md](observability.md).

## 3. Migrating from SQLite to PostgreSQL

Grafana stores data in a local SQLite file by default. To persist dashboards in PostgreSQL reuse the existing `db` service and add the following variables to the Grafana environment:

```yaml
GF_DATABASE_TYPE: postgres
GF_DATABASE_HOST: db:5432
GF_DATABASE_NAME: grafana
GF_DATABASE_USER: ${POSTGRES_USER}
GF_DATABASE_PASSWORD: ${POSTGRES_PASSWORD}
```

Create the `grafana` database and restart the containers. Grafana will then use PostgreSQL instead of SQLite.

## 4. Cleaning volumes

Before the initial deployment, remove any old Grafana volumes with `docker compose down -v`. This avoids duplicated plugin registrations in `grafana_data`.
