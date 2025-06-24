"""Data processing helpers for GLPI tickets."""

from __future__ import annotations

from typing import List, Union

import pandas as pd

TicketData = Union[List[dict], pd.DataFrame, pd.Series]

REQUIRED_FIELDS = ["id", "status", "group", "date_creation", "assigned_to"]


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
    missing = set(REQUIRED_FIELDS) - set(df.columns)
    if missing:
        raise KeyError(f"Missing required fields: {missing}")

    df = df[
        REQUIRED_FIELDS
        + [c for c in df.columns if c not in REQUIRED_FIELDS]
    ]
    df["date_creation"] = pd.to_datetime(
        df["date_creation"], errors="coerce"
    )
    df = df.where(pd.notna(df), None)
    return df


def save_json(df: pd.DataFrame, path: str = "mock/sample_data.json") -> None:
    """Save dataframe to JSON file."""
    df.to_json(path, orient="records", indent=2, date_format="iso")