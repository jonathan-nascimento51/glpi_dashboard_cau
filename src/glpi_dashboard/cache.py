from __future__ import annotations

"""Flask-Caching initialization module."""

import os
from flask_caching import Cache

from .config.settings import REDIS_HOST, REDIS_PORT, REDIS_DB

cache_config = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": int(os.getenv("CACHE_REDIS_DB", REDIS_DB)),
    "CACHE_DEFAULT_TIMEOUT": int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300")),
}

cache = Cache(config=cache_config)
