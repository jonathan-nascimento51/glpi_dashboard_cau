"""Flask-Caching initialization module."""

from __future__ import annotations

import os

from flask_caching import Cache

from backend.core.settings import REDIS_DB, REDIS_HOST, REDIS_PORT

cache_type = os.getenv("CACHE_TYPE", "redis").lower()
cache_config: dict[str, object]
if cache_type == "simple":
    cache_config = {"CACHE_TYPE": "SimpleCache"}
else:
    cache_config = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_HOST": REDIS_HOST,
        "CACHE_REDIS_PORT": REDIS_PORT,
        "CACHE_REDIS_DB": int(os.getenv("CACHE_REDIS_DB", REDIS_DB)),
        "CACHE_DEFAULT_TIMEOUT": int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300")),
    }
cache = Cache(config=cache_config)
if cache_type != "simple":  # pragma: no cover - optional
    try:
        cache.cache._read_client.ping()
    except Exception as exc:  # pragma: no cover - Redis missing
        import logging

        logging.warning("Redis unavailable, falling back to SimpleCache: %s", exc)
        cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
