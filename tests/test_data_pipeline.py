import pandas as pd
import pytest

from backend.adapters import normalization as transform
from backend.infrastructure.glpi.normalization import process_raw

pytest.importorskip("pandas")


def test_process_raw_sanitization():
    raw = [
        {"id": 1, "status": "Closed", "name": None, "assigned_to": 123},
        {"id": None, "status": None, "name": "Chamado A", "assigned_to": None},
        {"status": "new"},
    ]
    df = process_raw(raw)

    assert df.shape == (3, 7)
    assert df.columns.tolist() == [
        "id",
        "name",
        "status",
        "priority",
        "assigned_to",
        "group",
        "date_creation",
    ]

    assert df["id"].tolist() == [1, 0, 0]
    assert df["status"].tolist() == ["closed", "", "new"]
    assert df["name"].iloc[1] == "Chamado A"
    assert df["assigned_to"].iloc[0] == "123"
    assert df["group"].tolist() == ["", "", ""]
    assert df["priority"].isna().all()
    assert df["date_creation"].isna().all()


def test_process_raw_aliases():
    """Fields with underscore names should be normalized."""
    raw = [
        {
            "id": 1,
            "_status": "New",
            "_priority": 2,
            "_users_id_assign": 5,
            "groups_name": "N1",
            "creation_date": "2024-05-01",
        }
    ]
    df = process_raw(raw)

    assert df.shape[0] == 1
    required_columns = {"id", "status", "priority", "assigned_to", "group", "date_creation"}
    assert required_columns.issubset(df.columns)
    assert "priority" in df.columns
    assert df.iloc[0]["status"] == "new"
    assert df.iloc[0]["priority"] == 2
    assert str(df.dtypes["priority"]) == "Int64"
    assert df.iloc[0]["assigned_to"] == "5"
    assert df.iloc[0]["group"] == "N1"
    assert df.iloc[0]["id"] == 1
    assert df.iloc[0]["date_creation"].strftime("%Y-%m-%d") == "2024-05-01"


def test_process_raw_to_dataframe_dtypes():
    """process_raw combined with to_dataframe yields optimized dtypes."""
    raw = [
        {
            "id": "1",
            "status": "New",
            "assigned_to": 2,
            "group": "N1",
            "date_creation": "2024-06-01",
        },
        {"id": None, "status": "Closed", "assigned_to": None, "group": "N2"},
    ]

    df = process_raw(raw)
    typed = transform.to_dataframe(df.to_dict(orient="records"))

    assert typed.dtypes["id"] == "int32"
    assert str(typed.dtypes["status"]) == "category"
    assert str(typed.dtypes["group"]) == "category"
    assert str(typed.dtypes["assigned_to"]) == "category"


def test_process_raw_memory_usage_reduced():
    """Numeric downcasting and categorical conversion shrink memory usage."""
    raw = [
        {
            "id": str(i),
            "status": "New" if i % 2 == 0 else "Closed",
            "assigned_to": i % 10,
            "group": "N1",
        }
        for i in range(1000)
    ]

    baseline_df = pd.DataFrame(raw)
    baseline_df["name"] = ""
    baseline_df["date_creation"] = pd.NaT
    baseline = baseline_df.memory_usage(deep=True).sum()

    optimized = process_raw(raw).memory_usage(deep=True).sum()

    assert optimized < baseline


def test_process_raw_invalid_date():
    """Invalid date strings should raise a ValueError."""

    raw = [{"id": 1, "status": "New", "date_creation": "not-a-date"}]

    with pytest.raises(ValueError):
        process_raw(raw)
