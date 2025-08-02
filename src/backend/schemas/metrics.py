from __future__ import annotations

from pydantic import BaseModel


class MetricsSummary(BaseModel):
    """Ticket counts used for lightweight KPI cards."""

    total: int
    opened: int
    closed: int
