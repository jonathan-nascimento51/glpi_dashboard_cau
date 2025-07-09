"""Utility transformations for ticket data."""

from __future__ import annotations

import pandas as pd

__all__ = ["to_dataframe", "filter_by_status", "aggregate_by_user"]


def to_dataframe(tickets: list[dict]) -> pd.DataFrame:
    """Return a DataFrame from a list of tickets with optimized dtypes."""
    df = pd.DataFrame(tickets)
    if df.empty:
        return pd.DataFrame(
            columns=["id", "status", "assigned_to", "group"]
        ).astype(
            {
                "id": "int32",
                "status": "category",
                "assigned_to": "category",
                "group": "category",
            }
        )
    df["id"] = pd.to_numeric(df.get("id", pd.Series(dtype='object')), errors="coerce").fillna(0).astype("int32")
    df["status"] = df.get("status", pd.Series(dtype="object")).fillna("").astype("category")
    df["group"] = df.get("group", pd.Series(dtype="object")).fillna("").astype("category")
    df["assigned_to"] = df.get("assigned_to", pd.Series(dtype="object")).fillna("").astype("category")

    return df[["id", "status", "assigned_to", "group"]].copy()


def filter_by_status(df: pd.DataFrame, status: str) -> pd.DataFrame:
    """Return rows matching ``status``."""
    if "status" not in df.columns:
        return df.iloc[:0].copy()
    return df[df["status"] == status].copy()


def aggregate_by_user(df: pd.DataFrame) -> pd.DataFrame:
    """Count tickets per ``assigned_to`` user."""
    if "assigned_to" not in df.columns:
        return pd.DataFrame(columns=["assigned_to", "count"])
    counts = df.groupby("assigned_to", observed=True).size()
    return counts.reset_index(name="count")
