# GLPI Session Setup

## Context
The `glpi_session` module authenticates with the GLPI REST API and provides a
simple client used across the worker and dashboard apps.

## Decision
Manage authentication tokens via environment variables (`GLPI_URL`,
`GLPI_APP_TOKEN`, `GLPI_USER_TOKEN`). The session reuses a single `requests`
`Session` with a 30‑second timeout and built‑in retry logic.

## Consequences
Centralizing the connection ensures all services share the same caching and
error handling policy. Failures propagate quickly if credentials are missing or
invalid.

## Steps
1. Export the required variables in your shell or `.env` file before running any
   component.
2. Call `glpi_session.login()` once at startup to obtain the session cookies.
3. Use `glpi_session.get_tickets()` or related helpers throughout the pipeline
   to fetch data.
