from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, Field


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
