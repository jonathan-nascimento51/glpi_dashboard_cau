"""DataFrame transformations shielding the app from GLPI payload quirks."""

from __future__ import annotations

from typing import List, Union

import pandas as pd

# Basic DataFrame helpers were previously located under ``glpi_dashboard.acl``.
# They are now consolidated here to avoid circular imports and ease reuse.


def to_dataframe(tickets: list[dict]) -> pd.DataFrame:
    """Return a DataFrame from a list of tickets with optimized dtypes."""
    df = pd.DataFrame(tickets)
    if df.empty:
        return pd.DataFrame(columns=["id", "status", "assigned_to", "group"]).astype(
            {
                "id": "int32",
                "status": "category",
                "assigned_to": "category",
                "group": "category",
            }
        )
    df["id"] = (
        pd.to_numeric(df.get("id", pd.Series(dtype="object")), errors="coerce")
        .fillna(0)
        .astype("int32")
    )
    df["status"] = (
        df.get("status", pd.Series(dtype="object")).fillna("").astype("category")
    )
    df["group"] = (
        df.get("group", pd.Series(dtype="object")).fillna("").astype("category")
    )
    df["assigned_to"] = (
        df.get("assigned_to", pd.Series(dtype="object")).fillna("").astype("category")
    )

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


def sanitize_status_column(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with the ``status`` column normalized to lowercase strings."""
    if "status" not in df.columns:
        return df.copy()

    sanitized = df.copy()
    sanitized["status"] = sanitized["status"].fillna("").astype(str).str.lower()
    return sanitized


TicketData = Union[List[dict], pd.DataFrame, pd.Series]

REQUIRED_FIELDS = ["id", "status", "group", "assigned_to", "date_creation"]

# Map alternate/underscore-prefixed field names returned by the GLPI API to the
# canonical column names used by the dashboard.
FIELD_ALIASES = {
    "groups_name": "group",
    "group_name": "group",
    "users_id_recipient": "assigned_to",
    "users_id_assign": "assigned_to",
    "_users_id_assign": "assigned_to",
    "_users_id_requester": "assigned_to",
    "creation_date": "date_creation",
    "date": "date_creation",
    "_status": "status",
    "_priority": "priority",
}


def _ensure_dataframe(data: TicketData) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data.copy()
    if isinstance(data, pd.Series):
        return pd.DataFrame([data.to_dict()])
    return pd.DataFrame(list(data))


def process_raw(data: TicketData) -> pd.DataFrame:
    """Normalize raw ticket data for display in the dashboard."""

    df = _ensure_dataframe(data)

    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], downcast="integer")
        except (ValueError, TypeError):
            pass

    for src, dst in FIELD_ALIASES.items():
        if src in df.columns and dst not in df.columns:
            df.rename(columns={src: dst}, inplace=True)

    idx = df.index

    df["id"] = pd.to_numeric(
        df.get("id", pd.Series([None] * len(df), index=idx)),
        errors="coerce",
        downcast="integer",
    ).fillna(0)
    df["name"] = (
        df.get("name", pd.Series([""] * len(df), index=idx)).fillna("").astype(str)
    )
    df["status"] = (
        df.get("status", pd.Series([""] * len(df), index=idx))
        .fillna("")
        .astype(str)
        .str.lower()
        .astype("category")
    )
    df["group"] = (
        df.get("group", pd.Series([""] * len(df), index=idx)).fillna("").astype(str)
    ).astype("category")
    df["date_creation"] = pd.to_datetime(
        df.get("date_creation", pd.Series([pd.NaT] * len(df), index=idx))
    )
    assigned_raw = df.get("assigned_to", pd.Series([None] * len(df), index=idx))
    numeric_assigned = pd.to_numeric(assigned_raw, errors="coerce")
    if numeric_assigned.notna().any():
        assigned_to = numeric_assigned.astype("Int64").astype(str)
    else:
        assigned_to = assigned_raw.astype(str)
    df["assigned_to"] = assigned_to.replace({"<NA>": "", "nan": ""}).fillna("")

    return df[["id", "name", "status", "assigned_to", "group", "date_creation"]].copy()


__all__ = [
    "process_raw",
    "FIELD_ALIASES",
    "REQUIRED_FIELDS",
    "to_dataframe",
    "filter_by_status",
    "aggregate_by_user",
    "sanitize_status_column",
]
