import datetime as dt
import os
from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend.application import tickets_groups
from backend.infrastructure.glpi.glpi_session import GLPISession


def setup_env() -> None:
    os.environ["GLPI_BASE_URL"] = "http://example.com/apirest.php"
    os.environ["GLPI_APP_TOKEN"] = "a" * 40
    os.environ["GLPI_USER_TOKEN"] = "b" * 40


async def _fake_get_side_effect(
    endpoint: str, params: dict | None = None, **kwargs: Any
) -> dict:
    """Simulate responses from the GLPI API for different endpoints."""
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

    session = AsyncMock(spec=GLPISession)
    session.get.side_effect = _fake_get_side_effect
    df = await tickets_groups.collect_tickets_with_groups(
        "2024-01-01", "2024-01-02", session=session
    )
    assert len(df) == 1
    assert df.iloc[0]["group_name"] == "N1"


def test_pipeline_default(
    monkeypatch: pytest.MonkeyPatch, tmp_path: tickets_groups.Path
):
    """Default output name should include today's date."""
    from pathlib import Path

    import pytest

    pytest.importorskip("pandas")
    import pandas as pd

    async def fake_collect(start: str, end: str, client=None):
        return pd.DataFrame([{"ticket_id": 1}])

    def fake_save(df: pd.DataFrame, path: Path | str) -> Path:
        return tmp_path / Path(path).name

    monkeypatch.setattr(tickets_groups, "collect_tickets_with_groups", fake_collect)
    monkeypatch.setattr(tickets_groups, "save_parquet", fake_save)

    result = tickets_groups.pipeline("2024-01-01", "2024-01-02")
    expected = f"tickets_groups_{dt.date.today():%Y%m%d}.parquet"
    assert result.name == expected
