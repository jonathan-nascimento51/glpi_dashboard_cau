"""Minimal FastAPI app relying on the shared ``glpi_session`` client."""

from __future__ import annotations

import pandas as pd
from fastapi import FastAPI

from .glpi_session import Credentials, GLPISession

# Import shared metric helpers from the main API module
from .metrics import (
    LevelMetrics,
    MetricsOverview,
    compute_level_metrics,
    compute_overview,
)
from .normalization import process_raw
from .settings import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
)

app = FastAPI()


@app.get("/health")
async def health() -> dict[str, str]:
    """Simple health check used for smoke tests."""

    return {"status": "ok"}


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
    return {"total": total, "opened": int(opened), "closed": int(closed)}


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
    """Return aggregated ticket metrics using shared helpers."""
    async with create_session() as session:
        records = await session.get_all_paginated("Ticket")
    df = process_raw(records)
    return compute_overview(df)


@app.get("/metrics/level/{level}", response_model=LevelMetrics)
async def metrics_level(level: str) -> LevelMetrics:
    """Return metrics for a specific support level using shared helpers."""
    normalized = level.upper()
    async with create_session() as session:
        records = await session.get_all_paginated("Ticket")
    df = process_raw(records)
    return compute_level_metrics(df, normalized)


if __name__ == "__main__":  # pragma: no cover - manual run
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
