"""FastAPI service exposing GLPI tickets via REST and GraphQL.

All REST endpoints require the ``/v1`` prefix while GraphQL is served at
``/v1/graphql``. This convention allows future versions to coexist without
breaking existing clients.
"""

from __future__ import annotations

import argparse
import datetime
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, cast

import pandas as pd
import strawberry
import uvicorn
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    PlainTextResponse,
    StreamingResponse,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from backend.api.request_id_middleware import RequestIdMiddleware
from backend.application.aggregated_metrics import (
    compute_aggregated,
    get_cached_aggregated,
)
from backend.application.glpi_api_client import (
    GlpiApiClient,
    create_glpi_api_client,
    get_status_totals_by_levels,
)
from backend.application.read_model import query_ticket_summary
from backend.application.ticket_loader import (
    check_glpi_connection,
    load_and_translate_tickets,
    load_tickets,
    stream_tickets,
)
from backend.constants import GROUP_IDS
from backend.core.settings import KNOWLEDGE_BASE_FILE
from backend.schemas.metrics import MetricsSummary
from backend.schemas.ticket import ChamadoPorData, ChamadosPorDia, TicketSummaryOut
from backend.schemas.ticket_models import CleanTicketDTO
from backend.services.document_service import read_file
from backend.services.metrics_service import calculate_dataframe_metrics
from shared.utils.api_auth import verify_api_key
from shared.utils.json import UTF8JSONResponse
from shared.utils.logging import init_logging
from shared.utils.redis_client import redis_client

init_logging()

logger = logging.getLogger(__name__)


def get_glpi_client() -> Optional[GlpiApiClient]:
    """Return an instance of :class:`GlpiApiClient` or ``None``."""
    return create_glpi_api_client()


@strawberry.type
class Ticket:
    """GraphQL type for a GLPI ticket."""

    id: int
    status: str
    group: str
    assigned_to: str
    name: str
    date_creation: Optional[datetime.datetime]


@strawberry.type
class Metrics:
    """Simple metrics summary."""

    total: int
    opened: int
    closed: int


async def _load_and_cache_df(info: Info) -> pd.DataFrame:
    """
    Helper to load the tickets DataFrame and cache it in the request context
    to avoid redundant loads within the same GraphQL query.
    """
    if "tickets_df" not in info.context:
        df = await load_tickets(
            client=info.context.get("client"), cache=info.context.get("cache")
        )
        info.context["tickets_df"] = df
    return info.context["tickets_df"]


@strawberry.type
class Query:
    @strawberry.field
    async def tickets(self, info: Info) -> List[Ticket]:  # pragma: no cover
        df = await _load_and_cache_df(info)
        records = df.astype(object).where(pd.notna(df), None).to_dict("records")
        return [Ticket(**{str(k): v for k, v in r.items()}) for r in records]

    @strawberry.field
    async def metrics(self, info: Info) -> Metrics:
        df = await _load_and_cache_df(info)
        metrics_data = calculate_dataframe_metrics(df)
        return Metrics(**metrics_data)  # type: ignore[call-arg]


async def metrics_summary(request: Request, response: Response) -> MetricsSummary:
    """Return total, opened and closed ticket counts.

    This lightweight endpoint powers KPI cards without fetching the full
    ticket dataset.
    """

    client: Optional[GlpiApiClient] = request.app.state.client
    cache = request.app.state.cache
    df = await load_tickets(client=client, cache=cache, response=response)
    data = calculate_dataframe_metrics(df)
    return MetricsSummary.model_validate(data)


def create_app(client: Optional[GlpiApiClient] = None, cache=None) -> FastAPI:
    """Create FastAPI app exposing versioned REST and GraphQL endpoints.

    All REST endpoints are registered under the ``/v1`` prefix to allow
    future versions to coexist. GraphQL is available at ``/v1/graphql``.
    """
    cache = cache or redis_client

    if client is None:
        client = create_glpi_api_client()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # On startup
        await load_tickets(client=client, cache=cache)
        yield
        # On shutdown (if needed)

    deps = [Depends(verify_api_key)] if os.getenv("DASHBOARD_API_TOKEN") else []
    app = FastAPI(
        title="GLPI Worker API",
        default_response_class=UTF8JSONResponse,
        lifespan=lifespan,
        dependencies=deps,
    )
    app.state.client = client
    app.state.cache = cache
    app.add_middleware(RequestIdMiddleware)
    FastAPIInstrumentor().instrument_app(app)
    Instrumentator().instrument(app).expose(app)

    env = os.getenv("APP_ENV", "development").lower()
    if env == "production":
        allowed_origins = [
            origin.strip()
            for origin in os.getenv("API_CORS_ALLOW_ORIGINS", "").split(",")
            if origin.strip()
        ]
        allowed_methods = [
            method.strip().upper()
            for method in os.getenv("API_CORS_ALLOW_METHODS", "GET,HEAD,OPTIONS").split(
                ","
            )
            if method.strip()
        ]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_methods=allowed_methods,
            allow_headers=["*"],
            allow_credentials=True,
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origin_regex=".*",
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
        )

    # Router grouping all REST endpoints under /v1
    router = APIRouter()

    @router.get("/tickets", response_model=list[CleanTicketDTO])
    async def tickets(response: Response) -> list[CleanTicketDTO]:  # noqa: F401
        return await load_and_translate_tickets(
            client=client, cache=cache, response=response
        )

    @router.get(
        "/tickets/stream",
        response_model=list[CleanTicketDTO],
    )
    async def tickets_stream(response: Response) -> StreamingResponse:  # noqa: F401
        """Stream Server‑Sent Events with progress and final ticket list."""

        return StreamingResponse(
            stream_tickets(client, cache=cache, response=response),
            media_type="text/event-stream",
            headers=response.headers,
        )

    router.add_api_route(
        "/metrics/summary",
        metrics_summary,
        methods=["GET"],
        response_model=MetricsSummary,
    )

    @router.get("/breaker")
    async def breaker_metrics() -> Response:  # noqa: F401
        """Expose Prometheus metrics for the circuit breaker."""
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    @router.get("/metrics/aggregated")
    async def metrics_aggregated() -> dict:  # noqa: F401
        metrics = await get_cached_aggregated(cache, "metrics_aggregated")
        if metrics is None:
            df = await load_tickets(client=client, cache=cache)
            metrics = compute_aggregated(df)
            await cache.set("metrics_aggregated", metrics)
        return metrics

    @router.get("/metrics/levels")
    async def metrics_levels() -> Dict[str, Dict[str, int]]:  # noqa: F401
        """Return status counts grouped by ticket level (group)."""
        cache_key = "metrics:levels:all"
        data = await cache.get(cache_key)
        if data is None:
            data = await get_status_totals_by_levels(GROUP_IDS)
            await cache.set(cache_key, data)
        return cast(Dict[str, Dict[str, int]], data)

    @router.get(
        "/chamados/por-data",
        response_model=List[ChamadoPorData],
    )
    async def chamados_por_data() -> List[Dict[str, Any]]:
        raw = await cache.get("chamados_por_data")
        if raw is None:
            raise HTTPException(status_code=503, detail="metrics not available")
        # avisa ao type checker que raw é List[Dict[str, Any]]
        return cast(List[Dict[str, Any]], raw)

    @router.get(
        "/chamados/por-dia",
        response_model=List[ChamadosPorDia],
    )
    async def chamados_por_dia() -> List[Dict[str, Any]]:
        raw = await cache.get("chamados_por_dia")
        if raw is None:
            raise HTTPException(status_code=503, detail="metrics not available")
        return cast(List[Dict[str, Any]], raw)

    @router.get("/read-model/tickets", response_model=list[TicketSummaryOut])
    async def read_model_tickets(
        limit: int = 100, offset: int = 0
    ) -> list[TicketSummaryOut]:
        """Return tickets from the local read model (materialized view)."""
        try:
            rows = await query_ticket_summary(limit=limit, offset=offset)
            return [TicketSummaryOut.model_validate(r.__dict__) for r in rows]
        except Exception as exc:
            logger.exception("Failed to query read model")
            raise HTTPException(
                status_code=503, detail="Read model is currently unavailable."
            ) from exc

    @router.get("/cache/stats")
    async def cache_stats() -> dict:  # noqa: F401
        """Return basic hit/miss statistics for the cache."""
        return cache.get_cache_metrics()

    @router.get("/knowledge-base", response_class=PlainTextResponse)
    async def knowledge_base() -> PlainTextResponse:  # noqa: F401
        """Return the contents of the configured knowledge base file."""
        try:
            content = read_file(KNOWLEDGE_BASE_FILE)
            return PlainTextResponse(content)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="knowledge base not found")
        except PermissionError as e:
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied when reading knowledge base file: {str(e)}",
            )
        except OSError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Could not read knowledge base file: {str(e)}",
            )

    @router.get("/health")
    async def health_glpi() -> UTF8JSONResponse:  # noqa: F401
        """Check GLPI connectivity and return a JSON body."""
        status = await check_glpi_connection()
        if status != 200:
            return UTF8JSONResponse(
                status_code=status,
                content={
                    "status": "error",
                    "message": "GLPI connection failed",
                },
                headers={"Cache-Control": "no-cache"},
            )
        return UTF8JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "GLPI connection successful.",
            },
            headers={"Cache-Control": "no-cache"},
        )

    @router.head("/health")
    async def health_glpi_head() -> Response:  # noqa: F401
        """Same as ``health_glpi`` but returns headers only."""
        status = await check_glpi_connection()
        return Response(status_code=status, headers={"Cache-Control": "no-cache"})

    schema = strawberry.Schema(Query)

    def get_context(request: Request) -> dict[str, Any]:
        return {"client": client, "cache": cache}

    graphql = GraphQLRouter(
        schema,
        path="/",
        context_getter=get_context,
    )
    # Register REST routes under /v1 and GraphQL under /v1/graphql
    app.include_router(router, prefix="/v1")
    app.include_router(graphql, prefix="/v1/graphql")
    return app


app: FastAPI = create_app()


def main() -> None:  # pragma: no cover - manual run
    """CLI for running the worker API."""
    parser = argparse.ArgumentParser(description="Run GLPI worker API")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
