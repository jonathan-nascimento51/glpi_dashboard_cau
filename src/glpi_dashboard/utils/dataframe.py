from __future__ import annotations

import pandas as pd


def sanitize_status_column(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with the ``status`` column sanitized.

    Values become lowercase strings and nulls convert to empty strings.
    If the column is missing, the original data is returned untouched.
    """
    if "status" not in df.columns:
        return df.copy()

    sanitized = df.copy()
    sanitized["status"] = sanitized["status"].fillna("").astype(str).str.lower()
    return sanitized
