from __future__ import annotations

"""Utilities for fetching multiple tickets concurrently."""

import asyncio
from typing import List

from glpi_dashboard.config.settings import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
)
from .glpi_session import GLPISession, Credentials
from .exceptions import GLPIAPIError


async def fetch_all_tickets(ids: List[int]) -> List[dict]:
    """Fetch multiple tickets concurrently with limited concurrency.

    Retries on server errors (HTTP status >=500) using exponential backoff.
    """

    creds = Credentials(
        app_token=GLPI_APP_TOKEN,
        user_token=GLPI_USER_TOKEN,
        username=GLPI_USERNAME,
        password=GLPI_PASSWORD,
    )

    semaphore = asyncio.Semaphore(10)

    async with GLPISession(GLPI_BASE_URL, creds) as session:

        async def fetch(ticket_id: int) -> dict:
            backoff = 0.1
            retries = 0
            while True:
                async with semaphore:
                    try:
                        data = await session.get(f"Ticket/{ticket_id}")
                        return data.get("data", data)
                    except GLPIAPIError as exc:
                        if exc.status_code >= 500 and retries < 5:
                            await asyncio.sleep(backoff)
                            backoff *= 2
                            retries += 1
                            continue
                        raise

        results = await asyncio.gather(*(fetch(tid) for tid in ids))
        return list(results)


__all__ = ["fetch_all_tickets"]
