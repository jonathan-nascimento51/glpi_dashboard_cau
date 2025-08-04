"""Endpoints providing aggregated ticket metrics.

This module exposes simple REST routes used by the dashboard frontend. The
metrics are computed from GLPI tickets using :mod:`pandas` and cached in Redis
to keep the responses fast even when the dataset is large.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, Optional

import pandas as pd
from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError

from backend.application.glpi_api_client import (
    GlpiApiClient,
    create_glpi_api_client,
    get_status_totals_by_levels,
)
from backend.constants import GROUP_IDS, GROUP_LABELS_BY_ID
from backend.infrastructure.glpi.normalization import process_raw
from shared.utils.redis_client import RedisClient, redis_client

from . import router

# Status values that represent a closed ticket
CLOSED_STATUSES = ["closed", "solved"]

logger = logging.getLogger(__name__)

# Cache key used to store the aggregated metrics in Redis
CACHE_KEY_AGGREGATED = "metrics:aggregated"


class MetricsOverview(BaseModel):
    """Summary of key ticket metrics."""

    open_tickets: dict[str, int] = Field(default_factory=dict)
    tickets_closed_this_month: dict[str, int] = Field(default_factory=dict)
    status_distribution: dict[str, int] = Field(default_factory=dict)


class LevelMetrics(BaseModel):
    """Metrics for a single support level."""

    open_tickets: int = 0
    tickets_closed_this_month: int = 0
    status_distribution: dict[str, int] = Field(default_factory=dict)


async def _fetch_dataframe(client: Optional[GlpiApiClient]) -> pd.DataFrame:
    """Return tickets as a normalized DataFrame."""
    client = client or create_glpi_api_client()
    if client is None:
        raise RuntimeError("GLPI client unavailable")

    async with client:
        tickets = await client.fetch_tickets()

    data = [t.model_dump() for t in tickets]
    df = process_raw(data)
    df["group"] = map_group_ids_to_labels(df["group"])
    return df


def map_group_ids_to_labels(series: pd.Series) -> pd.Series:
    """Map numerical group IDs to their human-readable labels."""

    return pd.to_numeric(series, errors="coerce").map(GROUP_LABELS_BY_ID).fillna(series)


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


async def compute_aggregated(
    client: Optional[GlpiApiClient] = None,
    cache: Optional[RedisClient] = None,
    ttl_seconds: int = 300,
) -> MetricsOverview:
    """Compute metrics and cache the result."""
    cache = cache or redis_client
    cache_key = CACHE_KEY_AGGREGATED

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


@router.get("/metrics/aggregated", response_model=MetricsOverview)
async def metrics_aggregated() -> MetricsOverview:
    """Return aggregated ticket metrics for the dashboard."""
    try:
        return await compute_aggregated()
    except Exception as exc:
        logger.exception("Error computing aggregated metrics")
        raise HTTPException(
            status_code=500, detail="Failed to compute metrics"
        ) from exc


async def compute_levels(
    *,
    client: Optional[GlpiApiClient] = None,
    cache: Optional[RedisClient] = None,
    ttl_seconds: int = 300,
) -> Dict[str, Dict[str, int]]:
    """Compute ticket status counts grouped by level and cache the result."""

    cache = cache or redis_client
    cache_key = "metrics:levels:all"

    cached = await cache.get(cache_key)
    if isinstance(cached, dict):
        return cached
    try:
        result: Dict[str, Dict[str, int]] = await get_status_totals_by_levels(GROUP_IDS)
    except Exception:
        logger.exception("failed to fetch status totals; falling back to DataFrame")
        df = await _fetch_dataframe(client)
        df["status"] = df["status"].astype(str).str.lower()
        grouped = (
            df.groupby(["group", "status"], observed=True)
            .size()
            .unstack(fill_value=0)
            .astype(int)
        )
        result = grouped.to_dict(orient="index")
        # Ensure all support levels are present even if missing from the data
        all_statuses = {status: 0 for status in grouped.columns}
        for level in GROUP_IDS.keys():
            result.setdefault(level, all_statuses.copy())

    try:
        await cache.set(cache_key, result, ttl_seconds=ttl_seconds)
    except Exception as exc:  # pragma: no cover - cache errors
        logger.warning("Failed to store level metrics in cache: %s", exc)

    return result


@router.get("/metrics/levels", response_model=Dict[str, Dict[str, int]])
async def metrics_levels() -> Dict[str, Dict[str, int]]:
    """Return status counts grouped by support level."""

    try:
        return await compute_levels()
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error computing metrics by level")
        raise HTTPException(
            status_code=500, detail="Failed to compute metrics"
        ) from exc


async def compute_level_metrics(
    level: str,
    *,
    client: Optional[GlpiApiClient] = None,
    cache: Optional[RedisClient] = None,
    ttl_seconds: int = 300,
) -> LevelMetrics:
    """Compute metrics for a single support level and cache the result."""

    cache = cache or redis_client
    cache_key = f"metrics:levels:{level}"

    async def compute_metrics() -> LevelMetrics:
        df = await _fetch_dataframe(client)
        df["status"] = df["status"].astype(str).str.lower()
        if "group" not in df.columns:
            raise HTTPException(
                status_code=500,
                detail="Data error: 'group' column missing from ticket data",
            )
        df = df[df["group"] == level]

        open_mask = ~df["status"].isin(CLOSED_STATUSES)
        open_count = int(open_mask.sum())

        now = pd.Timestamp.utcnow().tz_localize("UTC")
        month_start = pd.Timestamp(year=now.year, month=now.month, day=1, tz="UTC")

        if not pd.api.types.is_datetime64_any_dtype(df["date_resolved"]):
            df["date_resolved"] = pd.to_datetime(df["date_resolved"], errors="coerce")
        if df["date_resolved"].dt.tz is None:
            df["date_resolved"] = df["date_resolved"].dt.tz_localize("UTC")
        else:
            df["date_resolved"] = df["date_resolved"].dt.tz_convert("UTC")

        closed_mask = df["status"].isin(CLOSED_STATUSES) & (
            df["date_resolved"] >= month_start
        )
        closed_count = int(closed_mask.sum())

        status_counts = df["status"].value_counts().astype(int).to_dict()

        return LevelMetrics(
            open_tickets=open_count,
            tickets_closed_this_month=closed_count,
            status_distribution=status_counts,
        )

    result = await get_or_set_cache(
        cache, cache_key, LevelMetrics, compute_metrics, ttl_seconds
    )
    if not isinstance(result, LevelMetrics):
        raise RuntimeError("Cached value is not a LevelMetrics instance")
    return result


class SupportLevel(str, Enum):
    """Known support levels exposed by the API."""

    N1 = "N1"
    N2 = "N2"
    N3 = "N3"
    N4 = "N4"


@router.get("/metrics/levels/{level}", response_model=MetricsOverview)
async def metrics_level(level: SupportLevel) -> MetricsOverview:
    """Return ticket metrics for a specific support level."""

    level_value = level.value
    try:
        return await compute_level_metrics(level_value)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error computing metrics for level %s", level_value)
        raise HTTPException(
            status_code=500, detail="Failed to compute metrics"
        ) from exc
