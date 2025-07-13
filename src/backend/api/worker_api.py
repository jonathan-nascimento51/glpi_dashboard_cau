"""FastAPI service exposing GLPI tickets via REST and GraphQL."""

from __future__ import annotations

import argparse
import contextlib
import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional, cast

import pandas as pd
import strawberry
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    JSONResponse,
    ORJSONResponse,
    PlainTextResponse,
    StreamingResponse,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from pydantic import BaseModel, Field
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from backend.application.aggregated_metrics import (
    get_cached_aggregated,
)
from backend.application.glpi_api_client import (
    GlpiApiClient,
    create_glpi_api_client,
)
from backend.application.read_model import query_ticket_summary
from backend.application.ticket_loader import (
    check_glpi_connection,
    load_and_translate_tickets,
    load_tickets,
    stream_tickets,
)
from backend.core.settings import (
    KNOWLEDGE_BASE_FILE,
)
from backend.domain import CleanTicketDTO
from shared.utils.redis_client import redis_client

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


class TicketSummaryOut(BaseModel):
    """Row from the materialized view used as read model."""

    ticket_id: int
    status: str
    priority: str
    group_name: str
    opened_at: str


@strawberry.type
class Query:
    @strawberry.field
    async def tickets(self, info: Info) -> List[Ticket]:  # pragma: no cover
        df = await load_tickets(
            client=info.context.get("client"), cache=info.context.get("cache")
        )
        records = df.astype(object).where(pd.notna(df), None).to_dict("records")
        return [Ticket(**{str(k): v for k, v in r.items()}) for r in records]

    @strawberry.field
    async def metrics(self, info: Info) -> Metrics:
        df = await load_tickets(
            client=info.context.get("client"), cache=info.context.get("cache")
        )
        total = len(df)
        closed = 0
        if "status" in df:
            status_series = df["status"].astype(str).str.lower()
            closed = df[status_series.isin(["closed", "solved"])].shape[0]
        opened = total - closed
        return Metrics(
            total=total,
            opened=opened,
            closed=closed,
        )  # type: ignore[call-arg]


def create_app(client: Optional[GlpiApiClient] = None, cache=None) -> FastAPI:
    """Create FastAPI app with REST and GraphQL routes."""
    cache = cache or redis_client
    app = FastAPI(title="GLPI Worker API", default_response_class=ORJSONResponse)
    FastAPIInstrumentor().instrument_app(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # or restrict as needed
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
        client = create_glpi_api_client()

    @app.get("/tickets", response_model=list[CleanTicketDTO])
    async def tickets(response: Response) -> list[CleanTicketDTO]:  # noqa: F401
        return await load_and_translate_tickets(
            client=client, cache=cache, response=response
        )

    @app.get("/tickets/stream")
    async def tickets_stream(response: Response) -> StreamingResponse:  # noqa: F401
        return StreamingResponse(
            stream_tickets(client, cache=cache, response=response),
            media_type="text/plain",
            headers=response.headers,
        )

    @app.get("/metrics")
    async def metrics(response: Response) -> dict:  # noqa: F401
        df = await load_tickets(client=client, cache=cache, response=response)
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
        response_model=List[ChamadoPorData],
    )
    async def chamados_por_data() -> List[Dict[str, Any]]:
        raw = await cache.get("chamados_por_data")
        if raw is None:
            raise HTTPException(status_code=503, detail="metrics not available")
        # avisa ao type checker que raw é List[Dict[str, Any]]
        return cast(List[Dict[str, Any]], raw)

    @app.get(
        "/chamados/por-dia",
        response_model=List[ChamadosPorDia],
    )
    async def chamados_por_dia() -> List[Dict[str, Any]]:
        raw = await cache.get("chamados_por_dia")
        if raw is None:
            raise HTTPException(status_code=503, detail="metrics not available")
        return cast(List[Dict[str, Any]], raw)

    @app.get("/read-model/tickets", response_model=list[TicketSummaryOut])
    async def read_model_tickets(
        limit: int = 100, offset: int = 0
    ) -> list[TicketSummaryOut]:  # noqa: F401
        rows = await query_ticket_summary(limit=limit, offset=offset)
        return [TicketSummaryOut.model_validate(r.__dict__) for r in rows]

    @app.get("/cache/stats")
    async def cache_stats() -> dict:  # noqa: F401
        return cache.get_cache_metrics()

    @app.get("/cache-metrics")  # legacy name
    async def cache_metrics() -> dict:  # noqa: F401
        return cache.get_cache_metrics()

    @app.get("/knowledge-base", response_class=PlainTextResponse)
    async def knowledge_base() -> PlainTextResponse:  # noqa: F401
        """Return the contents of the configured knowledge base file."""
        try:
            with open(KNOWLEDGE_BASE_FILE, "r", encoding="utf-8") as fh:
                return PlainTextResponse(fh.read())
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="knowledge base not found")

    async def _check_glpi() -> int:
        """Return HTTP status based on GLPI connectivity."""
        return await check_glpi_connection()

    @app.get("/health/glpi")
    async def health_glpi() -> JSONResponse:  # noqa: F401
        """Check GLPI connectivity and return a JSON body."""
        status = await _check_glpi()
        if status != 200:
            return JSONResponse(
                status_code=status,
                content={
                    "status": "error",
                    "message": "GLPI connection failed",
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

    @app.head("/health/glpi")
    async def health_glpi_head() -> Response:  # noqa: F401
        """Same as ``health_glpi`` but returns headers only."""
        status = await _check_glpi()
        return Response(status_code=status, headers={"Cache-Control": "no-cache"})

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


app: FastAPI | None = None


def main() -> None:  # pragma: no cover - manual run
    """CLI for running the worker API."""
    parser = argparse.ArgumentParser(description="Run GLPI worker API")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    args = parser.parse_args()

    global app
    if app is None:
        app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
