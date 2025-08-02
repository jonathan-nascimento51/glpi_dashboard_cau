from typing import List, Optional, Union
from unittest.mock import AsyncMock

import pandas as pd
import pytest

from backend.application import aggregated_metrics
from backend.application.aggregated_metrics import (
    cache_aggregated_metrics,
    get_cached_aggregated,
    status_by_group,
    tickets_by_date,
    tickets_daily_totals,
)
from shared.utils.redis_client import RedisClient

pytest.importorskip("pandas")


def make_df(dates: List[Optional[Union[str, None]]]):
    df = pd.DataFrame({"date_creation": dates})
    df["date_creation"] = pd.to_datetime(df["date_creation"])
    df["date_creation"] = df["date_creation"].astype("datetime64[ns]")
    return df


def test_tickets_by_date_counts():
    df = make_df(
        [
            "2024-06-01",
            "2024-06-01",
            "2024-06-02",
            None,
        ]
    )
    result = tickets_by_date(df)
    assert result.to_dict(orient="records") == [
        {"date": "2024-06-01", "total": 2},
        {"date": "2024-06-02", "total": 1},
    ]


def test_tickets_daily_totals_matches_by_date():
    df = make_df(
        [
            "2024-06-01",
            "2024-06-02",
            "2024-06-02",
        ]
    )
    by_date = tickets_by_date(df)
    daily = tickets_daily_totals(df)
    assert by_date.equals(daily)


@pytest.mark.asyncio
async def test_cache_helpers(monkeypatch: pytest.MonkeyPatch):
    fake = AsyncMock(spec=RedisClient)
    fake.get.return_value = {"status": {"open": 2}}
    monkeypatch.setattr(aggregated_metrics, "redis_client", fake)

    data = {"status": {"open": 2}}
    await cache_aggregated_metrics(None, "k", data)
    fake.set.assert_awaited_once_with("k", data)

    result = await get_cached_aggregated(None, "k")
    fake.get.assert_awaited_once_with("k")
    assert result == data


def test_status_by_group_counts():
    df = pd.DataFrame(
        [
            {"group": "N1", "status": "new"},
            {"group": "N1", "status": "pending"},
            {"group": "N1", "status": "pending"},
            {"group": "N2", "status": "solved"},
            {"group": "N2", "status": "closed"},
        ]
    )

    result = status_by_group(df)
    assert result == {
        "N1": {"new": 1, "pending": 2, "closed": 0},
        "N2": {"new": 0, "pending": 0, "closed": 2},
    }


def test_status_by_group_with_categorical():
    df = pd.DataFrame(
        [
            {"group": "N1", "status": "new"},
            {"group": "N1", "status": None},
            {"group": "N2", "status": "pending"},
        ]
    )

    df["status"] = df["status"].astype("category")
    result = status_by_group(df)
    assert result == {
        "N1": {"new": 1, "pending": 0, "closed": 0},
        "N2": {"new": 0, "pending": 1, "closed": 0},
    }
