import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
)  # noqa: E402

from glpi_dashboard.data.pipeline import process_raw  # noqa: E402
from glpi_dashboard.data import transform  # noqa: E402


def test_process_raw_sanitization():
    raw = [
        {"id": 1, "status": "Closed", "name": None, "assigned_to": 123},
        {"id": None, "status": None, "name": "Chamado A", "assigned_to": None},
        {"status": "new"},
    ]
    df = process_raw(raw)

    assert df.shape == (3, 6)
    assert df.columns.tolist() == [
        "id",
        "name",
        "status",
        "assigned_to",
        "group",
        "date_creation",
    ]

    assert df["id"].tolist() == [1, 0, 0]
    assert df["status"].tolist() == ["closed", "", "new"]
    assert df["name"].iloc[1] == "Chamado A"
    assert df["assigned_to"].iloc[0] == "123"
    assert df["group"].tolist() == ["", "", ""]
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

    assert df.iloc[0]["status"] == "new"
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
