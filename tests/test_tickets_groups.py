import os
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


class FakeSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def get(self, endpoint: str, params: dict | None = None):
        if endpoint.startswith("search/Ticket_User"):
            return {"data": [{"users_id": 2, "groups_id": 3}]}
        if endpoint.startswith("search/Ticket"):
            return {"data": [{"id": 1, "name": "t", "status": 1, "date": "2024-01-01"}]}
        if "User/2" in endpoint:
            return {"id": 2, "name": "Alice", "groups_id": 3}
        if "Group/3" in endpoint:
            return {"id": 3, "completename": "N1"}
        return {"id": 1}


@pytest.mark.asyncio
async def test_collect_basic():
    setup_env()

    session = FakeSession()
    df = await tickets_groups.collect_tickets_with_groups(
        "2024-01-01", "2024-01-02", session=session
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
