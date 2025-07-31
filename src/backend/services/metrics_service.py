from __future__ import annotations

from typing import Dict

import pandas as pd


def calculate_dataframe_metrics(df: pd.DataFrame) -> Dict[str, int]:
    """Return basic ticket metrics from ``df``.

    Parameters
    ----------
    df:
        DataFrame containing a ``status`` column.

    Returns
    -------
    dict
        Mapping with ``total``, ``opened`` and ``closed`` counts.
    """
    if df.empty:
        return {"total": 0, "opened": 0, "closed": 0}

    total = len(df)
    closed = 0
    if "status" in df.columns:
        status_series = df["status"].astype(str).str.lower()
        closed = df[status_series.isin(["closed", "solved"])].shape[0]

    opened = total - closed
    return {"total": total, "opened": opened, "closed": closed}


__all__ = ["calculate_dataframe_metrics"]
