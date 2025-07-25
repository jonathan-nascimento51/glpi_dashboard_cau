from __future__ import annotations

import logging
from typing import Any, Dict, Optional, cast

import aiohttp
import redis.asyncio as redis

from backend.core.settings import REDIS_DB, REDIS_HOST, REDIS_PORT
from backend.infrastructure.glpi.glpi_session import GLPIAPIError, GLPISession
from shared.utils.redis_client import RedisClient

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
        # Avoid using a global Redis client by default to prevent cache
        # cross-contamination in tests or multi-tenant setups.
        self.search_cache = search_cache or RedisClient()
        self._ticket_field_map: Dict[str, int] | None = None

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
        if isinstance(cached, dict):
            return cast(Dict[str, Any], cached)
        if cached is not None:
            logger.warning(
                "Ignoring invalid cached search options for %s: %s",
                itemtype,
                type(cached),
            )

        successful_fetch = False
        try:
            options = await self._session.list_search_options(itemtype)
            successful_fetch = True
        except (
            aiohttp.ClientError,
            GLPIAPIError,
        ) as exc:  # pragma: no cover - network failures
            logger.error("failed to load search options for %s: %s", itemtype, exc)
            options = {}

        ttl = (
            self.cache_ttl_seconds if successful_fetch else 300
        )  # e.g., 5 minutes for failures
        await self.search_cache.set(cache_key, options, ttl_seconds=ttl)
        return options

    async def _get_ticket_field_map(self) -> Dict[str, int]:
        """Return mapping from lower-case field name to numeric ID."""
        if self._ticket_field_map is not None:
            return self._ticket_field_map

        options = await self.get_search_options("Ticket")
        mapping: Dict[str, int] = {}
        for fid, info in options.items():
            if not isinstance(info, dict):
                continue
            name = str(info.get("name", "")).lower()
            if name:
                try:
                    mapping[name] = int(fid)
                except Exception:  # noqa: BLE001
                    continue
        self._ticket_field_map = mapping
        return mapping

    async def get_ticket_field_ids(self, fields: list[str]) -> list[int]:
        """Return numeric IDs for ``fields`` using cached search options."""
        field_map = await self._get_ticket_field_map()
        result: list[int] = []
        for name in fields:
            fid = field_map.get(name.lower())
            if fid is not None:
                result.append(fid)
        return result
