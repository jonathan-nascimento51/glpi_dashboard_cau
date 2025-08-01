from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class BatchFetchParams(BaseModel):
    """Input IDs for batch ticket fetching."""

    ids: List[int] = Field(..., description="Ticket IDs to fetch")
