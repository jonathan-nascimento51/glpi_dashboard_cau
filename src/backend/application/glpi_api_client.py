"""Async utilities for interacting with the GLPI API.

This module exposes :class:`GlpiApiClient` for high level access to the
GLPI REST API and the helper coroutine
:func:`get_status_counts_by_levels` which aggregates ticket counts by
status for a set of service levels::

    >>> levels = {"N1": 89, "N2": 90}
    >>> await get_status_counts_by_levels(levels)
    {'N1': {'new': 5, 'solved': 2}, 'N2': {...}}

The function returns a mapping of level names to status counts with the
status keys normalised to lower case.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional, Type

import aiohttp

__all__ = [
    "GlpiApiClient",
    "create_glpi_api_client",
    "get_status_counts_by_levels",
    "discover_field_ids",
    "fetch_status_totals",
    "get_status_totals_by_levels",
]

from backend.adapters.factory import create_glpi_session
from backend.adapters.mapping_service import MappingService
from backend.constants import GROUP_IDS, STATUS_ALIAS
from backend.infrastructure.glpi.glpi_session import GLPISession
from backend.schemas.ticket_models import STATUS_MAP, TEXT_STATUS_MAP, CleanTicketDTO
from backend.utils import paginate_items
from shared.dto import TicketTranslator

# Field names we always include in ticket search results.
BASE_TICKET_FIELDS = [
    "id",
    "name",
    "date",
    "priority",
    "status",
    "users_id_assign",
]
# Populated dynamically from MappingService
FORCED_DISPLAY_FIELDS: list[int] = []


def _safe_int(value: Any) -> Optional[int]:
    """Return ``int(value)`` if possible, else ``None``."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


logger = logging.getLogger(__name__)


class GlpiApiClient:
    """High level client that returns fully translated tickets."""

    def __init__(self, session: Optional[GLPISession] = None) -> None:
        if session is None:
            session = create_glpi_session()
        if session is None:
            raise RuntimeError("could not create GLPI session")
        self._session = session
        self._mapper = MappingService(self._session)
        self._translator = TicketTranslator(self._mapper)
        # Default forced fields in case dynamic discovery fails
        self._forced_fields: List[int] = FORCED_DISPLAY_FIELDS.copy()

    async def __aenter__(self) -> "GlpiApiClient":
        await self._session.__aenter__()
        await self._mapper.initialize()
        await self._populate_forced_fields()
        return self

    async def _populate_forced_fields(self) -> None:
        """Resolve numeric IDs for ``BASE_TICKET_FIELDS`` once."""
        if self._forced_fields:
            return
        try:
            options = await self._session.list_search_options("Ticket")
            field_map = {
                info.get("field"): int(fid)
                for fid, info in options.items()
                if isinstance(info, dict) and info.get("field")
            }
            if ids := [
                field_map[name] for name in BASE_TICKET_FIELDS if name in field_map
            ]:
                self._forced_fields[:] = ids
                return
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("failed to load ticket field IDs: %s", exc)
        # Fallback to legacy defaults if lookup fails
        if not self._forced_fields:
            self._forced_fields[:] = [1, 2, 4, 12, 15, 83]

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[Any],
    ) -> None:
        await self._session.__aexit__(exc_type, exc, tb)

    async def _map_numeric_fields_to_names(
        self, itemtype: str, records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Replace numeric keys in ``records`` with field names."""
        try:
            options = await self._session.list_search_options(itemtype)
        except Exception:  # pragma: no cover - best effort
            return records

        id_to_name: Dict[int, str] = {}
        for fid, info in options.items():
            if not isinstance(info, dict):
                continue
            name = info.get("field")
            if not name:
                continue
            try:
                id_to_name[int(fid)] = name
            except (ValueError, TypeError):
                continue

        for record in records:
            for key in list(record.keys()):
                if isinstance(key, int) or (isinstance(key, str) and key.isdigit()):
                    fid = int(key)
                    if name := id_to_name.get(fid):
                        record[name] = record.pop(key)
        return records

    async def _resolve_ticket_fields(self) -> None:
        """Discover essential Ticket field IDs dynamically."""
        try:
            options = await self._mapper.get_search_options("Ticket")
        except Exception as exc:  # pragma: no cover - network failures
            logger.error("failed to fetch ticket search options: %s", exc)
            self._forced_fields = FORCED_DISPLAY_FIELDS.copy()
            return

        mapping = {
            str(field): fid
            for fid, info in options.items()
            if (field := info.get("field")) is not None
        }
        id_field = _safe_int(mapping.get("id"))
        name_field = _safe_int(mapping.get("name"))
        date_field = _safe_int(mapping.get("date_creation"))
        priority_field = _safe_int(mapping.get("priority"))
        assign_field = _safe_int(mapping.get("users_id_assign"))

        if None in (id_field, name_field, date_field, priority_field, assign_field):
            self._forced_fields = FORCED_DISPLAY_FIELDS.copy()
        else:
            # Only assign non-None integer values to _forced_fields.
            self._forced_fields = [
                field
                for field in [
                    id_field,
                    name_field,
                    date_field,
                    priority_field,
                    assign_field,
                ]
                if field is not None
            ]

    async def get_all_paginated(
        self, itemtype: str, page_size: int = 100, **params: Any
    ) -> List[Dict[str, Any]]:
        """Return all items for ``itemtype`` using a resilient page loop."""
        # Normalize itemtype to remove any "search/" prefix
        normalized_itemtype = itemtype.replace("search/", "")
        base_params: Dict[str, Any] = {**params, "expand_dropdowns": 1}

        # Determine the correct endpoint based on whether it's a search query
        if "criteria" in base_params:
            endpoint = f"search/{normalized_itemtype}"
        else:
            endpoint = normalized_itemtype

        # For tickets, always force display of key fields
        if normalized_itemtype == "Ticket":
            base_params.setdefault("forcedisplay", self._forced_fields)

        async def fetch_page(offset: int, size: int) -> Any:
            page_params: Dict[str, Any] = {
                **base_params,
                "range": f"{offset}-{offset + size - 1}",
            }
            return await self._session.get(
                endpoint, params=page_params, return_headers=True
            )

        items = await paginate_items(itemtype, fetch_page, page_size=page_size)
        return await self._map_numeric_fields_to_names(normalized_itemtype, items)

    async def fetch_tickets(self) -> List[CleanTicketDTO]:
        """Return translated tickets from the GLPI API."""
        raw = await self.get_all_paginated("Ticket")
        translated: List[CleanTicketDTO] = []
        for item in raw:
            try:
                translated.append(await self._translator.translate_ticket(item))
            except Exception as exc:  # pragma: no cover - best effort
                logger.error("failed to translate ticket %s: %s", item.get("id"), exc)
        return translated

    async def fetch_tickets_by_ids(self, ids: List[int]) -> List[CleanTicketDTO]:
        """Return translated tickets for the given ``ids``."""

        pairs = [("Ticket", tid) for tid in ids]
        raw = await self._session.get_multiple_items(pairs)
        translated: List[CleanTicketDTO] = []
        for item in raw:
            try:
                translated.append(await self._translator.translate_ticket(item))
            except Exception as exc:  # pragma: no cover - best effort
                logger.error("failed to translate ticket %s: %s", item.get("id"), exc)
        return translated

    async def get_ticket_summary_by_group(self) -> Dict[str, Dict[str, int]]:
        """Aggregate ticket status counts for predefined support groups.

        Uses :data:`backend.constants.GROUP_IDS` to query tickets for each
        service level. The status keys are normalised to lowercase. If any
        request fails, the corresponding group will contain zeros for every
        known status defined in :data:`backend.schemas.ticket_models.TEXT_STATUS_MAP`.
        """

        expected_statuses = list(TEXT_STATUS_MAP.keys())
        summary: Dict[str, Dict[str, int]] = {
            level: {status: 0 for status in expected_statuses} for level in GROUP_IDS
        }

        for level, group_id in GROUP_IDS.items():
            try:
                tickets = await self.get_all_paginated(
                    "Ticket",
                    criteria=[
                        {
                            "field": "groups_id",
                            "searchtype": "equals",
                            "value": str(group_id),
                        }
                    ],
                )
                counts = summary[level]
                for item in tickets:
                    status_name: Optional[str] = None
                    if isinstance(item, dict):
                        status = item.get("status")
                        if isinstance(status, dict):
                            status_name = status.get("name")
                        elif status is not None:
                            status_name = str(status)
                        elif item.get("status_name"):
                            status_name = str(item["status_name"])
                    if not status_name:
                        continue
                    key = status_name.lower()
                    counts[key] = counts.get(key, 0) + 1
            except Exception:  # pragma: no cover - best effort
                logger.exception(
                    "failed to fetch ticket summary for group %s", group_id
                )
                # counts already initialised with zeros
                continue

        return summary

    async def count_status_by_group(
        self, level_ids: Dict[str, int]
    ) -> Dict[str, Dict[str, int]]:
        """Count tickets per status for the given support groups.

        Args:
            level_ids: Mapping of level name to GLPI group ID.

        Returns:
            A dictionary mapping each level name to another dictionary with
            normalised status keys (``new``, ``progress``, ``pending`` and
            ``resolved``) and their respective counts.
        """

        field_ids = await self._mapper.get_ticket_field_ids(["groups_id", "status"])
        if len(field_ids) < 2:
            raise KeyError("required field IDs not found")
        group_field_id, status_field_id = field_ids

        summary: Dict[str, Dict[str, int]] = {
            level: {k: 0 for k in ("new", "progress", "pending", "resolved")}
            for level in level_ids
        }

        for level, group_id in level_ids.items():
            for status_id, raw_name in STATUS_MAP.items():
                params = {
                    "criteria": [
                        {
                            "field": group_field_id,
                            "searchtype": "equals",
                            "value": str(group_id),
                        },
                        {
                            "field": status_field_id,
                            "searchtype": "equals",
                            "value": str(status_id),
                        },
                    ],
                    "range": "0-0",
                }
                try:
                    _, headers = await self._session.get(
                        "search/Ticket", params=params, return_headers=True
                    )
                except (
                    aiohttp.ClientError,
                    asyncio.TimeoutError,
                ):  # pragma: no cover - best effort
                    logger.exception(
                        "failed to count tickets for group %s status %s",
                        group_id,
                        status_id,
                    )
                    continue

                total = 0
                if headers:
                    content_range = headers.get("Content-Range") or headers.get(
                        "content-range"
                    )
                    if content_range and "/" in content_range:
                        try:
                            total = int(content_range.split("/")[-1])
                        except ValueError:
                            logger.warning(
                                "invalid Content-Range header: %s", content_range
                            )

                key = STATUS_ALIAS.get(raw_name.lower(), raw_name.lower())
                summary[level][key] += total

        return summary


async def discover_field_ids(session: GLPISession) -> Dict[str, int]:
    """Return numeric IDs for ``Grupo técnico`` and ``Status`` search fields."""
    options = await session.list_search_options("Ticket")
    group_field_id: Optional[int] = None
    status_field_id: Optional[int] = None
    for fid, info in options.items():
        if not isinstance(info, dict):
            continue
        name = str(info.get("name") or info.get("field") or "").strip().lower()
        if name in {"grupo técnico", "grupo tecnico"}:
            group_field_id = int(fid)
        elif name == "status":
            status_field_id = int(fid)
    if group_field_id is None or status_field_id is None:
        raise KeyError("required field IDs not found")
    return {"group": group_field_id, "status": status_field_id}


async def fetch_status_totals(
    session: GLPISession,
    group_field_id: int,
    status_field_id: int,
    group_id: int,
    status_id: int,
) -> int:
    """Return total tickets for ``group_id`` with ``status_id``."""
    params = {
        "criteria": [
            {"field": group_field_id, "searchtype": "equals", "value": str(group_id)},
            {"field": status_field_id, "searchtype": "equals", "value": str(status_id)},
        ],
        "range": "0-0",
    }
    _, headers = await session.get("search/Ticket", params=params, return_headers=True)
    total = 0
    if headers:
        content_range = headers.get("Content-Range") or headers.get("content-range")
        if content_range and "/" in content_range:
            try:
                total = int(content_range.split("/")[-1])
            except ValueError:
                logger.warning("invalid Content-Range header: %s", content_range)
    return total


async def get_status_totals_by_levels(
    levels: Dict[str, int],
) -> Dict[str, Dict[str, int]]:
    """Return ``{level: {status: total}}`` for each level and status."""
    try:
        async with create_glpi_session() as session:
            field_ids = await discover_field_ids(session)
            group_field = field_ids["group"]
            status_field = field_ids["status"]
            summary: Dict[str, Dict[str, int]] = {}
            for level, group_val in levels.items():
                counts: Dict[str, int] = {}
                for status_code, status_name in STATUS_MAP.items():
                    try:
                        total = await fetch_status_totals(
                            session, group_field, status_field, group_val, status_code
                        )
                    except Exception:  # pragma: no cover - best effort
                        logger.exception(
                            "failed to fetch totals for level %s status %s",
                            level,
                            status_name,
                        )
                        total = 0
                    counts[status_name] = total
                summary[level] = counts
            return summary
    except Exception:  # pragma: no cover - best effort
        logger.exception("failed to compute status totals")
        return {
            level: {status: 0 for status in STATUS_MAP.values()} for level in levels
        }


async def get_status_counts_by_levels(
    level_ids: Dict[str, int],
    client: Optional[GlpiApiClient] = None,
) -> Dict[str, Dict[str, int]]:
    """Return status counts for each support level.

    Args:
        level_ids: Mapping of level names to GLPI group IDs.

    Returns:
        A nested mapping where each level name maps to a dictionary of
        status names (lowercased) and their respective counts. If an
        error occurs while fetching data for a level, that level will
        map to an empty dictionary.
    """

    summary: Dict[str, Dict[str, int]] = {}
    if client is not None:
        # Use the provided client (assume it is already open/ready)
        for level, group_id in level_ids.items():
            try:
                tickets = await client.get_all_paginated(
                    "Ticket",
                    criteria=[
                        {
                            "field": "groups_id",
                            "searchtype": "equals",
                            "value": str(group_id),
                        }
                    ],
                )
                counts: Dict[str, int] = {}
                for item in tickets:
                    status_name: Optional[str] = None
                    if isinstance(item, dict):
                        status = item.get("status")
                        if isinstance(status, dict):
                            status_name = status.get("name")
                        elif status is not None:
                            status_name = str(status)
                        elif item.get("status_name"):
                            status_name = str(item["status_name"])
                    if not status_name:
                        continue
                    key = status_name.lower()
                    counts[key] = counts.get(key, 0) + 1
                summary[level] = counts
            except Exception:  # pragma: no cover - best effort
                logger.exception("failed to fetch status counts for level %s", level)
                summary[level] = {}
    else:
        try:
            async with GlpiApiClient() as new_client:
                for level, group_id in level_ids.items():
                    try:
                        tickets = await new_client.get_all_paginated(
                            "Ticket",
                            criteria=[
                                {
                                    "field": "groups_id",
                                    "searchtype": "equals",
                                    "value": str(group_id),
                                }
                            ],
                        )
                        counts = {}
                        for item in tickets:
                            status_name = None
                            if isinstance(item, dict):
                                status = item.get("status")
                                if isinstance(status, dict):
                                    status_name = status.get("name")
                                elif status is not None:
                                    status_name = str(status)
                                elif item.get("status_name"):
                                    status_name = str(item["status_name"])
                            if not status_name:
                                continue
                            key = status_name.lower()
                            counts[key] = counts.get(key, 0) + 1
                        summary[level] = counts
                    except Exception:  # pragma: no cover - best effort
                        logger.exception(
                            "failed to fetch status counts for level %s", level
                        )
                        summary[level] = {}
        except Exception:  # pragma: no cover - best effort
            logger.exception("failed to initialise GlpiApiClient")
            return {level: {} for level in level_ids}
    return summary


def create_glpi_api_client() -> Optional[GlpiApiClient]:
    try:
        return GlpiApiClient()
    except Exception as exc:  # pragma: no cover - init failures
        logger.exception("failed to create GlpiApiClient: %s", exc)
        return None
