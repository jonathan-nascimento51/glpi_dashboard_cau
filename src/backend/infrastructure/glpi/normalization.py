"""DataFrame transformations shielding the app from GLPI payload quirks."""

from __future__ import annotations

import contextlib
from typing import List, Union

import pandas as pd

# Basic DataFrame helpers were previously located under ``glpi_dashboard.acl``.
# They are now consolidated under ``backend.adapters.normalization`` to avoid
# circular imports and ease reuse.


TicketData = Union[List[dict[str, object]], pd.DataFrame, pd.Series]

REQUIRED_FIELDS = [
    "id",
    "status",
    "group",
    "assigned_to",
    "requester",
    "date_creation",
    "priority",
]

# Map alternate/underscore-prefixed field names returned by the GLPI API to the
# canonical column names used by the dashboard.
FIELD_ALIASES = {
    "groups_name": "group",
    "group_name": "group",
    "users_id_recipient": "assigned_to",
    "users_id_assign": "assigned_to",
    "_users_id_assign": "assigned_to",
    "_users_id_requester": "requester",
    "creation_date": "date_creation",
    "date": "date_creation",
    "_status": "status",
    "_priority": "priority",
}


def _ensure_dataframe(data: TicketData) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data.copy()
    if isinstance(data, pd.Series):
        return pd.DataFrame([data.to_dict()])  # type: ignore
    return pd.DataFrame(list(data))


def process_raw(data: TicketData) -> pd.DataFrame:
    """Normalize raw ticket data for display in the dashboard."""

    df = _ensure_dataframe(data)

    for col in df.columns:
        with contextlib.suppress(ValueError, TypeError):
            df[col] = pd.to_numeric(df[col], downcast="integer")  # type: ignore
    for src, dst in FIELD_ALIASES.items():
        if src in df.columns and dst not in df.columns:
            df.rename(columns={src: dst}, inplace=True)

    idx = df.index

    df["id"] = (
        pd.to_numeric(
            df.get("id", pd.Series([None] * len(df), index=idx)),
            errors="coerce",
            downcast="integer",
        )
        .fillna(0)
        .astype("Int64")
    )  # type: ignore

    df["name"] = (
        df.get("name", pd.Series([""] * len(df), index=idx))
        .fillna("")  # type: ignore
        .astype(str)
    )

    df["status"] = (
        df.get("status", pd.Series([""] * len(df), index=idx))
        .fillna("")  # type: ignore
        .astype(str)
        .str.lower()
        .astype("category")
    )
    df["priority"] = pd.to_numeric(
        df.get("priority", pd.Series(pd.NA, index=idx)),
        errors="coerce",
        downcast="integer",
    ).astype("Int64")  # type: ignore
    df["group"] = (
        df.get("group", pd.Series([""] * len(df), index=idx))
        .fillna("")  # type: ignore
        .astype(str)
    ).astype("category")
    df["date_creation"] = pd.to_datetime(
        df.get("date_creation", pd.Series([pd.NaT] * len(df), index=idx))
    )
    assigned_to = _normalize_assigned_field(df, "assigned_to", idx)
    df["assigned_to"] = (
        assigned_to.replace({"<NA>": "", "nan": "", "None": ""})
        .fillna(
            "",
        )
        .astype(str)
    )  # type: ignore

    requester = _normalize_assigned_field(df, "requester", idx)
    df["requester"] = requester.replace({"<NA>": "", "nan": "", "None": ""}).fillna("")

    return df[
        [
            "id",
            "name",
            "status",
            "priority",
            "assigned_to",
            "requester",
            "group",
            "date_creation",
        ]
    ].copy()


def _normalize_assigned_field(
    df: pd.DataFrame, field_name: str, idx: pd.Index
) -> pd.Series:
    assigned_raw = df.get(field_name, pd.Series([None] * len(df), index=idx))
    numeric_assigned = pd.to_numeric(assigned_raw, errors="coerce")  # type: ignore
    return (
        numeric_assigned.astype("Int64").astype(str)
        if numeric_assigned.notna().any()
        else assigned_raw.astype(str)
    )


__all__ = [
    "process_raw",
    "FIELD_ALIASES",
    "REQUIRED_FIELDS",
]
