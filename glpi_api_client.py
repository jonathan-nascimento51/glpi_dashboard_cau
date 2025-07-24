import asyncio
import logging
from typing import Any, Dict, List, Optional

from backend.infrastructure.glpi.glpi_auth import GLPIAuthClient
from backend.services.glpi_enrichment import GLPIEnrichmentService
from shared.dto import CleanTicketDTO

from app.api.metrics import compute_overview
from glpi_ticket_client import GLPITicketClient

logger = logging.getLogger(__name__)


class GlpiApiClient:
    """Facade that orchestrates GLPI API modules."""

    def __init__(
        self,
        *,
        auth_client: Optional[GLPIAuthClient] = None,
        ticket_client: Optional[GLPITicketClient] = None,
        enrichment: Optional[GLPIEnrichmentService] = None,
    ) -> None:
        self.auth_client = auth_client or GLPIAuthClient()
        self.ticket_client = ticket_client or GLPITicketClient(
            auth_client=self.auth_client
        )
        self.enrichment = enrichment or GLPIEnrichmentService(
            auth_client=self.auth_client
        )

    async def __aenter__(self) -> "GlpiApiClient":
        await self.refresh_session()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.enrichment.close()

    async def refresh_session(self) -> str:
        """Force a new session token."""
        token = await self.auth_client.get_session_token(force_refresh=True)
        logger.info("Session refreshed")
        return token

    async def get_tickets(
        self,
        filters: Optional[Dict[str, str]] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> List[Dict[str, Any]]:
        """Return enriched ticket dictionaries."""
        logger.info("Buscando tickets com filtros %s", filters)
        result = await asyncio.to_thread(
            self.ticket_client.list_tickets,
            filters,
            page,
            page_size,
        )
        enriched = await self.enrichment.enrich_tickets(result)
        return enriched

    async def fetch_tickets(self) -> List[CleanTicketDTO]:
        """Return validated tickets without filters."""
        records = await self.get_tickets()
        validated: List[CleanTicketDTO] = []
        for r in records:
            try:
                validated.append(CleanTicketDTO.model_validate(r))
            except Exception as exc:  # pragma: no cover - validation edge
                logger.error("validation error for ticket %s: %s", r.get("id"), exc)
        return validated

    async def get_metrics_overview(self) -> Dict[str, Any]:
        """Return aggregated metrics computed from tickets."""
        logger.info("Obtendo métricas agregadas")
        overview = await compute_overview(client=self)
        return overview.model_dump()


__all__ = ["GlpiApiClient"]
