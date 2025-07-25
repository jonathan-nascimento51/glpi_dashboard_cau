from __future__ import annotations

import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from shared.utils.logging import set_correlation_id


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach a ``request_id`` to each request via context variables."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request, call_next: Callable):
        request_id = uuid.uuid4().hex
        set_correlation_id(request_id)
        try:
            response = await call_next(request)
        finally:
            set_correlation_id(None)
        response.headers["X-Request-ID"] = request_id
        return response
