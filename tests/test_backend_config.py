import logging

import pytest
import redis

from backend.config import get_redis_connection


def test_get_redis_connection_failure_logs_warning(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    def fail(*args: object, **kwargs: object):
        raise redis.ConnectionError("fail")

    monkeypatch.setattr(redis, "Redis", fail)

    # caplog.at_level is a context manager, so no need to annotate as Callable
    with caplog.at_level(logging.WARNING):
        conn = get_redis_connection()

    assert conn is None
    assert any("Redis connection failed" in rec.getMessage() for rec in caplog.records)
