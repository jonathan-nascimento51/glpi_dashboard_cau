import json
from unittest.mock import MagicMock

from redis_client import RedisClient


def test_set(monkeypatch):
    client = RedisClient()
    mock_redis = MagicMock()
    monkeypatch.setattr(client, "_connect", lambda: mock_redis)
    client.set("k", {"v": 1}, ttl_seconds=10)
    mock_redis.setex.assert_called_once_with("k", 10, json.dumps({"v": 1}))


def test_get_hit(monkeypatch):
    client = RedisClient()
    mock_redis = MagicMock()
    mock_redis.get.return_value = json.dumps({"v": 1})
    monkeypatch.setattr(client, "_connect", lambda: mock_redis)
    result = client.get("k")
    assert result == {"v": 1}
    metrics = client.get_cache_metrics()
    assert metrics["hits"] == 1
    assert metrics["misses"] == 0


def test_get_miss(monkeypatch):
    client = RedisClient()
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    monkeypatch.setattr(client, "_connect", lambda: mock_redis)
    result = client.get("missing")
    assert result is None
    metrics = client.get_cache_metrics()
    assert metrics["hits"] == 0
    assert metrics["misses"] == 1


def test_delete(monkeypatch):
    client = RedisClient()
    mock_redis = MagicMock()
    monkeypatch.setattr(client, "_connect", lambda: mock_redis)
    client.delete("k")
    mock_redis.delete.assert_called_once_with("k")
