import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
)  # noqa: E402

from glpi_dashboard.data.pipeline import process_raw  # noqa: E402


def test_process_raw_sanitization():
    raw = [
        {"id": 1, "status": "Closed", "name": None, "assigned_to": 123},
        {"id": None, "status": None, "name": "Chamado A", "assigned_to": None},
        {"status": "new"},
    ]
    df = process_raw(raw)

    assert df.shape == (3, 4)
    assert df.columns.tolist() == ["id", "name", "status", "assigned_to"]

    assert df["id"].tolist() == [1, 0, 0]
    assert df["status"].tolist() == ["closed", "", "new"]
    assert df["name"].iloc[1] == "Chamado A"
    assert df["assigned_to"].iloc[0] == "123"
