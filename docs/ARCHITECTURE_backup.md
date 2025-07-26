# Project Architecture

This document provides a quick overview of how the repository is structured, the main dependencies and how data flows between the components.

## Main Directories

- **`src/backend/`** – FastAPI worker that talks to the GLPI API and exposes REST/GraphQL endpoints.
- **`src/frontend/`** – Dash application composed of callbacks and layout files.
- **`src/frontend/react_app/`** – Stand‑alone Vite + React dashboard that consumes the worker API.
- **`src/shared/`** – Shared models and utilities reused by both back‑end and front‑end modules.
- **`scripts/`** – Helper scripts organised into `setup/`, `fetch/` and `etl/` subfolders.
- **`examples/`** – Reference code and prototypes only.

## Data Flow

1. `glpi_session.py` authenticates against the GLPI REST API.
2. Background workers normalise the responses into `pandas.DataFrame` objects and store them in Redis/PostgreSQL.
3. The FastAPI layer (`src/backend/api/worker_api.py`) exposes `/tickets` and `/metrics` endpoints that read from this cache. The `/tickets` response now includes the `priority` label and the requester name.
4. Dash components or the React front‑end request these endpoints to render tables and charts.

```text
+--------+     +-------------+     +-----------+
|  GLPI  +---->+  Worker API  +---->+  Redis    |
+--------+     +-------------+     +-----------+
                       |
                       v
                   +-----------+
                   | PostgreSQL|
                   +-----------+
                       |
       +------------------------------+
       | Dash (src/frontend) / React  |
       +------------------------------+
```

Aggregated metrics are computed under `src/backend/application/aggregated_metrics.py` and cached in Redis so both UIs load quickly.

## Dependencies

- **Backend**: FastAPI, httpx, pandas, SQLAlchemy, Redis, PostgreSQL.
- **Frontend**: Dash for the Python UI and a Vite + React application with Tailwind for the web dashboard.

## GLPI Integration and Metrics

The worker reads `GLPI_BASE_URL`, `GLPI_APP_TOKEN` and `GLPI_USER_TOKEN` from the `.env` file to authenticate with GLPI. Normalised ticket data is stored in Redis/PostgreSQL. Dash visualisations live in `src/frontend/`, while additional widgets and analytics for managers reside in the React app inside `src/frontend/react_app/`.
