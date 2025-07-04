"""Async GLPI REST API client with resilience patterns."""

from __future__ import annotations

import logging
from typing import Any, List

import httpx
from purgatory import AsyncCircuitBreakerFactory
from pydantic import BaseModel, Field
from tenacity import AsyncRetrying, RetryError, stop_after_attempt, wait_exponential

from .glpi_adapter import CleanTicketDTO, RawTicketDTO, convert_ticket

logger = logging.getLogger(__name__)


class ClientParams(BaseModel):
    """Parameters for :class:`GLPIApiClient`."""

    base_url: str = Field(..., description="Base URL for GLPI API")
    client: httpx.AsyncClient = Field(..., description="Injected HTTPX client")


class GLPIApiClient:
    """Asynchronous GLPI API client with retry and circuit breaker."""

    def __init__(self, base_url: str, client: httpx.AsyncClient) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = client
        self._breaker_factory = AsyncCircuitBreakerFactory(
            default_threshold=5, default_ttl=30
        )

    async def _request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> httpx.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        @self._breaker_factory("glpi_api")
        async def send() -> httpx.Response:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(5),
                wait=wait_exponential(multiplier=1, min=1, max=10),
                reraise=True,
            ):
                with attempt:
                    resp = await self.client.request(
                        method, url, timeout=30.0, **kwargs
                    )
                    if resp.status_code in {429, 500, 502, 503, 504}:
                        logger.warning(
                            "Retrying %s %s due to status %s",
                            method,
                            url,
                            resp.status_code,
                        )
                        resp.raise_for_status()
                    resp.raise_for_status()
                    return resp

        try:
            return await send()
        except RetryError as exc:
            raise httpx.HTTPError("Retry failed") from exc

    async def fetch_tickets(self, **params: Any) -> List[CleanTicketDTO]:
        """Fetch all tickets using pagination and return clean DTOs."""

        params = {**params, "expand_dropdowns": 1}
        results: List[CleanTicketDTO] = []
        offset = 0
        limit = int(params.pop("limit", 100))

        while True:
            params["range"] = f"{offset}-{offset + limit - 1}"
            resp = await self._request("GET", "search/Ticket", params=params)
            data = resp.json().get("data", [])
            if isinstance(data, dict):
                data = [data]
            for item in data:
                if isinstance(item, dict):
                    raw = RawTicketDTO.model_validate(item)
                    results.append(convert_ticket(raw))
            content_range = resp.headers.get("Content-Range")
            if not content_range:
                break
            try:
                total = int(content_range.split("/")[1])
            except (IndexError, ValueError):
                break
            offset += limit
            if offset >= total:
                break
        return results


async def fetch_tickets(params: ClientParams, **query: Any) -> List[CleanTicketDTO]:
    """Helper that instantiates :class:`GLPIApiClient` and retrieves tickets."""

    client = GLPIApiClient(params.base_url, params.client)
    return await client.fetch_tickets(**query)


__all__ = ["GLPIApiClient", "ClientParams", "fetch_tickets"]
