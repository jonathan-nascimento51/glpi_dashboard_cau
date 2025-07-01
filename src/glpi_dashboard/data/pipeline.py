"""Data processing helpers for GLPI tickets."""

from __future__ import annotations

from typing import List, Union

import pandas as pd

TicketData = Union[List[dict], pd.DataFrame, pd.Series]

REQUIRED_FIELDS = ["id", "status", "group", "assigned_to", "date_creation"]

# Map alternate field names from the GLPI API to our normalized names
ALIASES = {
    "groups_name": "group",
    "users_id_recipient": "assigned_to",
    "creation_date": "date_creation",
}


def _ensure_dataframe(data: TicketData) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data.copy()
    if isinstance(data, pd.Series):
        return pd.DataFrame([data.to_dict()])
    return pd.DataFrame(list(data))


def process_raw(data: TicketData) -> pd.DataFrame:
    """Normalize raw ticket data.

    Parameters
    ----------
    data : list[dict] | pandas.DataFrame | pandas.Series
        Raw ticket data in any supported format.

    Returns
    -------
    pandas.DataFrame
        Cleaned dataframe with required columns and converted types.
    """
    df = _ensure_dataframe(data)

    # Rename columns based on known aliases from the API
    for src, dst in ALIASES.items():
        if src in df.columns and dst not in df.columns:
            df.rename(columns={src: dst}, inplace=True)

    # Determine additional fields to preserve the original payload
    extra_cols = [c for c in df.columns if c not in REQUIRED_FIELDS]
    # Reindex ensures all required fields exist; missing ones are filled with NaN/None
    df = df.reindex(columns=REQUIRED_FIELDS + extra_cols, fill_value=None)
    df["date_creation"] = pd.to_datetime(df["date_creation"], errors="coerce")
    return df


def save_json(df: pd.DataFrame, path: str = "mock/sample_data.json") -> None:
    """Save dataframe to JSON file."""
    df.to_json(path, orient="records", indent=2, date_format="iso")
