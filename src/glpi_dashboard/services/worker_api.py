"""FastAPI service exposing GLPI tickets via REST and GraphQL."""

from __future__ import annotations

import argparse
import json
from typing import List, Optional, AsyncGenerator

import pandas as pd
import strawberry
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
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
from glpi_dashboard.services.glpi_session import Credentials, GLPISession
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


async def _load_tickets(client: Optional[GLPISession] = None) -> pd.DataFrame:
    """Return processed ticket data from the API with caching."""
    cache_key = "tickets_api"
    cached = redis_client.get(cache_key)
    if cached is not None:
        try:
            # Extract the actual ticket list if cached is a dict
            data = cached.get("data", cached) if isinstance(cached, dict) else cached
            return process_raw(data)
        except (KeyError, ValueError):
            return pd.DataFrame(data)

    try:
        if client is None:
            creds = Credentials(
                app_token=GLPI_APP_TOKEN,
                user_token=GLPI_USER_TOKEN,
                username=GLPI_USERNAME,
                password=GLPI_PASSWORD,
            )
            client = GLPISession(GLPI_BASE_URL, creds)
        async with client as session:
            data = await session.get("search/Ticket")
    except Exception as exc:  # pragma: no cover - network errors
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if isinstance(data, dict):
        data = data.get("data", data)
    redis_client.set(cache_key, data)
    try:
        return process_raw(data)
    except (KeyError, ValueError):
        return pd.DataFrame(data)


@strawberry.type
class Query:
    @strawberry.field
    async def tickets(self, info: Info) -> List[Ticket]:  # pragma: no cover
        df = await _load_tickets(client=info.context.get("client"))
        return [
            Ticket(**{str(k): v for k, v in r.items()}) for r in df.to_dict("records")
        ]

    @strawberry.field
    async def metrics(self, info: Info) -> Metrics:
        df = await _load_tickets(client=info.context.get("client"))
        total = len(df)
        closed = 0
        if "status" in df:
            closed = df[df["status"].str.lower() == "closed"].shape[0]
        opened = total - closed
        return Metrics(total=total, opened=opened, closed=closed)


def create_app(client: Optional[GLPISession] = None) -> FastAPI:
    """Create FastAPI app with REST and GraphQL routes."""
    app = FastAPI(title="GLPI Worker API")

    @app.middleware("http")
    async def cache_tickets(request: Request, call_next):
        if request.method == "GET" and request.url.path == "/tickets":
            cached = redis_client.get("resp:tickets")
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
                try:
                    data = json.loads(body.decode())
                    redis_client.set("resp:tickets", data)
                except json.JSONDecodeError:
                    pass
            return response
        return await call_next(request)

    if client is None:
        creds = Credentials(
            app_token=GLPI_APP_TOKEN,
            user_token=GLPI_USER_TOKEN,
            username=GLPI_USERNAME,
            password=GLPI_PASSWORD,
        )
        client = GLPISession(GLPI_BASE_URL, creds)

    @app.get("/tickets")
    async def tickets() -> list[dict]:
        df = await _load_tickets(client=client)
        return df.to_dict(orient="records")

    @app.get("/metrics")
    async def metrics() -> dict:
        df = await _load_tickets(client=client)
        total = len(df)
        closed = 0
        if "status" in df:
            closed = df[df["status"].str.lower() == "closed"].shape[0]
        opened = total - closed
        return {"total": total, "opened": opened, "closed": closed}

    @app.get("/cache/stats")
    async def cache_stats() -> dict:
        return redis_client.get_cache_metrics()

    @app.get("/cache-metrics")  # legacy name
    async def cache_metrics() -> dict:
        return redis_client.get_cache_metrics()

    schema = strawberry.Schema(Query)
    graphql = GraphQLRouter(
        schema,
        path="/",
        context_getter=lambda r: {"client": client},
    )
    app.include_router(graphql, prefix="/graphql")
    return app


def main() -> None:  # pragma: no cover - manual run
    """CLI for running the worker API."""
    parser = argparse.ArgumentParser(description="Run GLPI worker API")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    args = parser.parse_args()

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
