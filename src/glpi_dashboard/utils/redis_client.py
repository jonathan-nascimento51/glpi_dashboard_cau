from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import redis
import redis.exceptions

from glpi_dashboard.config.settings import (
    REDIS_DB,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_TTL_SECONDS,
)

logger = logging.getLogger(__name__)


@dataclass
class CacheMetrics:
    """Simple structure to expose cache statistics."""

    hits: int = 0
    misses: int = 0

    def as_dict(self) -> Dict[str, float]:
        total = self.hits + self.misses
        hit_rate = (self.hits / total) * 100 if total else 0.0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total": total,
            "hit_rate": hit_rate,
        }


class RedisClient:
    """Wraps Redis operations and tracks metrics."""

    def __init__(self, prefix: str = "glpi") -> None:
        self._client: Optional[redis.Redis] = None
        self._prefix = prefix
        self.metrics = CacheMetrics()

    def _connect(self) -> redis.Redis:
        """Establish a connection to Redis if not already connected."""
        if self._client is None:
            self._client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True,
            )
            try:
                self._client.ping()
                logger.info("Successfully connected to Redis.")
            except redis.exceptions.ConnectionError as e:
                logger.error("Could not connect to Redis: %s", e)
                self._client = None
                raise
        return self._client

    def _format_key(self, key: str) -> str:
        return f"{self._prefix}:{key}"

    def get_cache_metrics(self) -> Dict[str, float]:
        """Return current cache metrics."""
        return self.metrics.as_dict()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data and register hit/miss."""
        try:
            client = self._connect()
            redis_key = self._format_key(key)
            cached_data = client.get(redis_key)
            if cached_data:
                self.metrics.hits += 1
                logger.debug("Cache HIT for key: %s", key)
                return json.loads(cached_data)
            self.metrics.misses += 1
            logger.debug("Cache MISS for key: %s", key)
            return None
        except redis.exceptions.ConnectionError as e:
            logger.error("Redis connection error during GET: %s", e)
            self._client = None
            return None
        except json.JSONDecodeError as e:
            logger.error("Error decoding JSON for key %s: %s", key, e)
            self.delete(key)
            return None
        except Exception as e:
            logger.error("Unexpected error during Redis GET for key %s: %s", key, e)
            return None

    def set(
        self, key: str, data: Dict[str, Any], ttl_seconds: Optional[int] = None
    ) -> None:

        """Store data in Redis cache with an optional TTL."""
        try:
            client = self._connect()
            ttl = ttl_seconds or REDIS_TTL_SECONDS
            redis_key = self._format_key(key)
            client.setex(redis_key, ttl, json.dumps(data))
            logger.debug("Cache SET for key %s with TTL %s", redis_key, ttl)
        except redis.exceptions.ConnectionError as e:
            logger.error("Redis connection error during SET: %s", e)
            self._client = None
        except Exception as e:
            logger.error("Unexpected error during Redis SET for key %s: %s", key, e)

    def delete(self, key: str) -> None:
        """Delete a key from Redis."""
        try:
            client = self._connect()
            redis_key = self._format_key(key)
            client.delete(redis_key)
            logger.debug("Cache DELETE for key: %s", redis_key)
        except redis.exceptions.AuthenticationError as e:
            logger.error("Redis connection error during DELETE: %s", e)
            self._client = None
        except Exception as e:
            logger.error("Unexpected error during Redis DELETE for key %s: %s", key, e)

    def get_ttl(self, key: str) -> int:
        """Return remaining TTL for a key in seconds or -2 if not found."""
        try:
            client = self._connect()
            redis_key = self._format_key(key)
            return client.ttl(redis_key)
        except redis.exceptions.AuthenticationError as e:
            logger.error("Redis connection error during TTL: %s", e)
            self._client = None
            return -2
        except Exception as e:
            logger.error("Unexpected error during Redis TTL for key %s: %s", key, e)
            return -2


# Global Redis client instance
redis_client = RedisClient()
