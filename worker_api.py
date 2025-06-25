"""FastAPI service exposing GLPI tickets via REST and GraphQL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import os
from typing import List

import pandas as pd
from fastapi import FastAPI, HTTPException
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
import uvicorn

from src.api.glpi_api import GLPIClient
from data_pipeline import process_raw


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


def _load_tickets(
    use_api: bool,
    data_file: Path,
    client: GLPIClient | None = None,
) -> pd.DataFrame:
    """Return processed ticket data from API or JSON file."""
    if use_api:
        try:
            if client is None:
                client = GLPIClient()
                client.start_session()
            data = client.search("Ticket")
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
    return process_raw(data)


@strawberry.type
class Query:
    @strawberry.field
    def tickets(self, info: Info) -> List[Ticket]:  # pragma: no cover
        df = _load_tickets(
            info.context["use_api"],
            info.context["data_file"],
            client=info.context.get("client"),
        )
        return [Ticket(**r) for r in df.to_dict("records")]

    @strawberry.field
    def metrics(self, info: Info) -> Metrics:
        df = _load_tickets(
            info.context["use_api"],
            info.context["data_file"],
            client=info.context.get("client"),
        )
        total = len(df)
        closed = df[df["status"].str.lower() == "closed"].shape[0]
        opened = total - closed
        return Metrics(total=total, opened=opened, closed=closed)


def create_app(
    use_api: bool = False,
    data_file: Path = DEFAULT_FILE,
) -> FastAPI:
    """Create FastAPI app with REST and GraphQL routes."""
    app = FastAPI(title="GLPI Worker API")

    client: GLPIClient | None = None
    if use_api:
        client = GLPIClient()
        client.start_session()

    @app.get("/tickets")
    def tickets() -> list[dict]:
        df = _load_tickets(use_api, data_file, client=client)
        return df.to_dict(orient="records")

    @app.get("/metrics")
    def metrics() -> dict:
        df = _load_tickets(use_api, data_file, client=client)
        total = len(df)
        closed = df[df["status"].str.lower() == "closed"].shape[0]
        opened = total - closed
        return {"total": total, "opened": opened, "closed": closed}

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
