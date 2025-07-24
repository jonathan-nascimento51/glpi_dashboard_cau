"""Utilities for fetching multiple tickets concurrently."""

from __future__ import annotations

import json
from typing import List

from pydantic import BaseModel, Field

from backend.application.glpi_api_client import GlpiApiClient
from backend.core.settings import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
)

# Import custom error raised by the GLPI client
from backend.domain.tool_error import ToolError
from backend.infrastructure.glpi.glpi_session import Credentials, GLPISession


class BatchFetchParams(BaseModel):
    """Input IDs for :func:`fetch_all_tickets`."""

    ids: List[int] = Field(..., description="Ticket IDs to fetch")


async def fetch_all_tickets(ids: List[int]) -> List[dict]:
    """Return raw ticket dictionaries for the provided ``ids``."""

    creds = Credentials(
        app_token=GLPI_APP_TOKEN,
        user_token=GLPI_USER_TOKEN,
        username=GLPI_USERNAME,
        password=GLPI_PASSWORD,
    )

    session = GLPISession(GLPI_BASE_URL, creds)
    client = GlpiApiClient(session=session)
    async with client:
        tickets = await client.fetch_tickets_by_ids(ids)
    # Preserve field aliases (e.g., `name`, `date_creation`) for frontend compatibility
    return [t.model_dump(by_alias=True) for t in tickets]


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
