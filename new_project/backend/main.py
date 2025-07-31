"""Minimal FastAPI app relying on the shared ``glpi_session`` client."""

from __future__ import annotations

import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

from backend.core.settings import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
)
from backend.infrastructure.glpi.glpi_session import Credentials, GLPISession
from backend.infrastructure.glpi.normalization import process_raw

app = FastAPI()


def create_session() -> GLPISession:
    """Instantiate ``GLPISession`` using settings from ``backend.core``."""

    creds = Credentials(
        app_token=GLPI_APP_TOKEN,
        user_token=GLPI_USER_TOKEN,
        username=GLPI_USERNAME,
        password=GLPI_PASSWORD,
    )
    return GLPISession(GLPI_BASE_URL, creds)


def calculate_metrics(df: pd.DataFrame) -> dict[str, int]:
    """Return a simple ticket status summary."""

    total = len(df)
    closed = 0
    if "status" in df.columns:
        closed = df["status"].astype(str).str.lower().isin(["closed", "solved"]).sum()
    opened = total - int(closed)
    return {"total": int(total), "opened": int(opened), "closed": int(closed)}


class MetricsOverview(BaseModel):
    """Summary of key ticket metrics."""

    open_tickets: dict[str, int] = Field(default_factory=dict)
    tickets_closed_this_month: dict[str, int] = Field(default_factory=dict)
    status_distribution: dict[str, int] = Field(default_factory=dict)


class LevelMetrics(BaseModel):
    """Metrics for a specific support level."""

    open_tickets: int = 0
    resolved_this_month: int = 0
    status_distribution: dict[str, int] = Field(default_factory=dict)


def compute_overview(df: pd.DataFrame) -> MetricsOverview:
    """Return metrics grouped by support level."""

    df["status"] = df.get("status", pd.Series(dtype=str)).astype(str).str.lower()
    open_mask = ~df["status"].isin(["closed", "solved"])
    open_by_level = (
        df[open_mask].groupby("group", observed=True).size().astype(int).to_dict()
    )

    closed_mask = df["status"].isin(["closed", "solved"])
    closed_by_level = (
        df[closed_mask].groupby("group", observed=True).size().astype(int).to_dict()
    )
    status_counts = df["status"].value_counts().astype(int).to_dict()

    return MetricsOverview(
        open_tickets=open_by_level,
        tickets_closed_this_month=closed_by_level,
        status_distribution=status_counts,
    )


def compute_level_metrics(df: pd.DataFrame, level: str) -> LevelMetrics:
    """Return metrics for a single support level."""

    df["status"] = df.get("status", pd.Series(dtype=str)).astype(str).str.lower()
    level_df = df[df.get("group", pd.Series(dtype=str)) == level]

    open_mask = ~level_df["status"].isin(["closed", "solved"])
    open_count = int(level_df[open_mask].shape[0])

    closed_mask = level_df["status"].isin(["closed", "solved"])
    resolved_count = int(level_df[closed_mask].shape[0])

    status_counts = level_df["status"].value_counts().astype(int).to_dict()

    return LevelMetrics(
        open_tickets=open_count,
        resolved_this_month=resolved_count,
        status_distribution=status_counts,
    )


@app.get("/tickets")
async def list_tickets() -> list[dict[str, object]]:
    """Fetch tickets from GLPI and return normalized JSON records."""

    async with create_session() as session:
        records = await session.get_all_paginated("Ticket")
    df = process_raw(records)
    return df.to_dict(orient="records")


@app.get("/metrics")
async def metrics() -> dict[str, int]:
    """Return a minimal ticket summary (total/opened/closed)."""

    async with create_session() as session:
        records = await session.get_all_paginated("Ticket")
    df = process_raw(records)
    return calculate_metrics(df)


@app.get("/metrics/overview", response_model=MetricsOverview)
async def metrics_overview() -> MetricsOverview:
    """Return aggregated ticket metrics."""

    async with create_session() as session:
        records = await session.get_all_paginated("Ticket")
    df = process_raw(records)
    return compute_overview(df)


@app.get("/metrics/level/{level}", response_model=LevelMetrics)
async def metrics_level(level: str) -> LevelMetrics:
    """Return metrics for a specific support level."""

    async with create_session() as session:
        records = await session.get_all_paginated("Ticket")
    df = process_raw(records)
    normalized = level.upper()
    return compute_level_metrics(df, normalized)


if __name__ == "__main__":  # pragma: no cover - manual run
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
