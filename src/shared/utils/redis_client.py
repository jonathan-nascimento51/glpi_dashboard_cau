from __future__ import annotations

import inspect
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import pandas as pd
import redis.asyncio as redis
from redis import exceptions as redis_exceptions

from backend.core.settings import (
    REDIS_DB,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_TTL_SECONDS,
)

logger = logging.getLogger(__name__)


def default_json_serializer(obj: Any) -> Any:
    """Return a JSON-serializable representation for unknown objects."""
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    return obj.isoformat() if hasattr(obj, "isoformat") else str(obj)


async def _maybe_await(result: Any) -> Any:
    """Await result if it is awaitable."""
    return await result if inspect.isawaitable(result) else result


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
        self._memory_cache: Dict[str, tuple[Any, datetime]] = {}

    async def _connect(self) -> redis.Redis:
        """Establish a connection to Redis if not already connected."""
        if self._client is None:
            self._client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True,
            )
            try:
                await _maybe_await(self._client.ping())
                logger.info("Successfully connected to Redis.")
            except redis_exceptions.ConnectionError as e:
                logger.error("Could not connect to Redis: %s", e)
                self._client = None
                raise
        return self._client

    def _format_key(self, key: str) -> str:
        return f"{self._prefix}:{key}"

    def get_cache_metrics(self) -> Dict[str, float]:
        """Return current cache metrics."""
        return self.metrics.as_dict()

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data and register hit/miss."""
        try:
            client = await self._connect()
            redis_key = self._format_key(key)
            cached_data = await _maybe_await(client.get(redis_key))
            if cached_data:
                self.metrics.hits += 1
                logger.debug("Cache HIT for key: %s", key)
                return json.loads(cached_data)
        except redis_exceptions.ConnectionError as e:
            logger.warning("Redis indisponível, usando cache em memória: %s", e)
            self._client = None
        except json.JSONDecodeError as e:
            logger.error("Error decoding JSON for key %s: %s", key, e)
            await self.delete(key)
            return None
        except Exception as e:
            logger.error("Unexpected error during Redis GET for key %s: %s", key, e)

        # Fallback: in-memory cache
        value = self._memory_cache.get(key)
        if value:
            data, expires = value
            if expires > datetime.utcnow():
                self.metrics.hits += 1
                logger.debug("Memory cache HIT for key: %s", key)
                return data
            del self._memory_cache[key]
        self.metrics.misses += 1
        logger.debug("Memory cache MISS for key: %s", key)
        return None

    async def set(self, key: str, data: Any, ttl_seconds: Optional[int] = None) -> None:
        """Store JSON-serializable ``data`` in Redis with an optional TTL."""
        ttl = ttl_seconds or REDIS_TTL_SECONDS
        expires = datetime.utcnow() + timedelta(seconds=ttl)
        self._memory_cache[key] = (data, expires)
        try:
            client = await self._connect()
            redis_key = self._format_key(key)
            await _maybe_await(
                client.setex(
                    redis_key,
                    ttl,
                    json.dumps(data, default=default_json_serializer),
                )
            )
            logger.debug("Cache SET for key %s with TTL %s", redis_key, ttl)
        except redis_exceptions.ConnectionError as e:
            logger.warning(
                "Redis indisponível durante SET, mantendo cache em memória: %s", e
            )
            self._client = None
        except Exception as e:
            logger.error("Unexpected error during Redis SET for key %s: %s", key, e)

    async def delete(self, key: str) -> None:
        """Delete a key from Redis."""
        try:
            client = await self._connect()
            redis_key = self._format_key(key)
            await _maybe_await(client.delete(redis_key))
            logger.debug("Cache DELETE for key: %s", redis_key)
        except (
            redis_exceptions.AuthenticationError,
            redis_exceptions.ConnectionError,
        ) as e:
            logger.warning("Redis indisponível durante DELETE: %s", e)
            self._client = None
        except Exception as e:
            logger.error("Unexpected error during Redis DELETE for key %s: %s", key, e)

    async def get_ttl(self, key: str) -> int:
        """Return remaining TTL for a key in seconds or -2 if not found."""
        try:
            client = await self._connect()
            redis_key = self._format_key(key)
            ttl = await _maybe_await(client.ttl(redis_key))
            if ttl is None or int(ttl) < 0:
                value = self._memory_cache.get(key)
                if value:
                    _, expires = value
                    return max(int((expires - datetime.utcnow()).total_seconds()), -2)
            return int(ttl)
        except (
            redis_exceptions.AuthenticationError,
            redis_exceptions.ConnectionError,
        ) as e:
            logger.warning("Redis indisponível durante TTL: %s", e)
            self._client = None
            value = self._memory_cache.get(key)
            if value:
                _, expires = value
                return max(int((expires - datetime.utcnow()).total_seconds()), -2)
            return -2
        except Exception as e:
            logger.error("Unexpected error during Redis TTL for key %s: %s", key, e)
            return -2

    async def close(self) -> None:
        """Close the underlying Redis connection if open."""
        if self._client is not None:
            try:
                await _maybe_await(self._client.close())
                logger.info("Redis connection closed")
            except Exception as e:  # pragma: no cover - defensive
                logger.error("Error closing Redis connection: %s", e)
            finally:
                self._client = None


# Global Redis client instance
redis_client = RedisClient()
