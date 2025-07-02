# scripts/validate_credentials.py

import asyncio
import sys
from pathlib import Path

from glpi_dashboard.config.settings import get_settings
from aiohttp import ClientSession
import textwrap
import logging

# --- Add project root to path to allow imports from src ---
# This allows the script to be run from the root directory of the project
# and still find the necessary modules in `src`.
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
# -----------------------------------------------------------

# from src.glpi_dashboard.services.glpi_session import GLPISession, Credentials
# from src.glpi_dashboard.services.exceptions import GLPIAPIError


async def check_glpi_connection():
    """
    Attempts to initialize a session with the GLPI API using credentials
    from the .env file to validate them.
    """
    print("🔍 Validating GLPI API credentials...")
    settings = get_settings()
    # Print tokens for debugging
    print(f"GLPI_APP_TOKEN: {settings.GLPI_APP_TOKEN}")
    print(f"GLPI_USER_TOKEN: {settings.GLPI_USER_TOKEN}")
    print(f"GLPI_USERNAME: {settings.GLPI_USERNAME}")
    print(f"GLPI_PASSWORD: {settings.GLPI_PASSWORD}")

    # Retire espaços/nova-linhas acidentais
    app_token = (settings.GLPI_APP_TOKEN or "").strip()
    user_token = settings.GLPI_USER_TOKEN.strip() if settings.GLPI_USER_TOKEN else ""

    headers = {
        "App-Token": app_token,
        "Authorization": f"user_token {user_token}",
        "Content-Type": "application/json",
    }

    async with ClientSession() as sess:
        url = f"{settings.GLPI_BASE_URL.rstrip('/')}/initSession"
        async with sess.get(url, headers=headers) as r:
            body = await r.text()
            logging.info("Status %s – %s", r.status, textwrap.shorten(body, 120))
            print(f"Status: {r.status}")
            print(f"Response: {body}")


if __name__ == "__main__":
    # Use asyncio.run() for a clean way to execute the async function.
    # This is the standard approach for Python 3.7+.
    asyncio.run(check_glpi_connection())
