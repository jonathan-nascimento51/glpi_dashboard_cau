import os
import re
import datetime as dt
import pytest
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
)  # noqa: E402

from glpi_dashboard.data import tickets_groups  # noqa: E402


def setup_env() -> None:
    os.environ["GLPI_BASE_URL"] = "http://example.com/apirest.php"
    os.environ["GLPI_APP_TOKEN"] = "app"
    os.environ["GLPI_USER_TOKEN"] = "user"


def mock_common(requests_mock):
    requests_mock.post(
        "http://example.com/apirest.php/initSession",
        json={"session_token": "t"},
    )


@pytest.mark.asyncio
async def test_collect_basic(requests_mock):
    setup_env()
    mock_common(requests_mock)
    requests_mock.get(
        re.compile(r"http://example.com/apirest.php/search/Ticket.*"),
        json={"data": [{"id": 1, "name": "t", "status": 1, "date": "2024-01-01"}]},
        headers={"Content-Range": "0-0/1"},
    )
    requests_mock.get(
        re.compile(r"http://example.com/apirest.php/search/Ticket_User.*"),
        json={"data": [{"users_id": 2, "groups_id": 3}]},
        headers={"Content-Range": "0-0/1"},
    )
    requests_mock.get(
        "http://example.com/apirest.php/User/2",
        json={"id": 2, "name": "Alice", "groups_id": 3},
    )
    requests_mock.get(
        "http://example.com/apirest.php/Group/3",
        json={"id": 3, "completename": "N1"},
    )

    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def get_all(self, item, **kwargs):
            if "Ticket_User" in item:
                return [{"users_id": 2, "groups_id": 3}]
            return [{"id": 1, "name": "t", "status": 1, "date": "2024-01-01"}]

        def get(self, *args, **kwargs):
            if "User" in args[0]:
                return {"id": 2, "name": "Alice", "groups_id": 3}
            if "Group" in args[0]:
                return {"id": 3, "completename": "N1"}
            return {"id": 1}

    session = FakeSession()
    df = await tickets_groups.collect_tickets_with_groups(
        "2024-01-01", "2024-01-02", client=session
    )
    assert len(df) == 1
    assert df.iloc[0]["group_name"] == "N1"


def test_pipeline_default(
    monkeypatch: pytest.MonkeyPatch, tmp_path: tickets_groups.Path
):
    """Default output name should include today's date."""
    import pandas as pd
    from pathlib import Path

    async def fake_collect(start: str, end: str, client=None):
        return pd.DataFrame([{"ticket_id": 1}])

    def fake_save(df: pd.DataFrame, path: Path | str) -> Path:
        return tmp_path / Path(path).name

    monkeypatch.setattr(tickets_groups, "collect_tickets_with_groups", fake_collect)
    monkeypatch.setattr(tickets_groups, "save_parquet", fake_save)

    result = tickets_groups.pipeline("2024-01-01", "2024-01-02")
    expected = f"tickets_groups_{dt.date.today():%Y%m%d}.parquet"
    assert result.name == expected
