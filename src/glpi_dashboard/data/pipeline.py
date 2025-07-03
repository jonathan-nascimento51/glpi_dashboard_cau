"""Data processing helpers for GLPI tickets."""

from __future__ import annotations

from typing import List, Union

import pandas as pd

TicketData = Union[List[dict], pd.DataFrame, pd.Series]

REQUIRED_FIELDS = ["id", "status", "group", "assigned_to", "date_creation"]

# Map alternate/underscore-prefixed field names returned by the GLPI API
# to the canonical column names used by the dashboard. This keeps
# ``process_raw`` resilient to schema variations across GLPI versions.
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
    """Normalize raw ticket data for display in the dashboard.

    This function is resilient to missing keys and converts the main textual
    fields to human‑friendly strings. It preserves ``id`` as an integer when
    possible and always returns the same four columns expected by the front‑end.
    """

    df = _ensure_dataframe(data)

    # Attempt to reduce memory by converting numeric-like columns to the
    # smallest possible integer subtype. ``errors='ignore'`` keeps textual
    # columns untouched while still downcasting when values look like
    # integers.
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore", downcast="integer")

    # Handle legacy/alternate field names from the API
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


def save_json(df: pd.DataFrame, path: str = "mock/sample_data.json") -> None:
    """Save dataframe to JSON file."""
    df.to_json(path, orient="records", indent=2, date_format="iso")
