import logging
import json
import redis
from typing import Optional, Dict, Any

from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_TTL_SECONDS

logger = logging.getLogger(__name__)


class RedisClient:
    """
    A client for interacting with Redis, supporting caching with TTL.
    Tracks cache hit/miss ratio.
    """

    def __init__(self):
        self._client: Optional = None
        self._cache_hits = 0
        self._cache_misses = 0

    def _connect(self) -> redis.Redis:
        """Establishes a connection to Redis if not already connected."""
        if self._client is None:
            try:
                self._client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=REDIS_DB,
                    decode_responses=True,  # decode to Python strings
                )
                self._client.ping()  # Test connection
                logger.info("Successfully connected to Redis.")
            except redis.exceptions.ConnectionError as e:
                logger.error(f"Could not connect to Redis: {e}")
                # Reset client on failed connection
                self._client = None
                raise
        return self._client

    def get_cache_metrics(self) -> Dict[str, float]:
        """Returns current cache hit rate and total requests."""
        total_requests = self._cache_hits + self._cache_misses
        if total_requests == 0:
            hit_rate = 0.0
        else:
            hit_rate = (self._cache_hits / total_requests) * 100
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "total": total_requests,
            "hit_rate": hit_rate,
        }

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves data from Redis cache.
        Logs cache hit/miss.
        """
        try:
            client = self._connect()
            cached_data = client.get(key)
            if cached_data:
                self._cache_hits += 1
                logger.debug(f"Cache HIT for key: {key}")
                return json.loads(cached_data)
            else:
                self._cache_misses += 1
                logger.debug(f"Cache MISS for key: {key}")
                return None
        except redis.exceptions.ConnectionError as e:
            logger.error("Redis connection error during GET: %s", e)
            self._client = None  # Reset client to force re-connection
            return None
        except json.JSONDecodeError as e:
            logger.error(
                "Error decoding JSON from Redis for key %s: %s",
                key,
                e,
            )
            # Optionally delete corrupted cache entry
            self.delete(key)
            return None
        except Exception as e:
            logger.error(
                "Unexpected error during Redis GET for key %s: %s",
                key,
                e,
            )
            return None

    def set(
        self, key: str, data: Dict[str, Any], ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Stores data in Redis cache with a configurable TTL.
        [4, 8]
        """
        try:
            client = self._connect()
            if ttl_seconds is None:
                ttl_seconds = REDIS_TTL_SECONDS

            # Use setex for atomic set with expiry [4]
            client.setex(key, ttl_seconds, json.dumps(data))
            logger.debug(f"Cache SET for key: {key} with TTL: {ttl_seconds}s")
        except redis.exceptions.ConnectionError as e:
            logger.error("Redis connection error during SET: %s", e)
            self._client = None
        except Exception as e:
            logger.error(
                "Unexpected error during Redis SET for key %s: %s",
                key,
                e,
            )

    def delete(self, key: str) -> None:
        """Deletes a key from Redis."""
        try:
            client = self._connect()
            client.delete(key)
            logger.debug(f"Cache DELETE for key: {key}")
        except redis.exceptions.ConnectionError as e:
            logger.error("Redis connection error during DELETE: %s", e)
            self._client = None
        except Exception as e:
            logger.error(
                "Unexpected error during Redis DELETE for key %s: %s",
                key,
                e,
            )


# Global Redis client instance
redis_client = RedisClient()
