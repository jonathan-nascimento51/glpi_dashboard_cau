"""Database access for the ticket summary read model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List

from sqlalchemy import text

from backend.infrastructure.database.database import (
    AsyncSessionLocal,
    refresh_materialized_view,
)


@dataclass
class TicketSummary:
    ticket_id: int
    status: str
    priority: str
    group_name: str
    opened_at: date


async def get_ticket_summary(limit: int = 100, offset: int = 0) -> List[TicketSummary]:
    """Return rows from ``mv_ticket_summary`` ordered by ``ticket_id``."""
    query = text(
        "SELECT ticket_id, status, priority, group_name, opened_at "
        "FROM mv_ticket_summary ORDER BY ticket_id LIMIT :limit OFFSET :offset"
    )
    async with AsyncSessionLocal() as session:
        result = await session.execute(query, {"limit": limit, "offset": offset})
        rows = result.mappings().all()
    return [TicketSummary(**row) for row in rows]


async def refresh_read_model() -> float:
    """Refresh the materialized view used as read model."""
    return await refresh_materialized_view()
