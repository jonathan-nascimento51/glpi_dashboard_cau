import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from glpi_dashboard.utils.redis_client import RedisClient


@pytest.mark.asyncio
async def test_set(monkeypatch):
    client = RedisClient()
    mock_redis = MagicMock()
    mock_redis.setex = AsyncMock()
    monkeypatch.setattr(client, "_connect", AsyncMock(return_value=mock_redis))
    await client.set("k", {"v": 1}, ttl_seconds=10)
    mock_redis.setex.assert_called_once()


@pytest.mark.asyncio
async def test_get_hit(monkeypatch):
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
async def test_get_miss(monkeypatch):
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
async def test_delete(monkeypatch):
    client = RedisClient()
    mock_redis = MagicMock()
    mock_redis.delete = AsyncMock()
    monkeypatch.setattr(client, "_connect", AsyncMock(return_value=mock_redis))
    await client.delete("k")
    mock_redis.delete.assert_called_once_with("glpi:k")


@pytest.mark.asyncio
async def test_get_ttl(monkeypatch):
    client = RedisClient()
    mock_redis = MagicMock()
    mock_redis.ttl = AsyncMock(return_value=42)
    monkeypatch.setattr(client, "_connect", AsyncMock(return_value=mock_redis))
    ttl = await client.get_ttl("k")
    mock_redis.ttl.assert_called_once()
    assert ttl == 42
