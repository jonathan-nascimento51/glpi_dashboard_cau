from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import redis.asyncio as redis
from backend.core.settings import REDIS_DB, REDIS_HOST, REDIS_PORT
from backend.infrastructure.glpi.glpi_session import GLPISession
from shared.utils.redis_client import RedisClient
from shared.utils.redis_client import redis_client as default_redis_client

logger = logging.getLogger(__name__)


class MappingService:
    """Fetch and cache dynamic ID-to-name mappings from GLPI."""

    def __init__(
        self,
        session: GLPISession,
        redis_client: Optional[redis.Redis] = None,
        cache_ttl_seconds: int = 86400,
        search_cache: Optional[RedisClient] = None,
    ) -> None:
        self._session = session
        self._data: Dict[str, Dict[int, str]] = {}
        self.cache_ttl_seconds = cache_ttl_seconds
        self.redis = redis_client or redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
        )
        self.search_cache = search_cache or default_redis_client

    async def initialize(self) -> None:
        """Load all mappings from the GLPI API into memory and cache."""
        endpoints = {
            "users": ("glpi:mappings:users", "User"),
            "groups": ("glpi:mappings:groups", "Group"),
            "categories": ("glpi:mappings:categories", "itilcategory"),
            "locations": ("glpi:mappings:locations", "Location"),
            "operating_systems": ("glpi:mappings:operating_systems", "OperatingSystem"),
        }
        for key, (cache_key, endpoint) in endpoints.items():
            mapping = await self._get_mapping(cache_key, endpoint)
            self._data[key] = mapping

    async def _index_all(self, endpoint: str) -> list[dict]:
        """Return all records for ``endpoint`` using the GLPI session."""
        return await self._session.get_all(endpoint)

    async def _get_mapping(self, cache_key: str, endpoint: str) -> Dict[int, str]:
        """Return mapping from cache or fetch from GLPI and populate cache."""
        cached = await self.redis.hgetall(cache_key)
        if cached:
            return {int(k): v for k, v in cached.items()}

        try:
            records = await self._index_all(endpoint)  # type: ignore[attr-defined]
        except Exception as exc:  # pragma: no cover - network failures
            logger.error("failed to load mapping for %s: %s", endpoint, exc)
            records = []

        mapping: Dict[int, str] = {}
        for item in records:
            try:
                item_id_raw = item.get("id")
                if item_id_raw is None:
                    continue
                item_id = int(item_id_raw)
                name = str(item.get("name", "N/A"))
            except Exception:  # noqa: BLE001
                continue
            if item_id:
                mapping[item_id] = name

        async with self.redis.pipeline() as pipe:
            if mapping:
                await pipe.hset(
                    cache_key, mapping={str(k): v for k, v in mapping.items()}
                )
            await pipe.expire(cache_key, self.cache_ttl_seconds)
            await pipe.execute()

        logger.info("Loaded %d entries for %s", len(mapping), endpoint)
        return mapping

    def lookup(self, category: str, item_id: int) -> str | None:
        """Return the name for ``item_id`` in ``category`` if present."""
        return self._data.get(category, {}).get(item_id)

    async def get_user_map(self) -> Dict[int, str]:
        """Return user ID to name mapping using cache-aside strategy."""
        mapping = await self._get_mapping("glpi:mappings:users", "User")
        self._data["users"] = mapping
        return mapping

    async def get_username(self, user_id: int) -> str:
        """Return user name for ``user_id`` or ``"Unassigned"`` if missing."""
        user_map = await self.get_user_map()
        return user_map.get(user_id, "Unassigned")

    async def get_search_options(self, itemtype: str) -> Dict[str, Any]:
        """Return cached search options for ``itemtype`` or fetch from GLPI."""
        cache_key = f"search_options:{itemtype}"
        cached = await self.search_cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            options = await self._session.list_search_options(itemtype)
        except Exception as exc:  # pragma: no cover - network failures
            logger.error("failed to load search options for %s: %s", itemtype, exc)
            options = {}

        await self.search_cache.set(
            cache_key, options, ttl_seconds=self.cache_ttl_seconds
        )
        return options
