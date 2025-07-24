"""Endpoints providing aggregated ticket metrics."""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd
from backend.application.glpi_api_client import (
    GlpiApiClient,
    create_glpi_api_client,
)
from backend.infrastructure.glpi.normalization import process_raw
from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError
from shared.utils.redis_client import RedisClient, redis_client

from . import router

logger = logging.getLogger(__name__)

# Cache key used to store the metrics overview in Redis
CACHE_KEY_OVERVIEW = "metrics:overview"


class MetricsOverview(BaseModel):
    """Summary of key ticket metrics."""

    open_tickets: dict[str, int] = Field(default_factory=dict)
    created_and_resolved_this_month: dict[str, int] = Field(default_factory=dict)
    status_distribution: dict[str, int] = Field(default_factory=dict)


async def _fetch_dataframe(client: Optional[GlpiApiClient]) -> pd.DataFrame:
    """Return tickets as a normalized DataFrame."""
    client = client or create_glpi_api_client()
    if client is None:
        raise RuntimeError("GLPI client unavailable")

    async with client:
        tickets = await client.fetch_tickets()

    data = [t.model_dump() for t in tickets]
    return process_raw(data)


async def compute_overview(
    client: Optional[GlpiApiClient] = None,
    cache: Optional[RedisClient] = None,
    ttl_seconds: int = 300,
) -> MetricsOverview:
    """Compute metrics and cache the result."""
    cache = cache or redis_client
    cache_key = CACHE_KEY_OVERVIEW

    cached = await cache.get(cache_key)
    if cached:
        try:
            return MetricsOverview.model_validate(cached)
        except (
            ValidationError,
            TypeError,
        ) as exc:  # pragma: no cover - bad cache content
            logger.warning("Ignoring invalid cache entry: %s", exc)

    df = await _fetch_dataframe(client)
    df["status"] = df["status"].astype(str).str.lower()

    open_mask = ~df["status"].isin(["closed", "solved"])
    open_by_level = (
        df[open_mask].groupby("group", observed=True).size().astype(int).to_dict()
    )

    now = pd.Timestamp.utcnow().tz_localize("UTC")
    month_start = pd.Timestamp(year=now.year, month=now.month, day=1, tz="UTC")
    if df["date_creation"].dt.tz is None:
        df["date_creation"] = df["date_creation"].dt.tz_localize("UTC")
    else:
        df["date_creation"] = df["date_creation"].dt.tz_convert("UTC")
    closed_mask = df["status"].isin(["closed", "solved"]) & (
        df["date_creation"] >= month_start
    )
    created_and_resolved_by_level = (
        df[closed_mask].groupby("group", observed=True).size().astype(int).to_dict()
    )

    status_counts = df["status"].value_counts().astype(int).to_dict()

    result = MetricsOverview(
        open_tickets=open_by_level,
        created_and_resolved_this_month=created_and_resolved_by_level,
        status_distribution=status_counts,
    )

    try:
        await cache.set(cache_key, result.model_dump(), ttl_seconds=ttl_seconds)
    except Exception as exc:  # pragma: no cover - cache failures
        logger.warning("Failed to store metrics in cache: %s", exc)

    return result


@router.get("/metrics/overview", response_model=MetricsOverview)
async def metrics_overview() -> MetricsOverview:
    """Return aggregated ticket metrics for the dashboard."""
    try:
        return await compute_overview()
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error computing metrics overview")
        raise HTTPException(
            status_code=500, detail="Failed to compute metrics"
        ) from exc
