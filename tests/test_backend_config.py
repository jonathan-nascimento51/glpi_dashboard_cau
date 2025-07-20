import logging

import redis

from backend.config import get_redis_connection


def test_get_redis_connection_failure_logs_warning(monkeypatch, caplog):
    def fail(*_args, **_kwargs):
        raise redis.ConnectionError("fail")

    monkeypatch.setattr(redis, "Redis", fail)

    with caplog.at_level(logging.WARNING):
        conn = get_redis_connection()

    assert conn is None
    assert any("Redis connection failed" in rec.getMessage() for rec in caplog.records)
