from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .pipeline import process_raw


def load_mock_data(path: str | Path) -> pd.DataFrame:
    """Read ticket data from a JSON file and normalize it."""
    file = Path(path)
    with file.open() as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("data", data)
    return process_raw(data)
