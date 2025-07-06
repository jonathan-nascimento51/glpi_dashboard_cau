# ADR-0005: Observability

Date: 2024-07-06

## Status

Proposed

## Context

Running multiple services requires insight into request rates, errors and
resource usage.  The development compose file already bundles Prometheus and
Grafana but observability decisions were not yet captured in an ADR.

## Decision

Expose Prometheus metrics from the FastAPI worker at `/metrics` and circuit
breaker stats at `/breaker`.  Ship default Grafana dashboards and logging in
structured JSON.  These tools run as optional containers in Docker Compose and
are enabled in staging and production environments.

## Consequences

* Facilitates early detection of performance regressions and API failures.
* Adds overhead to maintain dashboards and extra containers during deployment.

## Steps
