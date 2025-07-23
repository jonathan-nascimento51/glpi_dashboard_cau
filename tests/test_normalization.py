import pytest

from backend.adapters.normalization import (
    aggregate_by_user,
    filter_by_status,
    sanitize_status_column,
    to_dataframe,
)

pytest.importorskip("pandas")


@pytest.fixture()
def ticket_list():
    return [
        {"id": "1", "status": "New", "assigned_to": "alice", "group": "N1"},
        {"id": None, "status": None, "group": "N2"},
        {"status": "PENDING", "assigned_to": None, "group": None},
    ]


@pytest.fixture()
def ticket_df(ticket_list):
    return to_dataframe(ticket_list)


def test_to_dataframe_converts_and_sets_defaults(ticket_df):
    assert ticket_df.dtypes["id"] == "int32"
    assert str(ticket_df.dtypes["status"]) == "category"
    assert str(ticket_df.dtypes["assigned_to"]) == "category"
    assert str(ticket_df.dtypes["group"]) == "category"

    assert ticket_df["id"].tolist() == [1, 0, 0]
    assert ticket_df["assigned_to"].tolist() == ["alice", "", ""]
    assert ticket_df["group"].tolist() == ["N1", "N2", ""]
    assert ticket_df["status"].tolist() == ["New", "", "PENDING"]


def test_filter_by_status(ticket_df):
    closed = filter_by_status(ticket_df, "New")
    assert closed["id"].tolist() == [1]


def test_aggregate_by_user(ticket_df):
    result = aggregate_by_user(ticket_df)
    counts = dict(zip(result["assigned_to"], result["count"]))
    assert counts == {"alice": 1, "": 2}


def test_sanitize_status_column(ticket_df):
    sanitized = sanitize_status_column(ticket_df)
    assert sanitized["status"].tolist() == ["new", "", "pending"]
    assert sanitized["status"].dtype == object
