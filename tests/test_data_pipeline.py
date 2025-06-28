import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
)  # noqa: E402

import pandas as pd  # noqa: E402
import pytest  # noqa: E402
from glpi_dashboard.data.pipeline import process_raw, save_json  # noqa: E402

sample = [
    {
        "id": 1,
        "status": "new",
        "group": "N1",
        "date_creation": "2024-01-01",
        "assigned_to": "alice",
        "name": "t1",
    },
    {
        "id": 2,
        "status": "closed",
        "group": "N2",
        "date_creation": "2024-01-02",
        "assigned_to": "bob",
        "name": "t2",
    },
]


def test_process_list():
    df = process_raw(sample)
    assert list(df.columns[:5]) == [
        "id",
        "status",
        "group",
        "date_creation",
        "assigned_to",
    ]
    assert df["date_creation"].dtype.kind == "M"


def test_process_dataframe():
    df_in = pd.DataFrame(sample)
    df = process_raw(df_in)
    assert len(df) == 2


def test_process_series():
    series = pd.Series(sample[0])
    df = process_raw(series)
    assert df.iloc[0]["id"] == 1


def test_missing_fields():
    bad = [{"id": 1}]
    with pytest.raises(KeyError):
        process_raw(bad)


def test_save_json(tmp_path):
    df = process_raw(sample)
    file = tmp_path / "out.json"
    save_json(df, file)
    assert file.exists() and file.read_text()
