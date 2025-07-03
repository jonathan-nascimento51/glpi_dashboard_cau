import os
import sys

import pandas as pd

root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(root, "src"))  # noqa: E402

from glpi_dashboard.data import transform  # noqa: E402


def test_to_dataframe_dtypes():
    df = transform.to_dataframe(
        [
            {"id": "1", "status": "new", "assigned_to": "alice", "group": "N1"},
            {"id": 2, "status": "closed", "assigned_to": "bob", "group": "N2"},
        ]
    )
    assert df.dtypes["id"] == "int32"
    assert str(df.dtypes["status"]) == "category"
    assert str(df.dtypes["group"]) == "category"
    assert str(df.dtypes["assigned_to"]) == "category"
    assert df.iloc[0]["id"] == 1


def test_filter_by_status():
    df = pd.DataFrame(
        [
            {"id": 1, "status": "new"},
            {"id": 2, "status": "closed"},
        ]
    )
    result = transform.filter_by_status(df, "closed")
    assert result["id"].tolist() == [2]


def test_aggregate_by_user():
    df = pd.DataFrame(
        [
            {"assigned_to": "alice"},
            {"assigned_to": "bob"},
            {"assigned_to": "alice"},
        ]
    )
    result = transform.aggregate_by_user(df)
    counts = dict(zip(result["assigned_to"], result["count"]))
    assert counts == {"alice": 2, "bob": 1}


def test_empty_dataframe_handling():
    df = transform.to_dataframe([])
    assert df.empty
    assert list(df.columns) == ["id", "status", "assigned_to", "group"]
    result_status = transform.filter_by_status(df, "new")
    assert result_status.empty
    result_agg = transform.aggregate_by_user(df)
    assert result_agg.empty
