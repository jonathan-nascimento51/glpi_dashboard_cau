import logging
from typing import Any, Dict, List, Optional, Type

from backend.adapters.factory import create_glpi_session
from backend.adapters.mapping_service import MappingService
from backend.infrastructure.glpi.glpi_session import GLPISession
from backend.utils import paginate_items
from shared.dto import CleanTicketDTO, TicketTranslator

# Field names we always include in ticket search results.
BASE_TICKET_FIELDS = ["id", "name", "date", "priority", "status"]
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
        if self._forced_display_fields:
            return
        try:
            ids = await self._mapper.get_ticket_field_ids(BASE_TICKET_FIELDS)
            if ids:
                self._forced_display_fields[:] = ids
                return
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("failed to load ticket field IDs: %s", exc)
        # Fallback to legacy defaults if lookup fails
        if not self._forced_display_fields:
            self._forced_display_fields[:] = [1, 2, 4, 12, 15, 83]

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[Any],
    ) -> None:
        await self._session.__aexit__(exc_type, exc, tb)

    async def _resolve_ticket_fields(self) -> None:
        """Discover essential Ticket field IDs dynamically."""
        try:
            options = await self._mapper.get_search_options("Ticket")
        except Exception as exc:  # pragma: no cover - network failures
            logger.error("failed to fetch ticket search options: %s", exc)
            self._forced_fields = FORCED_DISPLAY_FIELDS.copy()
            return

        mapping = {str(info.get("field")): fid for fid, info in options.items()}
        id_field = _safe_int(mapping.get("id"))
        name_field = _safe_int(mapping.get("name"))
        date_field = _safe_int(mapping.get("date_creation"))
        priority_field = _safe_int(mapping.get("priority"))

        if None in (id_field, name_field, date_field, priority_field):
            self._forced_fields = FORCED_DISPLAY_FIELDS.copy()
        else:
            # All fields are guaranteed to be non-None due to the preceding condition.
            self._forced_fields = [id_field, name_field, date_field, priority_field]

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

        return await paginate_items(itemtype, fetch_page, page_size=page_size)

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


def create_glpi_api_client() -> Optional[GlpiApiClient]:
    try:
        return GlpiApiClient()
    except Exception as exc:  # pragma: no cover - init failures
        logger.exception("failed to create GlpiApiClient: %s", exc)
        return None
