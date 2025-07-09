"""Check GLPI credentials before running the stack."""

from __future__ import annotations

import asyncio
import sys

from dotenv import load_dotenv

from backend.adapters.glpi_session import (
    Credentials,
    GLPIAPIError,
    GLPISession,
    GLPIUnauthorizedError,
)
from glpi_dashboard.config.settings import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
    USE_MOCK_DATA,
)

# Windows event loop fix for aiodns
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def _check() -> None:
    # Offline mode: skip check
    if USE_MOCK_DATA:
        print("⚠️  Modo offline ativado (USE_MOCK_DATA=True). Health check ignorado.")
        return

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
    while (
        session._session_token is not None
        and session._session_token != expected_token
        and not asyncio.get_event_loop().time() - start > timeout
    ):
        await asyncio.sleep(0.05)


def main() -> None:
    """Validate credentials and print result."""
    load_dotenv()
    try:
        asyncio.run(_check())
    except (GLPIAPIError, GLPIUnauthorizedError) as exc:  # pragma: no cover - network
        print(f"\u274c Falha na conexão: {exc}")
    except Exception as exc:  # pragma: no cover - unexpected errors
        print(f"\u274c Falha na conexão: {exc}")
    else:
        print("\u2705 Conexão com GLPI bem-sucedida!")


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
