import logging
from typing import Any, Dict, List, Optional, Tuple

from aiohttp_retry import ExponentialRetry, RetryClient

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
        self._retry_client: Optional[RetryClient] = None

    async def __aenter__(self) -> "GlpiApiClient":
        await self._session.__aenter__()
        await self._mapper.initialize()
        retry = ExponentialRetry(attempts=3)
        self._retry_client = RetryClient(retry_options=retry)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._retry_client:
            await self._retry_client.close()
        await self._session.__aexit__(exc_type, exc, tb)

    async def get(
        self,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        return_headers: bool = False,
    ) -> Any | Tuple[Any, Dict[str, str]]:
        return await self._request(
            "GET",
            endpoint,
            params=params,
            headers=headers,
            return_headers=return_headers,
        )

    async def post(
        self,
        endpoint: str,
        *,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        return_headers: bool = False,
    ) -> Any | Tuple[Any, Dict[str, str]]:
        return await self._request(
            "POST",
            endpoint,
            json_data=json_data,
            headers=headers,
            return_headers=return_headers,
        )

    async def put(
        self,
        endpoint: str,
        *,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        return_headers: bool = False,
    ) -> Any | Tuple[Any, Dict[str, str]]:
        return await self._request(
            "PUT",
            endpoint,
            json_data=json_data,
            headers=headers,
            return_headers=return_headers,
        )

    async def delete(
        self,
        endpoint: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        return_headers: bool = False,
    ) -> Any | Tuple[Any, Dict[str, str]]:
        return await self._request(
            "DELETE",
            endpoint,
            headers=headers,
            return_headers=return_headers,
        )

    async def get_all_paginated(
        self, itemtype: str, page_size: int = 100, **params: Any
    ) -> List[Dict[str, Any]]:
        """Return all items for ``itemtype`` using a resilient page loop."""

        base_params = {**params, "expand_dropdowns": 1}
        endpoint = itemtype if itemtype.startswith("search/") else f"search/{itemtype}"

        async def fetch_page(offset: int, size: int):
            page_params = {**base_params, "range": f"{offset}-{offset + size - 1}"}
            return await self.get(endpoint, params=page_params, return_headers=True)

        return await paginate_items(itemtype, fetch_page, page_size=page_size)

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        return_headers: bool = False,
    ) -> Any | Tuple[Any, Dict[str, str]]:
        # sourcery skip: assign-if-exp, reintroduce-else
        """Perform an HTTP request using ``RetryClient``."""

        if self._retry_client is None:
            raise RuntimeError("client not initialized")

        url = f"{self._session.base_url}/{endpoint.lstrip('/')}"
        req_headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "App-Token": self._session.credentials.app_token,
        }
        if self._session._session_token:
            req_headers["Session-Token"] = self._session._session_token
        if headers:
            req_headers |= headers

        attempt = 0
        while True:
            async with self._retry_client.request(
                method,
                url,
                headers=req_headers,
                params=params,
                json=json_data,
            ) as resp:
                if resp.status == 401 and attempt == 0:
                    await self._session._refresh_session_token()
                    req_headers["Session-Token"] = self._session._session_token or ""
                    attempt += 1
                    continue
                resp.raise_for_status()
                data = await resp.json()
                if return_headers:
                    return data, dict(resp.headers)
                return data

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
