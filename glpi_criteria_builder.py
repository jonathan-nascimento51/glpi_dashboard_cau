"""Utility to build GLPI search filters using human friendly field names."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Criterion:
    """Single search criterion."""

    field: int
    search: str
    link: str = "AND"


class CriteriaBuilder:
    """Compose search criteria for the GLPI REST API."""

    # Default mapping for common ticket fields
    _default_map: Dict[str, int] = {
        "status": 5,
        "group": 21,
        "assigned_to": 9,
    }
    # Cache populated when loading field IDs from the API
    _cache: Dict[str, Dict[str, int]] = {}

    def __init__(
        self,
        *,
        itemtype: str = "Ticket",
        field_map: Optional[Dict[str, int]] = None,
    ) -> None:
        self.itemtype = itemtype
        self._criteria: List[Criterion] = []
        if field_map is not None:
            self.field_map = {k.lower(): v for k, v in field_map.items()}
        else:
            self.field_map = self._cache.get(itemtype, self._default_map.copy())

    @classmethod
    async def load_field_ids(
        cls, session: Any, itemtype: str = "Ticket"
    ) -> Dict[str, int]:
        """Load field IDs from ``session.list_search_options`` and cache them."""
        if itemtype in cls._cache:
            return cls._cache[itemtype]
        options = await session.list_search_options(itemtype)
        mapping: Dict[str, int] = {}
        for fid, info in options.items():
            name = str(info.get("name", "")).strip()
            if not name:
                continue
            key = name.lower().replace(" ", "_")
            try:
                mapping[key] = int(fid)
            except (TypeError, ValueError):
                continue
        cls._cache[itemtype] = mapping
        return mapping

    def add(
        self, field_name: str, value: str, *, link: str = "AND"
    ) -> "CriteriaBuilder":
        """Add a search criterion by human friendly ``field_name``."""
        field_id = self.field_map.get(field_name.lower())
        if field_id is None:
            raise KeyError(f"Unknown field: {field_name}")
        logger.debug(
            "Filtro adicionado: field '%s' (id %s) = '%s', link=%s",
            field_name,
            field_id,
            value,
            link,
        )
        self._criteria.append(Criterion(field_id, value, link))
        return self

    def where_status(self, status: str, *, link: str = "AND") -> "CriteriaBuilder":
        """Add a status filter."""
        return self.add("status", status, link=link)

    def where_group(self, group: str, *, link: str = "AND") -> "CriteriaBuilder":
        """Add an assigned group filter."""
        return self.add("group", group, link=link)

    def build(self) -> Dict[str, str]:
        """Return parameters suitable for ``requests`` ``params`` argument."""
        params: Dict[str, str] = {}
        for idx, crit in enumerate(self._criteria):
            params[f"criteria[{idx}][field]"] = str(crit.field)
            params[f"criteria[{idx}][search]"] = str(crit.search)
            if idx < len(self._criteria) - 1:
                params[f"criteria[{idx}][link]"] = crit.link
        return params
