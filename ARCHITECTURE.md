# Project Architecture

This short guide explains how the repository is organised and how the main services interact with GLPI.

## Directory Overview

- **`docker/backend/`** – Dockerfile and config for running the FastAPI worker.
- **`src/backend/`** – actual worker implementation exposing REST and GraphQL endpoints. Integration with GLPI lives under `adapters/` and service logic under `services/`.
- **`src/frontend/`** – Dash components and callbacks that render metrics. `layout/layout.py` defines the main dashboard view.
- **`frontend/`** – Next.js project for a richer React front‑end. It consumes the worker API using `NEXT_PUBLIC_API_BASE_URL`.
- **`src/shared/`** – utilities reused across back‑end modules (DTOs, resilience helpers).
- **`scripts/`** – helper tools for setup, data fetch and validation.

## Data Flow

1. `glpi_session.py` opens an async session with the GLPI REST API.
2. `ticket_loader.py` and `metrics_worker.py` normalize responses and store them in Redis/PostgreSQL.
3. The worker (`src/backend/api/worker_api.py`) exposes `/tickets`, `/metrics` and `/metrics/aggregated` endpoints.
4. Dash components or the React app request these endpoints to display tables and charts.

```
+-------+      +-------------+      +-----------+
| GLPI  +----->+  Worker API +----->+  Redis    |
+-------+      +-------------+      +-----------+
                     |                    
                     v                    
                 +-----------+
                 | PostgreSQL|
                 +-----------+
                     |
       +-------------------------------+
       | Dash (src/frontend) / React   |
       +-------------------------------+
```

Aggregated metrics are computed in `src/backend/services/aggregated_metrics.py` and kept in Redis so both UIs load quickly.

## GLPI Integration & Metrics

The GLPI credentials and base URL are read from `.env` variables. When `metrics_worker.py` runs, it updates cached counts like total tickets and daily totals. Dash visualisations live under `src/frontend/` while the separate React dashboard resides in `frontend/`.
