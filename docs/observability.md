# Observability

The development compose file includes Prometheus and Grafana services. Prometheus scrapes metrics from the FastAPI backend at `/metrics` and the circuit breaker endpoint `/breaker`.

## FastAPI instrumentation

Tracing is enabled via OpenTelemetry. After the FastAPI app is created in
`worker_api.py` the following call instruments all routes:

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI(...)
FastAPIInstrumentor().instrument_app(app)
```

`resources/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: /metrics
  - job_name: 'circuitbreaker'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: /breaker
```

Grafana loads dashboards from JSON. An example (`resources/grafana_dashboard.json`):

```json
{
  "title": "Backend Metrics",
  "panels": [
    {"type": "graph", "title": "Request latency", "targets": [{"expr": "request_latency_seconds"}]}
  ]
}
```

When the stack is running, access Grafana at <http://localhost:3001> and import this dashboard.

## Grafana settings

The development `docker-compose.override.yml` sets several environment variables for the Grafana service:

* `GF_PLUGINS_BACKGROUNDINSTALLER_DISABLED=true` – disables automatic plugin installation during startup so builds remain deterministic.
* `GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS` – optional list of plugin IDs that bypass signature checks. Set it only when using community plugins that are not signed.
* `GF_DATABASE_SQLITE_ENABLE_WAL=true` – enables write-ahead logging for the embedded SQLite database, improving concurrency.
* A healthcheck runs `wget --spider http://localhost:3000/login` to ensure the UI is reachable.

### Migrating Grafana to PostgreSQL

Grafana defaults to SQLite for development. To persist dashboards in PostgreSQL, reuse the existing `db` service by adding these variables to the Grafana environment block:

```yaml
GF_DATABASE_TYPE: postgres
GF_DATABASE_HOST: db:5432
GF_DATABASE_NAME: grafana
GF_DATABASE_USER: ${POSTGRES_USER}
GF_DATABASE_PASSWORD: ${POSTGRES_PASSWORD}
```

Create the `grafana` database and restart the containers. Grafana will store all data in PostgreSQL instead of the local SQLite file.
