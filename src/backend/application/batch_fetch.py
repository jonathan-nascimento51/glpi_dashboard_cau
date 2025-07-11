"""Utilities for fetching multiple tickets concurrently."""

from __future__ import annotations

import asyncio
import json
from typing import List

from pydantic import BaseModel, Field

from backend.core.settings import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
)

# Import custom error raised by the GLPI client
from backend.domain.exceptions import GLPIAPIError
from backend.domain.tool_error import ToolError
from backend.infrastructure.glpi.glpi_session import Credentials, GLPISession


class BatchFetchParams(BaseModel):
    """Input IDs for :func:`fetch_all_tickets`."""

    ids: List[int] = Field(..., description="Ticket IDs to fetch")


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


async def fetch_all_tickets_tool(params: BatchFetchParams) -> str:
    """Return JSON data for multiple tickets or an error message.

    This tool wraps :func:`fetch_all_tickets` for use in agent pipelines where
    results must be serialized. It returns a JSON list on success. When an
    exception occurs it yields ``{"error": {"message": str, "details": str}}``.
    """

    try:
        data = await fetch_all_tickets(params.ids)
        return json.dumps(data)
    except Exception as exc:  # pragma: no cover - tool usage
        err = ToolError("failed to fetch tickets", str(exc))
        return json.dumps({"error": err.dict()})


__all__ = ["fetch_all_tickets", "BatchFetchParams", "fetch_all_tickets_tool"]
