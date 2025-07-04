"""Helpers for computing and caching aggregated ticket metrics."""

from __future__ import annotations

from typing import Optional, Dict, Any

import pandas as pd

from glpi_dashboard.utils.redis_client import RedisClient, redis_client
from glpi_dashboard.data.transform import aggregate_by_user


def compute_aggregated(df: pd.DataFrame) -> Dict[str, Any]:
    """Return simple aggregated metrics from ``df``."""
    status_counts = (
        df.get("status", pd.Series(dtype="object"))
        .fillna("")
        .astype(str)
        .str.lower()
        .value_counts()
        .to_dict()
    )
    by_user = aggregate_by_user(df).set_index("assigned_to")["count"].to_dict()
    return {"status": status_counts, "per_user": by_user}


async def cache_aggregated_metrics(
    cache: Optional[RedisClient], key: str, data: Dict[str, Any]
) -> None:
    """Store aggregated metrics in cache."""
    cache = cache or redis_client
    await cache.set(key, data)


async def get_cached_aggregated(
    cache: Optional[RedisClient], key: str
) -> Optional[Dict[str, Any]]:
    """Retrieve cached metrics if available."""
    cache = cache or redis_client
    return await cache.get(key)

