"""Check GLPI credentials before running the stack."""

from __future__ import annotations

import asyncio
from dotenv import load_dotenv

from glpi_dashboard.services.glpi_session import (
    GLPISession,
    Credentials,
    GLPIAPIError,
    GLPIUnauthorizedError,
)
from glpi_dashboard.config.settings import (
    GLPI_BASE_URL,
    GLPI_APP_TOKEN,
    GLPI_USERNAME,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
)


async def _check() -> None:
    creds = Credentials(
        app_token=GLPI_APP_TOKEN,
        user_token=GLPI_USER_TOKEN,
        username=GLPI_USERNAME,
        password=GLPI_PASSWORD,
    )
    async with GLPISession(GLPI_BASE_URL, creds) as session:
        await wait_for_token(session, "proactive_token_2")


async def wait_for_token(session, expected_token, timeout=1.0):
    start = asyncio.get_event_loop().time()
    while session._session_token != expected_token:
        if asyncio.get_event_loop().time() - start > timeout:
            break
        await asyncio.sleep(0.05)


def main() -> None:
    """Validate credentials and print result."""
    load_dotenv()
    try:
        asyncio.run(_check())
    except (GLPIAPIError, GLPIUnauthorizedError) as exc:  # pragma: no cover - network
        print(f"\u274C Falha na conex\u00e3o: {exc}")
    except Exception as exc:  # pragma: no cover - unexpected errors
        print(f"\u274C Falha na conex\u00e3o: {exc}")
    else:
        print("\u2705 Conex\u00e3o com GLPI bem-sucedida!")


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
