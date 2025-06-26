"""FastAPI service exposing GLPI tickets via REST and GraphQL."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import List, Optional

import pandas as pd
import strawberry
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from config import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
)
from data_pipeline import process_raw
from glpi_session import Credentials, GLPISession
from redis_client import redis_client

DEFAULT_FILE = Path(os.getenv("KNOWLEDGE_BASE_FILE", "mock/sample_data.json"))


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


async def _load_tickets(
    use_api: bool,
    data_file: Path,
    client: Optional[GLPISession] = None,
) -> pd.DataFrame:
    """Return processed ticket data from API or JSON file with caching."""
    cache_key = "tickets_api" if use_api else f"tickets_file:{data_file}"
    cached = redis_client.get(cache_key)
    if cached is not None:
        try:
            return process_raw(cached)
        except KeyError:
            return pd.DataFrame(cached)

    if use_api:
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
    else:
        try:
            with data_file.open() as f:
                data = json.load(f)
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=404,
                detail="File not found",
            ) from exc

    if isinstance(data, dict):
        data = data.get("data", data)
    redis_client.set(cache_key, data)
    try:
        return process_raw(data)
    except KeyError:
        return pd.DataFrame(data)


@strawberry.type
class Query:
    @strawberry.field
    async def tickets(self, info: Info) -> List[Ticket]:  # pragma: no cover
        df = await _load_tickets(
            info.context["use_api"],
            info.context["data_file"],
            client=info.context.get("client"),
        )
        return [Ticket(**r) for r in df.to_dict("records")]

    @strawberry.field
    async def metrics(self, info: Info) -> Metrics:
        df = await _load_tickets(
            info.context["use_api"],
            info.context["data_file"],
            client=info.context.get("client"),
        )
        total = len(df)
        closed = 0
        if "status" in df:
            closed = df[df["status"].str.lower() == "closed"].shape[0]
        opened = total - closed
        return Metrics(total=total, opened=opened, closed=closed)


def create_app(
    use_api: bool = False,
    data_file: Path = DEFAULT_FILE,
) -> FastAPI:
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

                async def new_iter() -> bytes:
                    yield body

                response.body_iterator = new_iter()
                try:
                    data = json.loads(body.decode())
                    redis_client.set("resp:tickets", data)
                except json.JSONDecodeError:
                    pass
            return response
        return await call_next(request)

    client: Optional[GLPISession] = None
    if use_api:
        creds = Credentials(
            app_token=GLPI_APP_TOKEN,
            user_token=GLPI_USER_TOKEN,
            username=GLPI_USERNAME,
            password=GLPI_PASSWORD,
        )
        client = GLPISession(GLPI_BASE_URL, creds)

    @app.get("/tickets")
    async def tickets() -> list[dict]:
        df = await _load_tickets(use_api, data_file, client=client)
        return df.to_dict(orient="records")

    @app.get("/metrics")
    async def metrics() -> dict:
        df = await _load_tickets(use_api, data_file, client=client)
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
        context_getter=lambda r: {
            "use_api": use_api,
            "data_file": data_file,
            "client": client,
        },
    )
    app.include_router(graphql, prefix="/graphql")
    return app


def main() -> None:  # pragma: no cover - manual run
    """CLI for running the worker API."""
    parser = argparse.ArgumentParser(description="Run GLPI worker API")
    parser.add_argument(
        "--use-api",
        action="store_true",
        help="Fetch from GLPI instead of JSON dump",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_FILE,
        help="Path to JSON dump",
    )
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    args = parser.parse_args()

    app = create_app(use_api=args.use_api, data_file=args.file)
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
