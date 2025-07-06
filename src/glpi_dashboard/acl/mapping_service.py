from __future__ import annotations

import logging
from typing import Dict

from ..services.glpi_session import GLPISession

logger = logging.getLogger(__name__)


class MappingService:
    """Fetch and cache dynamic ID-to-name mappings from GLPI."""

    def __init__(self, session: GLPISession) -> None:
        self._session = session
        self._data: Dict[str, Dict[int, str]] = {}

    async def initialize(self) -> None:
        """Load all mappings from the GLPI API."""
        endpoints = {
            "users": "User",
            "groups": "Group",
            "categories": "itilcategory",
            "locations": "Location",
            "operating_systems": "OperatingSystem",
        }
        for key, endpoint in endpoints.items():
            await self._fetch_mapping(endpoint, key)

    async def _fetch_mapping(self, endpoint: str, key: str) -> None:
        """Retrieve data from ``endpoint`` and store ``id``→``name`` pairs."""
        try:
            records = await self._session.get_all(endpoint)
        except Exception as exc:  # pragma: no cover - network failures
            logger.error("Failed to load mapping for %s: %s", endpoint, exc)
            records = []

        mapping: Dict[int, str] = {}
        for item in records:
            try:
                item_id_raw = item.get("id")
                if item_id_raw is None:
                    continue
                item_id = int(item_id_raw)
                name = str(item.get("name", ""))
            except Exception:  # noqa: BLE001
                continue
            if item_id:
                mapping[item_id] = name
        self._data[key] = mapping
        logger.info("Loaded %d entries for %s", len(mapping), key)

    def lookup(self, category: str, item_id: int) -> str | None:
        """Return the name for ``item_id`` in ``category`` if present."""
        return self._data.get(category, {}).get(item_id)
