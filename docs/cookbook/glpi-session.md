# GLPI Session Setup

## Context
The `glpi_session` module authenticates with the GLPI REST API and exposes
``GLPISession``—an **asynchronous** client built on ``aiohttp``. This client is
used by the worker services and ETL routines. A deprecated synchronous wrapper,
``GLPISessionManager`` (``glpi_client.py``), is still available for legacy
scripts but should be avoided for new development.

## Decision
Credentials are read from the environment via ``GLPI_BASE_URL`` and
``GLPI_APP_TOKEN`` plus either ``GLPI_USER_TOKEN`` or ``GLPI_USERNAME`` /``GLPI_PASSWORD``.
``GLPISession`` manages token refresh automatically and maintains a single
``aiohttp.ClientSession`` with retry and circuit breaking provided by
``shared.utils.resilience``.

## Consequences
Centralizing the connection ensures all services share the same caching and
error handling policy. Failures propagate quickly if credentials are missing or
invalid, making troubleshooting straightforward during deployment.

## Usage
1. Export the required variables in your shell or ``.env`` file before running
   any component.
2. Create a ``GLPISession`` using ``async with`` to ensure proper cleanup:

   ```python
   from backend.infrastructure.glpi.glpi_session import Credentials, GLPISession

   creds = Credentials(app_token="APP", user_token="USER")
   async with GLPISession("https://glpi/api", creds) as session:
       ticket = await session.get("Ticket/1")
   ```

3. The old ``GLPISessionManager`` class mirrors the same API but is synchronous
   and relies on ``requests``. It is retained only for simple scripts or tests
   that cannot use ``asyncio``.
