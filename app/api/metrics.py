"""Endpoints providing aggregated ticket metrics.

This module exposes simple REST routes used by the dashboard frontend. The
metrics are computed from GLPI tickets using :mod:`pandas` and cached in Redis
to keep the responses fast even when the dataset is large.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

import pandas as pd
from backend.application.glpi_api_client import (
    GlpiApiClient,
    create_glpi_api_client,
)
from backend.infrastructure.glpi.normalization import process_raw
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from shared.utils.redis_client import RedisClient, redis_client

logger = logging.getLogger(__name__)
router = APIRouter()


class MetricsOverview(BaseModel):
    """Summary of key ticket metrics."""

    open_tickets: Dict[str, int] = Field(default_factory=dict)
    resolved_this_month: Dict[str, int] = Field(default_factory=dict)
    status_distribution: Dict[str, int] = Field(default_factory=dict)


class LevelMetrics(BaseModel):
    """Metrics for a specific support level."""

    open_tickets: int = 0
    resolved_this_month: int = 0
    status_distribution: Dict[str, int] = Field(default_factory=dict)


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
    cache_key = "metrics:overview"

    cached = await cache.get(cache_key)
    if cached:
        try:
            return MetricsOverview.model_validate(cached)
        except Exception as exc:  # pragma: no cover - bad cache content
            logger.warning("Ignoring invalid cache entry: %s", exc)

    df = await _fetch_dataframe(client)
    df["status"] = df["status"].astype(str).str.lower()

    open_mask = ~df["status"].isin(["closed", "solved"])
    open_by_level = (
        df[open_mask].groupby("group", observed=True).size().astype(int).to_dict()
    )

    now = pd.Timestamp.utcnow()
    month_start = pd.Timestamp(year=now.year, month=now.month, day=1)
    closed_mask = df["status"].isin(["closed", "solved"]) & (
        df["date_creation"] >= month_start
    )
    resolved_by_level = (
        df[closed_mask].groupby("group", observed=True).size().astype(int).to_dict()
    )

    status_counts = df["status"].value_counts().astype(int).to_dict()

    result = MetricsOverview(
        open_tickets=open_by_level,
        resolved_this_month=resolved_by_level,
        status_distribution=status_counts,
    )

    try:
        await cache.set(cache_key, result.model_dump(), ttl_seconds=ttl_seconds)
    except Exception as exc:  # pragma: no cover - cache failures
        logger.warning("Failed to store metrics in cache: %s", exc)

    return result


async def compute_level_metrics(
    level: str,
    client: Optional[GlpiApiClient] = None,
    cache: Optional[RedisClient] = None,
    ttl_seconds: int = 300,
) -> LevelMetrics:
    """Compute metrics for a single support level and cache the result."""
    cache = cache or redis_client
    cache_key = f"metrics:level:{level}"

    cached = await cache.get(cache_key)
    if cached:
        try:
            return LevelMetrics.model_validate(cached)
        except Exception as exc:  # pragma: no cover - bad cache content
            logger.warning("Ignoring invalid cache entry for %s: %s", level, exc)

    df = await _fetch_dataframe(client)
    df["status"] = df["status"].astype(str).str.lower()
    level_df = df[df["group"] == level]

    open_mask = ~level_df["status"].isin(["closed", "solved"])
    open_count = int(level_df[open_mask].shape[0])

    now = pd.Timestamp.utcnow()
    month_start = pd.Timestamp(year=now.year, month=now.month, day=1)
    closed_mask = level_df["status"].isin(["closed", "solved"]) & (
        level_df["date_creation"] >= month_start
    )
    resolved_count = int(level_df[closed_mask].shape[0])

    status_counts = level_df["status"].value_counts().astype(int).to_dict()

    result = LevelMetrics(
        open_tickets=open_count,
        resolved_this_month=resolved_count,
        status_distribution=status_counts,
    )

    try:
        await cache.set(cache_key, result.model_dump(), ttl_seconds=ttl_seconds)
    except Exception as exc:  # pragma: no cover - cache failures
        logger.warning("Failed to store level metrics in cache: %s", exc)

    return result


@router.get("/metrics/overview", response_model=MetricsOverview)
async def metrics_overview() -> MetricsOverview:
    """Return aggregated ticket metrics for the dashboard."""
    try:
        return await compute_overview()
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error computing metrics overview: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to compute metrics")


@router.get("/metrics/level/{level}", response_model=LevelMetrics)
async def metrics_level(level: str) -> LevelMetrics:
    """Return metrics for a single support level (e.g. N1, N2)."""
    try:
        normalized = level.upper()
        return await compute_level_metrics(normalized)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error computing level metrics for %s: %s", level, exc)
        raise HTTPException(status_code=500, detail="Failed to compute metrics")
