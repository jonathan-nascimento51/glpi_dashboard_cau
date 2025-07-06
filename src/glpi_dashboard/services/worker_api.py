"""FastAPI service exposing GLPI tickets via REST and GraphQL."""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import json
import logging
from functools import wraps
from typing import Any, AsyncGenerator, Awaitable, Callable, List, Optional, Type

import pandas as pd
import strawberry
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from glpi_dashboard.acl import (
    CleanTicketDTO,
    MappingService,
    TicketTranslator,
    process_raw,
)
from glpi_dashboard.services.aggregated_metrics import (
    get_cached_aggregated,
)
from glpi_dashboard.services.exceptions import GLPIAPIError, GLPIUnauthorizedError
from glpi_dashboard.services.glpi_api_client import GlpiApiClient
from glpi_dashboard.services.glpi_session import Credentials, GLPISession
from glpi_dashboard.utils.redis_client import redis_client

from ..config.settings import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
)

logger = logging.getLogger(__name__)


@strawberry.type
class Ticket:
    """GraphQL type for a GLPI ticket."""

    id: int
    status: str
    group: str
    assigned_to: str
    name: str


@strawberry.type
class Metrics:
    """Simple metrics summary."""

    total: int
    opened: int
    closed: int


class ChamadoPorData(BaseModel):
    """Aggregated tickets per creation date."""

    date: str = Field(..., examples=["2024-06-01"])
    total: int = Field(..., examples=[5])


class ChamadosPorDia(BaseModel):
    """Daily ticket totals used for heatmaps."""

    date: str = Field(..., examples=["2024-06-01"])
    total: int = Field(..., examples=[5])


def get_ticket_translator() -> TicketTranslator:
    """Instantiate :class:`TicketTranslator` with configured dependencies."""

    creds = Credentials(
        app_token=GLPI_APP_TOKEN,
        user_token=GLPI_USER_TOKEN,
        username=GLPI_USERNAME,
        password=GLPI_PASSWORD,
    )
    session = GLPISession(GLPI_BASE_URL, creds)
    mapper = MappingService(session)
    return TicketTranslator(mapper)


async def _load_and_translate_tickets(
    translator: TicketTranslator,
    cache=None,
) -> List[CleanTicketDTO]:
    """Return a list of ``CleanTicketDTO`` using the ACL pipeline."""

    cache = cache or redis_client
    cache_key = "tickets_clean"

    cached = await cache.get(cache_key)
    if cached is not None:
        try:
            return [CleanTicketDTO.model_validate(d) for d in cached]
        except Exception:
            pass

    translated: List[CleanTicketDTO] = []
    async with translator.mapper._session as glpi:
        raw_tickets = await glpi.get_all("Ticket")
        for raw_ticket in raw_tickets:
            try:
                clean_ticket = await translator.translate_ticket(raw_ticket)
                translated.append(clean_ticket)
            except Exception as exc:  # pragma: no cover - translation errors
                logger.error(
                    "Falha ao traduzir o ticket ID %s: %s",
                    raw_ticket.get("id"),
                    exc,
                )

    await cache.set(cache_key, [t.model_dump() for t in translated])
    return translated


async def _load_tickets(
    client: Optional[GlpiApiClient] = None,
    cache=None,
) -> pd.DataFrame:
    """Return processed ticket data from the API with caching."""
    cache = cache or redis_client
    cache_key = "tickets_api"
    cached = await cache.get(cache_key)
    if cached is not None:
        try:
            # Extract the actual ticket list if cached is a dict
            data = cached.get("data", cached) if isinstance(cached, dict) else cached
            return process_raw(data)
        except (KeyError, ValueError):
            return pd.DataFrame(data)

    def _sync_fetch(c: GlpiApiClient) -> list[dict]:
        with c as session:
            return session.get_all("Ticket")

    async def _async_fetch() -> list[dict]:
        creds = Credentials(
            app_token=GLPI_APP_TOKEN,
            user_token=GLPI_USER_TOKEN,
            username=GLPI_USERNAME,
            password=GLPI_PASSWORD,
        )
        async with GLPISession(GLPI_BASE_URL, creds) as session:
            return await session.get_all("Ticket")

    try:
        if client is None:
            data = await _async_fetch()
        else:
            data = await asyncio.to_thread(_sync_fetch, client)
    except Exception as exc:  # pragma: no cover - network errors
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if isinstance(data, dict):
        data = data.get("data", data)
    await cache.set(cache_key, data)
    try:
        return process_raw(data)
    except (KeyError, ValueError):
        return pd.DataFrame(data)


async def _stream_tickets(
    client: Optional[GlpiApiClient],
    cache=None,
) -> AsyncGenerator[bytes, None]:
    """Yield progress events followed by final ticket data."""
    yield b"fetching...\n"
    df = await _load_tickets(client=client, cache=cache)
    yield b"processing...\n"
    data = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")
    yield json.dumps(data).encode()


@strawberry.type
class Query:
    @strawberry.field
    async def tickets(self, info: Info) -> List[Ticket]:  # pragma: no cover
        df = await _load_tickets(
            client=info.context.get("client"), cache=info.context.get("cache")
        )
        records = df.astype(object).where(pd.notna(df), None).to_dict("records")
        return [Ticket(**{str(k): v for k, v in r.items()}) for r in records]

    @strawberry.field
    async def metrics(self, info: Info) -> Metrics:
        df = await _load_tickets(
            client=info.context.get("client"), cache=info.context.get("cache")
        )
        total = len(df)
        closed = 0
        if "status" in df:
            status_series = df["status"].astype(str).str.lower()
            closed = df[status_series.isin(["closed", "solved"])].shape[0]
        opened = total - closed
        return Metrics(total=total, opened=opened, closed=closed)  # type: ignore[call-arg]


def create_app(client: Optional[GlpiApiClient] = None, cache=None) -> FastAPI:
    """Create FastAPI app with REST and GraphQL routes."""
    cache = cache or redis_client
    app = FastAPI(title="GLPI Worker API", default_response_class=ORJSONResponse)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # or restrict as needed
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def cache_response(key: str, ttl_seconds: int, model: Type[BaseModel]):
        """Decorator to cache endpoint responses as a list of dicts."""

        def decorator(func: Callable[[], Awaitable[list[dict]]]):
            @wraps(func)
            async def wrapper() -> list[BaseModel]:
                cached_data = await cache.get(key)
                if cached_data is not None:
                    return [model.model_validate(d) for d in cached_data]
                result = await func()
                await cache.set(key, result, ttl_seconds=ttl_seconds)
                return [model.model_validate(d) for d in result]

            return wrapper

        return decorator

    @app.middleware("http")
    async def cache_tickets(request: Request, call_next):  # noqa: F401
        if request.method != "GET" or request.url.path != "/tickets":
            return await call_next(request)

        cached = await cache.get("resp:tickets")
        if cached is not None:
            return JSONResponse(content=cached)
        response = await call_next(request)
        if response.status_code == 200:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            async def new_iter() -> AsyncGenerator[bytes, None]:
                yield body

            response.body_iterator = new_iter()
            with contextlib.suppress(json.JSONDecodeError):
                data = json.loads(body.decode())
                await cache.set("resp:tickets", data)
        return response

    if client is None:
        creds = Credentials(
            app_token=GLPI_APP_TOKEN,
            user_token=GLPI_USER_TOKEN,
            username=GLPI_USERNAME,
            password=GLPI_PASSWORD,
        )
        client = GlpiApiClient(
            GLPI_BASE_URL,
            creds,
        )

    @app.get("/tickets", response_model=list[CleanTicketDTO])
    async def tickets(
        translator: TicketTranslator = Depends(get_ticket_translator),
    ) -> list[CleanTicketDTO]:  # noqa: F401
        return await _load_and_translate_tickets(translator, cache=cache)

    @app.get("/tickets/stream")
    async def tickets_stream() -> StreamingResponse:  # noqa: F401
        return StreamingResponse(
            _stream_tickets(client, cache=cache), media_type="text/plain"
        )

    @app.get("/metrics")
    async def metrics() -> dict:  # noqa: F401
        df = await _load_tickets(client=client, cache=cache)
        total = len(df)
        closed = 0
        if "status" in df:
            status_series = df["status"].astype(str).str.lower()
            closed = df[status_series.isin(["closed", "solved"])].shape[0]
        opened = total - closed
        return {"total": total, "opened": opened, "closed": closed}

    @app.get("/breaker")
    async def breaker_metrics() -> Response:  # noqa: F401
        """Expose Prometheus metrics for the circuit breaker."""
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    @app.get("/metrics/aggregated")
    async def metrics_aggregated() -> dict:  # noqa: F401
        metrics = await get_cached_aggregated(cache, "metrics_aggregated")
        if metrics is None:
            raise HTTPException(status_code=503, detail="metrics not available")
        return metrics

    @app.get(
        "/chamados/por-data",
        response_model=list[ChamadoPorData],
    )
    async def chamados_por_data() -> list[dict]:  # noqa: F401
        data = await cache.get("chamados_por_data")
        if data is None:
            raise HTTPException(status_code=503, detail="metrics not available")
        return data

    @app.get(
        "/chamados/por-dia",
        response_model=list[ChamadosPorDia],
    )
    async def chamados_por_dia() -> list[dict]:  # noqa: F401
        data = await cache.get("chamados_por_dia")
        if data is None:
            raise HTTPException(status_code=503, detail="metrics not available")
        return data

    @app.get("/cache/stats")
    async def cache_stats() -> dict:  # noqa: F401
        return cache.get_cache_metrics()

    @app.get("/cache-metrics")  # legacy name
    async def cache_metrics() -> dict:  # noqa: F401
        return cache.get_cache_metrics()

    @app.get("/health/glpi")
    async def health_glpi() -> JSONResponse:  # noqa: F401
        """Check GLPI connectivity."""
        creds = Credentials(
            app_token=GLPI_APP_TOKEN,
            user_token=GLPI_USER_TOKEN,
            username=GLPI_USERNAME,
            password=GLPI_PASSWORD,
        )
        try:
            async with GLPISession(GLPI_BASE_URL, creds):
                pass
        except (GLPIAPIError, GLPIUnauthorizedError) as exc:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "GLPI connection failed",
                    "details": str(exc),
                },
                headers={"Cache-Control": "no-cache"},
            )
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "GLPI connection successful.",
            },
            headers={"Cache-Control": "no-cache"},
        )

    schema = strawberry.Schema(Query)

    def get_context(request: Request) -> dict[str, Any]:
        return {"client": client, "cache": cache}

    graphql = GraphQLRouter(
        schema,
        path="/",
        context_getter=get_context,
    )
    app.include_router(graphql, prefix="/graphql")
    return app


# Expose ASGI app for uvicorn
app = create_app()


def main() -> None:  # pragma: no cover - manual run
    """CLI for running the worker API."""
    parser = argparse.ArgumentParser(description="Run GLPI worker API")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    args = parser.parse_args()

    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
