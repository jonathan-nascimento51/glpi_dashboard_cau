# GLPI Session Setup

## Context
The project interacts with the GLPI service desk via its REST API. Authentication is handled through a reusable session object so subsequent calls share headers and cookies.

## Decision
Provide a `glpi_session.py` module that creates a `requests.Session` after reading `GLPI_URL`, `GLPI_APP_TOKEN` and `GLPI_USER_TOKEN` from environment variables. Helper functions wrap common API endpoints.

## Consequences
API requests are centralized with consistent error handling and timeouts. If the credentials change, only this module needs to be updated.

## Steps
1. Call `login()` to create the authenticated session.
2. Use `get_tickets(status=None, limit=100)` to fetch ticket records.
3. Handle HTTP errors with `raise_for_status()` so failures surface quickly.
4. Close the session when the worker shuts down to free resources.
