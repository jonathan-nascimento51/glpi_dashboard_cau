"""HTTPX client with retry and circuit breaker."""

from __future__ import annotations

import httpx
import logging

from .retry_decorator import retry_api_call
from .circuit_breaker import call_with_breaker, breaker

logger = logging.getLogger(__name__)


class ResilientClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault("timeout", 5.0)
        super().__init__(*args, **kwargs)

    async def request(self, method: str, url: str, **kwargs):
        if breaker.current_state == breaker.STATE_OPEN:
            logger.warning("Circuit open, returning fallback")
            return httpx.Response(503, json={"detail": "service unavailable"})

        @retry_api_call
        @call_with_breaker
        async def do_request():
            return await super().request(method, url, **kwargs)

        return await do_request()
