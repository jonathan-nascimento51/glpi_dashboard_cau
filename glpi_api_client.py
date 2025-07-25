import asyncio
import logging
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from app.api.metrics import compute_overview
from backend.infrastructure.glpi.glpi_auth import GLPIAuthClient
from backend.services.glpi_enrichment import GLPIEnrichmentService
from glpi_ticket_client import GLPITicketClient
from shared.dto import CleanTicketDTO

logger = logging.getLogger(__name__)

BASE_TICKET_FIELDS = [
    "id",
    "name",
    "status",
    "priority",
    "date_creation",
    "users_id_assign",  # Garantindo as informações de atribuição
]


def _resolve_ticket_fields(dynamic_fields: Optional[List[str]] = None) -> List[str]:
    """Resolve e retorna a lista completa de campos de ticket.

    Garante que o campo 'users_id_assign' esteja sempre presente.
    """
    fields = set(BASE_TICKET_FIELDS)
    if dynamic_fields:
        fields.update(dynamic_fields)
    fields.add("users_id_assign")
    return list(fields)


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
        # Substituído self._forced_display_fields por self._forced_fields
        self._forced_fields = self._populate_forced_fields()

    async def __aenter__(self) -> "GlpiApiClient":
        await self.refresh_session()
        return self

    async def __aexit__(
        self,
        exc_type: type | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:
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
        logger.info("Fetching tickets with filters %s", filters)
        result = await asyncio.to_thread(
            self.ticket_client.list_tickets,
            filters,
            page,
            page_size,
        )
        enriched = await self.enrichment.enrich_tickets(result)
        # Convert EnrichedTicket objects to dicts if necessary
        return [dict(e) for e in enriched]

    async def fetch_tickets(self) -> List[CleanTicketDTO]:
        """Return validated tickets without filters."""
        records = await self.get_tickets()
        validated: List[CleanTicketDTO] = []
        for r in records:
            try:
                validated.append(CleanTicketDTO.model_validate(r))
            except ValidationError as exc:  # pragma: no cover - validation edge
                logger.error("validation error for ticket %s: %s", r.get("id"), exc)
        return validated

    async def get_metrics_overview(self) -> Dict[str, Any]:
        """Return aggregated metrics computed from tickets."""
        logger.info("Computing aggregated metrics")
        overview = await compute_overview(client=self)
        return overview.model_dump()

    def _populate_forced_fields(self) -> List[str]:
        """
        Popula a lista de campos forçados que devem estar presentes em cada ticket,
        garantindo que o campo de atribuição esteja incluído.
        """
        _forced_fields: List[str] = ["users_id_assign"]
        # Aqui você pode adicionar outros campos, se necessário.
        return _forced_fields


__all__ = ["GlpiApiClient"]
