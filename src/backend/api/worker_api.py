"""FastAPI service exposing GLPI tickets via REST and GraphQL."""

from __future__ import annotations

import argparse
import contextlib
import json
import logging
import os
from typing import Any, AsyncGenerator, Dict, List, Optional, cast

import pandas as pd
import strawberry
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    JSONResponse,
    ORJSONResponse,
    PlainTextResponse,
    StreamingResponse,
)
from pydantic import BaseModel, Field
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from backend.adapters.dto import CleanTicketDTO, TicketTranslator
from backend.adapters.glpi_session import Credentials, GLPISession
from backend.adapters.mapping_service import MappingService
from backend.adapters.normalization import process_raw
from backend.services.aggregated_metrics import (
    cache_aggregated_metrics,
    compute_aggregated,
    get_cached_aggregated,
    tickets_by_date,
    tickets_daily_totals,
)
from backend.services.exceptions import (
    GLPIAPIError,
    GLPIUnauthorizedError,
)
from backend.services.read_model import query_ticket_summary
from backend.utils.redis_client import redis_client

from ..config.settings import (
    CLIENT_TIMEOUT_SECONDS,
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
    KNOWLEDGE_BASE_FILE,
    USE_MOCK_DATA,
    VERIFY_SSL,
)

logger = logging.getLogger(__name__)

MOCK_TICKETS_FILE = os.getenv("MOCK_TICKETS_FILE", "data/mock_tickets.json")


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


def get_ticket_translator() -> Optional[TicketTranslator]:
    """Instantiate :class:`TicketTranslator` unless using mock data."""

    if USE_MOCK_DATA:
        return None

    try:
        creds = Credentials(
            app_token=GLPI_APP_TOKEN,
            user_token=GLPI_USER_TOKEN,
            username=GLPI_USERNAME,
            password=GLPI_PASSWORD,
        )
        session = GLPISession(
            GLPI_BASE_URL,
            creds,
            verify_ssl=VERIFY_SSL,
            timeout=CLIENT_TIMEOUT_SECONDS,
        )
    except Exception as exc:  # pragma: no cover - init failures
        logger.exception("GLPI session init failed: %s", exc)
        return None

    mapper = MappingService(session)
    return TicketTranslator(mapper)


async def _load_and_translate_tickets(
    translator: Optional[TicketTranslator],
    cache=None,
    response: Optional[Response] = None,
) -> List[CleanTicketDTO]:
    """Return a list of ``CleanTicketDTO`` using the ACL pipeline."""

    # Offline mode bypasses translator and GLPI session
    if USE_MOCK_DATA or translator is None:
        df = await _load_tickets(cache=cache, response=response)
        records = df.astype(object).where(pd.notna(df), None).to_dict("records")
        return [CleanTicketDTO.model_validate(r) for r in records]

    cache = cache or redis_client
    cache_key = "tickets_clean"

    cached = await cache.get(cache_key)
    if cached is not None:
        with contextlib.suppress(Exception):
            return [CleanTicketDTO.model_validate(d) for d in cached]
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

    await cache.set(cache_key, {"data": [t.model_dump() for t in translated]})
    return translated


async def _load_tickets(
    client: Optional[GLPISession] = None,
    cache=None,
    response: Optional[Response] = None,
) -> pd.DataFrame:
    """Return processed ticket data from the API with caching.

    When the GLPI session fails to initialize the function falls back to the
    local mock dataset and sets a warning header on ``response`` if provided.
    """
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

    # In offline mode load tickets from a local JSON file
    if USE_MOCK_DATA:
        try:
            with open(MOCK_TICKETS_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as exc:  # pragma: no cover - file errors
            logger.error("Failed to load mock data: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        await cache.set(cache_key, data)
        df = process_raw(data)
        metrics = compute_aggregated(df)
        await cache_aggregated_metrics(cache, "metrics_aggregated", metrics)
        await cache.set(
            "chamados_por_data", {"data": tickets_by_date(df).to_dict(orient="records")}
        )
        await cache.set(
            "chamados_por_dia",
            {"data": tickets_daily_totals(df).to_dict(orient="records")},
        )
        return df

    async def _async_fetch() -> list[dict]:
        creds = Credentials(
            app_token=GLPI_APP_TOKEN,
            user_token=GLPI_USER_TOKEN,
            username=GLPI_USERNAME,
            password=GLPI_PASSWORD,
        )
        async with GLPISession(
            GLPI_BASE_URL,
            creds,
            verify_ssl=VERIFY_SSL,
            timeout=CLIENT_TIMEOUT_SECONDS,
        ) as session:
            return await session.get_all("Ticket")

    try:
        if client is None:
            data = await _async_fetch()
        else:
            async with client as sess:
                data = await sess.get_all("Ticket")
    except Exception as exc:  # pragma: no cover - network errors
        logger.exception("Failed to fetch from GLPI: %s", exc)
        if response is not None:
            response.headers["X-Warning"] = "using mock data"
        try:
            with open(MOCK_TICKETS_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as file_exc:  # pragma: no cover - file errors
            logger.error("Failed to load mock data: %s", file_exc)
            raise HTTPException(status_code=500, detail=str(file_exc)) from file_exc
        await cache.set(cache_key, data)
        df = process_raw(data)
        metrics = compute_aggregated(df)
        await cache_aggregated_metrics(cache, "metrics_aggregated", metrics)
        await cache.set(
            "chamados_por_data", {"data": tickets_by_date(df).to_dict(orient="records")}
        )
        await cache.set(
            "chamados_por_dia",
            {"data": tickets_daily_totals(df).to_dict(orient="records")},
        )
        return df

    if isinstance(data, dict):
        data = data.get("data", data)
    await cache.set(cache_key, {"data": data})
    try:
        return process_raw(data)
    except (KeyError, ValueError):
        return pd.DataFrame(data)


async def _stream_tickets(
    client: Optional[GLPISession],
    cache=None,
    response: Optional[Response] = None,
) -> AsyncGenerator[bytes, None]:
    """Yield progress events followed by final ticket data."""
    yield b"fetching...\n"
    df = await _load_tickets(client=client, cache=cache, response=response)
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


def create_app(client: Optional[GLPISession] = None, cache=None) -> FastAPI:
    """Create FastAPI app with REST and GraphQL routes."""
    cache = cache or redis_client
    app = FastAPI(title="GLPI Worker API", default_response_class=ORJSONResponse)

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
        creds = Credentials(
            app_token=GLPI_APP_TOKEN,
            user_token=GLPI_USER_TOKEN,
            username=GLPI_USERNAME,
            password=GLPI_PASSWORD,
        )
        client = GLPISession(
            GLPI_BASE_URL,
            creds,
            verify_ssl=VERIFY_SSL,
            timeout=CLIENT_TIMEOUT_SECONDS,
        )

    @app.get("/tickets", response_model=list[CleanTicketDTO])
    async def tickets(
        response: Response,
        translator: Optional[TicketTranslator] = Depends(get_ticket_translator),
    ) -> list[CleanTicketDTO]:  # noqa: F401
        return await _load_and_translate_tickets(
            translator, cache=cache, response=response
        )

    @app.get("/tickets/stream")
    async def tickets_stream(response: Response) -> StreamingResponse:  # noqa: F401
        return StreamingResponse(
            _stream_tickets(client, cache=cache, response=response),
            media_type="text/plain",
            headers=response.headers,
        )

    @app.get("/metrics")
    async def metrics(response: Response) -> dict:  # noqa: F401
        df = await _load_tickets(client=client, cache=cache, response=response)
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
        creds = Credentials(
            app_token=GLPI_APP_TOKEN,
            user_token=GLPI_USER_TOKEN,
            username=GLPI_USERNAME,
            password=GLPI_PASSWORD,
        )
        try:
            async with GLPISession(
                GLPI_BASE_URL,
                creds,
                verify_ssl=VERIFY_SSL,
                timeout=CLIENT_TIMEOUT_SECONDS,
            ):
                pass
        except (GLPIAPIError, GLPIUnauthorizedError):
            return 500
        return 200

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
