"""Ticket-related API routes.

This router exposes endpoints for summarising ticket information. The
primary endpoint implemented here aggregates ticket counts by status
for each configured support level (N1–N4). See
``backend.services.glpi.get_ticket_summary_by_group`` for details on
how the data is gathered.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.services.glpi import get_ticket_summary_by_group
from backend.models.ts_models import TicketsSummaryPerLevel

router = APIRouter()


@router.get("/api/tickets/summary-per-level", response_model=TicketsSummaryPerLevel)
def tickets_summary_per_level() -> TicketsSummaryPerLevel:
    """Return a summary of tickets grouped by status per service level.

    The returned object has a top-level key for each level (e.g. ``"N1"``),
    whose value is another dictionary mapping ticket statuses to counts.
    In case of any internal failure this endpoint raises an HTTP 500.
    """
    try:
        return get_ticket_summary_by_group()
    except Exception as exc:
        # Convert unexpected errors into a generic 500 response so the
        # underlying exception details are not leaked to the client.
        raise HTTPException(
            status_code=500,
            detail="Failed to compute ticket summary. See server logs for details.",
        ) from exc
