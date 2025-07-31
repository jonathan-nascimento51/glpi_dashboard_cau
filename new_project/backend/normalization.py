from __future__ import annotations

from typing import Iterable

import pandas as pd


def process_raw(data: Iterable[dict[str, object]] | pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame representation of ``data``."""

    if isinstance(data, pd.DataFrame):
        return data.copy()
    return pd.DataFrame(list(data))
