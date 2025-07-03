"""FastAPI service exposing GLPI tickets via REST and GraphQL."""


from __future__ import annotations

import argparse
import asyncio
import contextlib
import json
from typing import List, Optional, AsyncGenerator

import pandas as pd
import strawberry
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from ..config.settings import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
)
from glpi_dashboard.data.pipeline import process_raw
from glpi_dashboard.services.glpi_api_client import GlpiApiClient
from glpi_dashboard.services.glpi_session import Credentials, GLPISession
from glpi_dashboard.services.exceptions import GLPIAPIError, GLPIUnauthorizedError
from glpi_dashboard.utils.redis_client import redis_client


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


async def _load_tickets(client: Optional[GlpiApiClient] = None) -> pd.DataFrame:
    """Return processed ticket data from the API with caching."""
    cache_key = "tickets_api"
    cached = await redis_client.get(cache_key)
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
    await redis_client.set(cache_key, data)
    try:
        return process_raw(data)
    except (KeyError, ValueError):
        return pd.DataFrame(data)


async def _stream_tickets(client: Optional[GlpiApiClient]) -> AsyncGenerator[bytes, None]:
    """Yield progress events followed by final ticket data."""
    yield b"fetching...\n"
    df = await _load_tickets(client=client)
    yield b"processing...\n"
    data = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")
    yield json.dumps(data).encode()


@strawberry.type
class Query:
    @strawberry.field
    async def tickets(self, info: Info) -> List[Ticket]:  # pragma: no cover
        df = await _load_tickets(client=info.context.get("client"))
        records = df.astype(object).where(pd.notna(df), None).to_dict("records")
        return [Ticket(**{str(k): v for k, v in r.items()}) for r in records]

    @strawberry.field
    async def metrics(self, info: Info) -> Metrics:
        df = await _load_tickets(client=info.context.get("client"))
        total = len(df)
        closed = 0
        if "status" in df:
            status_series = df["status"].astype(str).str.lower()
            closed = df[status_series == "closed"].shape[0]
        opened = total - closed
        return Metrics(total=total, opened=opened, closed=closed)


def create_app(client: Optional[GlpiApiClient] = None) -> FastAPI:
    """Create FastAPI app with REST and GraphQL routes."""
    app = FastAPI(title="GLPI Worker API")

    @app.middleware("http")
    async def cache_tickets(request: Request, call_next):  # noqa: F401
        if request.method != "GET" or request.url.path != "/tickets":
            return await call_next(request)

        cached = await redis_client.get("resp:tickets")
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
                await redis_client.set("resp:tickets", data)
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

    @app.get("/tickets")
    async def tickets() -> list[dict]:  # noqa: F401
        df = await _load_tickets(client=client)
        return df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

    @app.get("/tickets/stream")
    async def tickets_stream() -> StreamingResponse:  # noqa: F401
        return StreamingResponse(_stream_tickets(client), media_type="text/plain")

    @app.get("/metrics")
    async def metrics() -> dict:  # noqa: F401
        df = await _load_tickets(client=client)
        total = len(df)
        closed = 0
        if "status" in df:
            status_series = df["status"].astype(str).str.lower()
            closed = df[status_series == "closed"].shape[0]
        opened = total - closed
        return {"total": total, "opened": opened, "closed": closed}

    @app.get("/cache/stats")
    async def cache_stats() -> dict:  # noqa: F401
        return redis_client.get_cache_metrics()

    @app.get("/cache-metrics")  # legacy name
    async def cache_metrics() -> dict:  # noqa: F401
        return redis_client.get_cache_metrics()

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
    graphql = GraphQLRouter(
        schema,
        path="/",
        context_getter=lambda _request: {"client": client},  # noqa: ARG005
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
