# GLPI Session Setup

## Context
The `glpi_session` module authenticates with the GLPI REST API and provides a
simple client used across the worker and dashboard apps. It wraps `requests`
with sensible defaults so other modules only deal with high level helpers.

## Decision
Manage authentication tokens via environment variables (`GLPI_URL`,
`GLPI_APP_TOKEN`, `GLPI_USER_TOKEN`). The session reuses a single `requests`
`Session` with a 30‑second timeout and built‑in retry logic. Token refresh is
handled automatically when the API responds with an authentication error.

## Consequences
Centralizing the connection ensures all services share the same caching and
error handling policy. Failures propagate quickly if credentials are missing or
invalid, making troubleshooting straightforward during deployment.

## Steps
1. Export the required variables in your shell or `.env` file before running any
   component. Using `python-dotenv` helps load them during development.
2. Call `glpi_session.login()` once at startup to obtain the session cookies; if
   the call fails due to expired tokens, refresh the environment variables and
   retry.
3. Use `glpi_session.get_tickets()` or related helpers throughout the pipeline
   to fetch data.
