import logging
from typing import Any, Dict, List, Optional

from backend.adapters.factory import create_glpi_session
from backend.adapters.mapping_service import MappingService
from backend.infrastructure.glpi.glpi_session import GLPISession
from backend.utils import paginate_items
from shared.dto import CleanTicketDTO, TicketTranslator

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

    async def __aenter__(self) -> "GlpiApiClient":
        await self._session.__aenter__()
        await self._mapper.initialize()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._session.__aexit__(exc_type, exc, tb)

    async def get_all_paginated(
        self, itemtype: str, page_size: int = 100, **params: Any
    ) -> List[Dict[str, Any]]:
        """Return all items for ``itemtype`` using a resilient page loop."""

        base_params = {**params, "expand_dropdowns": 1}
        # The 'search' endpoint is only necessary when filtering with 'criteria'.
        # Otherwise, use the direct itemtype endpoint to get full objects.
        if "criteria" in base_params:
            endpoint = (
                itemtype if itemtype.startswith("search/") else f"search/{itemtype}"
            )
        else:
            endpoint = itemtype.replace("search/", "")

        async def fetch_page(offset: int, size: int):
            page_params = {**base_params, "range": f"{offset}-{offset + size - 1}"}
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


def create_glpi_api_client() -> Optional[GlpiApiClient]:
    try:
        return GlpiApiClient()
    except Exception as exc:  # pragma: no cover - init failures
        logger.exception("failed to create GlpiApiClient: %s", exc)
        return None
