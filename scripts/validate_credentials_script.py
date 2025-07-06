# scripts/validate_credentials_script.py

import asyncio
import logging
import textwrap

from aiohttp import ClientSession

from glpi_dashboard.config.settings import get_settings


async def check_glpi_connection():
    """
    Attempts to initialize a session with the GLPI API using credentials
    from the .env file to validate them.
    """
    print("🔍 Validating GLPI API credentials...")
    settings = get_settings()
    # Tokens are used only to attempt a login; avoid printing them to stdout

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
