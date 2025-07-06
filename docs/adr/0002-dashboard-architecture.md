# ADR-0002: Dashboard Architecture

Date: 2024-07-04

## Status

Proposed

## Context

The first iteration of the dashboard mixed data ingestion and UI logic in a
single service.  As the scope grew—adding offline mode, GraphQL endpoints and
background updates—it became clear that the project needed a clearer separation
between data processing and presentation.  The architecture document proposes a
dedicated FastAPI worker for GLPI integration and a Dash/Next.js front-end for
visualization.

## Decision

Adopt a two-service architecture composed of:

1. **Worker API** built with FastAPI.  It fetches tickets from the GLPI REST API,
   stores them in PostgreSQL and Redis and exposes REST/GraphQL routes.
2. **Dash front‑end** responsible for charts and tables.  It reads data from the
   worker via HTTP.

Docker Compose orchestrates both services alongside Redis and the database.

## Consequences

* Clear separation of concerns simplifies maintenance and testing.
* Each service can scale independently or even be deployed separately.
* Deployment becomes more complex since multiple containers must be managed and
  networked correctly.

## Steps
