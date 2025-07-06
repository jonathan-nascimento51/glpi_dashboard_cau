"""Compatibility wrappers for the new Anti-Corruption Layer."""

from __future__ import annotations

from pandas import DataFrame

from ..acl import process_raw


def save_json(df: DataFrame, path: str = "mock/sample_data.json") -> None:
    """Save dataframe to JSON file."""

    df.to_json(path, orient="records", indent=2, date_format="iso")


__all__ = ["process_raw", "save_json"]
