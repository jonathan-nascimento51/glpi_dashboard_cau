from __future__ import annotations

from pydantic import BaseModel, Field


class ChamadoPorData(BaseModel):
    """Aggregated tickets per creation date."""

    date: str = Field(..., examples=["2024-06-01"])
    total: int = Field(..., examples=[5])


class ChamadosPorDia(BaseModel):
    """Daily ticket totals used for heatmaps."""

    date: str = Field(..., examples=["2024-06-01"])
    total: int = Field(..., examples=[5])


class TicketSummaryOut(BaseModel):
    """Row from the materialized view used as read model."""

    ticket_id: int
    status: str
    priority: str
    group_name: str
    opened_at: str
