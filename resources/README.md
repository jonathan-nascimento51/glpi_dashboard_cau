# Resources

This directory contains sample data and configuration files used by the
application during development or when the GLPI API is unavailable.

- `mock_tickets.json` – small synthetic dataset used as offline fallback when
  `USE_MOCK_DATA=true`.
- `grafana_dashboard.json` – example Grafana dashboard that visualizes backend
  metrics.
- `prometheus.yml` – default Prometheus scrape configuration for the backend
  services.
