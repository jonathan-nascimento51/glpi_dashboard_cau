import asyncio
from typing import Any, Dict, List, Optional, Set, TypedDict

from backend.adapters.factory import create_glpi_session
from backend.infrastructure.glpi.glpi_session import GLPISession
from shared.utils.logging import get_logger

logger = get_logger(__name__)


class EnrichedTicket(TypedDict, total=False):
    id: int
    status: int
    status_name: str
    users_id_recipient: int
    user_name: str
    groups_id_assign: int
    group_name: str


class GLPIEnrichmentService:
    """Map and enrich raw GLPI ticket data with readable fields."""

    DEFAULT_UNKNOWN_VALUE = "Unknown"

    def __init__(self, session: Optional[GLPISession] = None) -> None:
        """Create service using an existing :class:`GLPISession` if provided."""

        provided = session is not None
        if session is None:
            session = create_glpi_session()
        if session is None:
            raise RuntimeError("could not create GLPI session")

        self._session = session
        self._owns_session = not provided
        self._status_map: Dict[int, str] = {}
        self._user_cache: Dict[int, str] = {}
        self._group_cache: Dict[int, str] = {}

    async def close(self) -> None:
        if self._owns_session:
            await self._session.close()

    async def _request(self, endpoint: str) -> Dict[str, Any]:
        """Proxy ``GET`` requests through the underlying ``GLPISession``."""

        return await self._session.get(endpoint)

    async def _load_statuses(self) -> None:
        if self._status_map:
            return
        logger.info("Carregando lista de status do GLPI")
        data = await self._request("TicketStatus")
        records = data.get("data", data)
        mapping: Dict[int, str] = {}
        for item in records:
            try:
                sid = int(item.get("id"))
                name = str(item.get("name"))
            except (ValueError, TypeError):
                continue
            mapping[sid] = name
        self._status_map.update(mapping)

    async def _get_status_name(self, status_id: int) -> str:
        await self._load_statuses()
        return self._status_map.get(status_id, self.DEFAULT_UNKNOWN_VALUE)

    async def _fetch_user_name(self, user_id: int) -> str:
        data = await self._request(f"User/{user_id}")
        return str(data.get("name", self.DEFAULT_UNKNOWN_VALUE))

    async def _get_user_name(self, user_id: int) -> str:
        cached = self._user_cache.get(user_id)
        if cached is not None:
            return cached
        logger.info("User ID %s não encontrado no cache, consultando API...", user_id)
        name = await self._fetch_user_name(user_id)
        self._user_cache[user_id] = name
        return name

    async def _fetch_group_name(self, group_id: int) -> str:
        data = await self._request(f"Group/{group_id}")
        return str(data.get("name", self.DEFAULT_UNKNOWN_VALUE))

    async def _get_group_name(self, group_id: int) -> str:
        cached = self._group_cache.get(group_id)
        if cached is not None:
            return cached
        logger.info("Group ID %s não encontrado no cache, consultando API...", group_id)
        name = await self._fetch_group_name(group_id)
        self._group_cache[group_id] = name
        return name

    async def enrich_ticket(self, ticket: Dict[str, Any]) -> EnrichedTicket:
        if "status_name" not in ticket and "status" in ticket:
            ticket["status_name"] = await self._get_status_name(int(ticket["status"]))
        if "users_id_recipient" in ticket and "user_name" not in ticket:
            uid = ticket.get("users_id_recipient")
            if uid is not None:
                ticket["user_name"] = await self._get_user_name(int(uid))
        if "groups_id_assign" in ticket and "group_name" not in ticket:
            gid = ticket.get("groups_id_assign")
            if gid is not None:
                ticket["group_name"] = await self._get_group_name(int(gid))
        return ticket  # type: ignore[return-value]

    async def enrich_tickets(
        self, tickets: List[Dict[str, Any]]
    ) -> List[EnrichedTicket]:
        user_ids: Set[int] = set()
        group_ids: Set[int] = set()
        for t in tickets:
            uid = t.get("users_id_recipient")
            if uid is not None and "user_name" not in t:
                user_ids.add(int(uid))
            gid = t.get("groups_id_assign")
            if gid is not None and "group_name" not in t:
                group_ids.add(int(gid))
        await asyncio.gather(
            *(self._get_user_name(uid) for uid in user_ids),
            return_exceptions=True,
        )
        await asyncio.gather(
            *(self._get_group_name(gid) for gid in group_ids),
            return_exceptions=True,
        )
        results = []
        for ticket in tickets:
            results.append(await self.enrich_ticket(ticket))
        return results
