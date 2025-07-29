"""Endpoints providing aggregated ticket metrics.

This module exposes simple REST routes used by the dashboard frontend. The
metrics are computed from GLPI tickets using :mod:`pandas` and cached in Redis
to keep the responses fast even when the dataset is large.
"""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict, Optional, cast

import pandas as pd
from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError

from backend.application.glpi_api_client import (
    GlpiApiClient,
    create_glpi_api_client,
)
from backend.infrastructure.glpi.normalization import process_raw
from shared.utils.redis_client import RedisClient, redis_client

from . import router

# Status values that represent a closed ticket
CLOSED_STATUSES = ["closed", "solved"]

logger = logging.getLogger(__name__)

# Cache key used to store the metrics overview in Redis
CACHE_KEY_OVERVIEW = "metrics:overview"


class MetricsOverview(BaseModel):
    """Summary of key ticket metrics."""

    open_tickets: dict[str, int] = Field(default_factory=dict)
    tickets_closed_this_month: dict[str, int] = Field(default_factory=dict)
    status_distribution: dict[str, int] = Field(default_factory=dict)


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


async def get_or_set_cache(
    cache: RedisClient,
    cache_key: str,
    model: type[BaseModel],
    compute_func: Callable[[], Awaitable[BaseModel]],
    ttl_seconds: int = 300,
) -> BaseModel:
    cached = await cache.get(cache_key)
    if cached:
        try:
            return model.model_validate(cached)
        except (ValidationError, TypeError) as exc:
            logger.warning(
                "Ignoring invalid cache entry due to %s: %s",
                type(exc).__name__,
                exc,
            )
    result: BaseModel = await compute_func()
    try:
        await cache.set(cache_key, result.model_dump(), ttl_seconds=ttl_seconds)
    except Exception as exc:
        logger.warning("Failed to store metrics in cache: %s", exc)
    return result


async def compute_overview(
    client: Optional[GlpiApiClient] = None,
    cache: Optional[RedisClient] = None,
    ttl_seconds: int = 300,
) -> MetricsOverview:
    """Compute metrics and cache the result."""
    cache = cache or redis_client
    cache_key = CACHE_KEY_OVERVIEW

    async def compute_metrics():
        df = await _fetch_dataframe(client)
        df["status"] = df["status"].astype(str).str.lower()

        open_mask = ~df["status"].isin(CLOSED_STATUSES)
        open_by_level: dict[Any, int] = (
            df[open_mask].groupby("group", observed=True).size().astype(int).to_dict()
        )

        now = pd.Timestamp.utcnow().tz_localize("UTC")
        month_start = pd.Timestamp(year=now.year, month=now.month, day=1, tz="UTC")
        # Ensure all entries in 'date_resolved' are localized to UTC
        if not pd.api.types.is_datetime64_any_dtype(df["date_resolved"]):
            df["date_resolved"] = pd.to_datetime(df["date_resolved"], errors="coerce")
        if df["date_resolved"].dt.tz is None:
            df["date_resolved"] = df["date_resolved"].dt.tz_localize("UTC")
        else:
            df["date_resolved"] = df["date_resolved"].dt.tz_convert("UTC")
        closed_mask = df["status"].isin(CLOSED_STATUSES) & (
            df["date_resolved"] >= month_start
        )

        closed_this_month_by_level = (
            df[closed_mask].groupby("group", observed=True).size().astype(int).to_dict()
        )

        status_counts = df["status"].value_counts().astype(int).to_dict()

        return MetricsOverview(
            open_tickets=open_by_level,
            tickets_closed_this_month=closed_this_month_by_level,
            status_distribution=status_counts,
        )

    result = await get_or_set_cache(
        cache, cache_key, MetricsOverview, compute_metrics, ttl_seconds
    )
    # Ensure the result is a MetricsOverview instance
    if not isinstance(result, MetricsOverview):
        raise RuntimeError("Cached value is not a MetricsOverview instance")
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

    open_mask = ~level_df["status"].isin(CLOSED_STATUSES)
    open_count = int(level_df[open_mask].shape[0])

    if not pd.api.types.is_datetime64tz_dtype(level_df["date_resolved"]):
        level_df["date_resolved"] = level_df["date_resolved"].dt.tz_localize("UTC")
    else:
        level_df["date_resolved"] = level_df["date_resolved"].dt.tz_convert("UTC")
    closed_mask = level_df["status"].isin(CLOSED_STATUSES)
    resolved_count = int(level_df[closed_mask].shape[0])

    status_counts: dict[str, int] = cast(
        dict[Any, int], level_df["status"].value_counts().astype(int).to_dict()
    )

    result = LevelMetrics(
        open_tickets=open_count,
        resolved_this_month=resolved_count,
        status_distribution=status_counts,
    )

    try:
        await cache.set(cache_key, result.model_dump_json(), ttl_seconds=ttl_seconds)
    except Exception as exc:  # pragma: no cover - cache failures
        logger.warning("Failed to store level metrics in cache: %s", exc)
    return result


@router.get("/metrics/overview", response_model=MetricsOverview)
async def metrics_overview() -> MetricsOverview:
    """Return aggregated ticket metrics for the dashboard."""
    try:
        return await compute_overview()
    except Exception as exc:
        logger.exception("Error computing metrics overview")
        raise HTTPException(
            status_code=500, detail="Failed to compute metrics"
        ) from exc
