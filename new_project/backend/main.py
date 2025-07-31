"""Minimal FastAPI app relying on the shared ``glpi_session`` client."""

from __future__ import annotations

import pandas as pd
from fastapi import FastAPI

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


if __name__ == "__main__":  # pragma: no cover - manual run
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
