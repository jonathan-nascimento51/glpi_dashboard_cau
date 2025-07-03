# Observability

The development compose file includes Prometheus and Grafana services. Prometheus scrapes metrics from the FastAPI backend at `/metrics` and the circuit breaker endpoint `/breaker`.

`monitoring/prometheus.yml`:

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

Grafana loads dashboards from JSON. An example (`monitoring/grafana_dashboard.json`):

```json
{
  "title": "Backend Metrics",
  "panels": [
    {"type": "graph", "title": "Request latency", "targets": [{"expr": "request_latency_seconds"}]}
  ]
}
```

When the stack is running, access Grafana at <http://localhost:3001> and import this dashboard.
