"""Helpers for computing and caching aggregated ticket metrics."""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd

from backend.adapters.normalization import aggregate_by_user
from shared.utils.redis_client import RedisClient, redis_client


def tickets_by_date(df: pd.DataFrame) -> pd.DataFrame:
    """Return ticket counts grouped by ``date_creation``."""
    if "date_creation" not in df.columns:
        return pd.DataFrame(columns=["date", "total"])

    counts = (
        df["date_creation"].dropna().dt.strftime("%Y-%m-%d").value_counts().sort_index()
    )
    return counts.rename_axis("date").reset_index(name="total")


def tickets_daily_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Return daily ticket totals for the heatmap."""
    return tickets_by_date(df)


def compute_aggregated(df: pd.DataFrame) -> Dict[str, Any]:
    """Return simple aggregated metrics from ``df``."""
    raw_status = df.get("status")
    status_series = (
        pd.Series(raw_status, dtype="object").fillna("").astype(str).str.lower()
    )
    status_series = status_series.replace({"solved": "closed"})
    status_counts = status_series.value_counts().to_dict()
    by_user = aggregate_by_user(df).set_index("assigned_to")["count"].to_dict()
    return {"status": status_counts, "per_user": by_user}


def status_by_group(df: pd.DataFrame) -> Dict[str, Dict[str, int]]:
    """Return counts of ``new``, ``pending`` and ``solved`` tickets per group.

    Parameters
    ----------
    df:
        Input DataFrame with at least ``status`` and ``group`` columns.

    Returns
    -------
    dict
        Mapping of group name to a dict of status counts.
    """

    if not {"status", "group"}.issubset(df.columns):
        return {}

    tmp = df[["group", "status"]].copy()
    tmp["status"] = tmp["status"].fillna("").astype(str).str.lower()
    tmp = tmp[tmp["status"].isin(["new", "pending", "solved"])]

    grouped = (
        tmp.groupby(["group", "status"], observed=True).size().unstack(fill_value=0)
    )

    for col in ["new", "pending", "solved"]:
        if col not in grouped.columns:
            grouped[col] = 0

    grouped = grouped[["new", "pending", "solved"]]
    grouped = grouped.astype(int)
    return grouped.to_dict(orient="index")


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
