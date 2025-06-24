import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scripts import filters  # noqa: E402


def sample_df():
    return pd.DataFrame(
        [
            {"id": 1, "status": "new", "group": "N1", "assigned_to": "alice"},
            {
                "id": 2,
                "status": "assigned",
                "group": "N2",
                "assigned_to": "bob",
            },
        ]
    )


def test_by_status():
    df = sample_df()
    assert len(filters.by_status(df, "new")) == 1


def test_by_group():
    df = sample_df()
    assert len(filters.by_group(df, "N2")) == 1


def test_by_technician():
    df = sample_df()
    assert len(filters.by_technician(df, "Alice")) == 1
