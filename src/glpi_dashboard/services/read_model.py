"""Query helpers for the read model."""

from typing import List

from glpi_dashboard.read_model import TicketSummary, get_ticket_summary


async def query_ticket_summary(
    limit: int = 100, offset: int = 0
) -> List[TicketSummary]:
    """Return ticket summaries from the read model."""
    return await get_ticket_summary(limit=limit, offset=offset)
