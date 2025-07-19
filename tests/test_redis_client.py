import json
from unittest.mock import AsyncMock, MagicMock

import pandas as pd
import pytest
import redis.exceptions
from pytest_mock import MockerFixture

from shared.utils.redis_client import RedisClient


@pytest.mark.asyncio
async def test_set(mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch):
    client = RedisClient()
    mock_redis = MagicMock()
    mock_redis.setex = AsyncMock()
    monkeypatch.setattr(client, "_connect", AsyncMock(return_value=mock_redis))
    await client.set("k", {"v": 1}, ttl_seconds=10)
    mock_redis.setex.assert_called_once()


@pytest.mark.asyncio
async def test_set_timestamp(monkeypatch: pytest.MonkeyPatch):
    client = RedisClient()
    mock_redis = MagicMock()
    mock_redis.setex = AsyncMock()
    monkeypatch.setattr(client, "_connect", AsyncMock(return_value=mock_redis))
    await client.set("k", {"t": pd.Timestamp("2024-01-01")}, ttl_seconds=5)
    args, _ = mock_redis.setex.call_args
    stored = json.loads(args[2])
    assert stored == {"t": "2024-01-01T00:00:00"}


@pytest.mark.asyncio
async def test_get_hit(monkeypatch: pytest.MonkeyPatch):
    client = RedisClient()
    mock_redis = MagicMock()
    mock_redis.get = AsyncMock(return_value=json.dumps({"v": 1}))
    monkeypatch.setattr(client, "_connect", AsyncMock(return_value=mock_redis))
    result = await client.get("k")
    assert result == {"v": 1}
    metrics = client.get_cache_metrics()
    assert metrics["hits"] == 1
    assert metrics["misses"] == 0


@pytest.mark.asyncio
async def test_get_miss(monkeypatch: pytest.MonkeyPatch):
    client = RedisClient()
    mock_redis = MagicMock()
    mock_redis.get = AsyncMock(return_value=None)
    monkeypatch.setattr(client, "_connect", AsyncMock(return_value=mock_redis))
    result = await client.get("missing")
    assert result is None
    metrics = client.get_cache_metrics()
    assert metrics["hits"] == 0
    assert metrics["misses"] == 1


@pytest.mark.asyncio
async def test_delete(monkeypatch: pytest.MonkeyPatch):
    client = RedisClient()
    mock_redis = MagicMock()
    mock_redis.delete = AsyncMock()
    monkeypatch.setattr(client, "_connect", AsyncMock(return_value=mock_redis))
    await client.delete("k")
    mock_redis.delete.assert_called_once_with("glpi:k")


@pytest.mark.asyncio
async def test_get_ttl(monkeypatch: pytest.MonkeyPatch):
    client = RedisClient()
    mock_redis = MagicMock()
    mock_redis.ttl = AsyncMock(return_value=42)
    monkeypatch.setattr(client, "_connect", AsyncMock(return_value=mock_redis))
    ttl = await client.get_ttl("k")
    mock_redis.ttl.assert_called_once()
    assert ttl == 42


@pytest.mark.asyncio
async def test_delete_connection_error(monkeypatch: pytest.MonkeyPatch):
    client = RedisClient()
    mock_redis = MagicMock()
    mock_redis.delete = AsyncMock(side_effect=redis.exceptions.ConnectionError("fail"))
    monkeypatch.setattr(client, "_connect", AsyncMock(return_value=mock_redis))
    await client.delete("k")
    assert client._client is None
    metrics = client.get_cache_metrics()
    assert metrics["hits"] == 0
    assert metrics["misses"] == 0


@pytest.mark.asyncio
async def test_get_ttl_connection_error(monkeypatch: pytest.MonkeyPatch):
    client = RedisClient()
    mock_redis = MagicMock()
    mock_redis.ttl = AsyncMock(side_effect=redis.exceptions.ConnectionError("fail"))
    monkeypatch.setattr(client, "_connect", AsyncMock(return_value=mock_redis))
    ttl = await client.get_ttl("k")
    assert ttl == -2
    assert client._client is None
    metrics = client.get_cache_metrics()
    assert metrics["hits"] == 0
    assert metrics["misses"] == 0
