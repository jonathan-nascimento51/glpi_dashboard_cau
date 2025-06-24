"""FastAPI service exposing GLPI tickets via REST and GraphQL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

import pandas as pd
from fastapi import FastAPI, HTTPException
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
import uvicorn

from glpi_api import get_tickets
from data_pipeline import process_raw

DEFAULT_FILE = Path("mock/sample_data.json")


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


def _load_tickets(use_api: bool, data_file: Path) -> pd.DataFrame:
    """Return processed ticket data from API or JSON file."""
    if use_api:
        try:
            data = get_tickets()
        except Exception as exc:  # pragma: no cover - network errors
            raise HTTPException(status_code=500, detail=str(exc)) from exc
    else:
        with data_file.open() as f:
            data = json.load(f)
    return process_raw(data)


@strawberry.type
class Query:
    @strawberry.field
    def tickets(
        self, info: Info
    ) -> List[Ticket]:  # pragma: no cover - simple wrapper
        df = _load_tickets(info.context["use_api"], info.context["data_file"])
        return [Ticket(**r) for r in df.to_dict("records")]

    @strawberry.field
    def metrics(self, info: Info) -> Metrics:
        df = _load_tickets(info.context["use_api"], info.context["data_file"])
        total = len(df)
        closed = df[df["status"].str.lower() == "closed"].shape[0]
        opened = total - closed
        return Metrics(total=total, opened=opened, closed=closed)


def create_app(
    use_api: bool = False, data_file: Path = DEFAULT_FILE
) -> FastAPI:
    """Create FastAPI app with REST and GraphQL routes."""
    app = FastAPI(title="GLPI Worker API")

    @app.get("/tickets")
    def tickets() -> list[dict]:
        df = _load_tickets(use_api, data_file)
        return df.to_dict(orient="records")

    @app.get("/metrics")
    def metrics() -> dict:
        df = _load_tickets(use_api, data_file)
        total = len(df)
        closed = df[df["status"].str.lower() == "closed"].shape[0]
        opened = total - closed
        return {"total": total, "opened": opened, "closed": closed}

    schema = strawberry.Schema(Query)
    graphql = GraphQLRouter(
        schema,
        path="/",
        context_getter=lambda r: {"use_api": use_api, "data_file": data_file},
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
        "--file", type=Path, default=DEFAULT_FILE, help="Path to JSON dump"
    )
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    args = parser.parse_args()

    app = create_app(use_api=args.use_api, data_file=args.file)
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()

"""FastAPI service exposing GLPI tickets via REST and GraphQL."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pandas as pd
from fastapi import FastAPI, HTTPException
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
import uvicorn

from glpi_api import get_tickets
from data_pipeline import process_raw

DATA_FILE = Path("mock/sample_data.json")


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


def _load_tickets(use_api: bool) -> pd.DataFrame:
    """Return processed ticket data from API or JSON."""
    if use_api:
        try:
            data = get_tickets()
        except Exception as exc:  # pragma: no cover - network errors
            raise HTTPException(status_code=500, detail=str(exc)) from exc
    else:
        with DATA_FILE.open() as f:
            data = json.load(f)
    return process_raw(data)


@strawberry.type
class Query:
    @strawberry.field
    def tickets(self, info: Info) -> List[Ticket]:  # pragma: no cover - simple wrapper
        df = _load_tickets(info.context["use_api"])
        return [Ticket(**r) for r in df.to_dict("records")]

    @strawberry.field
    def metrics(self, info: Info) -> Metrics:
        df = _load_tickets(info.context["use_api"])
        total = len(df)
        closed = df[df["status"].str.lower() == "closed"].shape[0]
        opened = total - closed
        return Metrics(total=total, opened=opened, closed=closed)


def create_app(use_api: bool = False) -> FastAPI:
    """Create FastAPI app with REST and GraphQL routes."""
    app = FastAPI(title="GLPI Worker API")

    @app.get("/tickets")
    def tickets() -> list[dict]:
        df = _load_tickets(use_api)
        return df.to_dict(orient="records")

    @app.get("/metrics")
    def metrics() -> dict:
        df = _load_tickets(use_api)
        total = len(df)
        closed = df[df["status"].str.lower() == "closed"].shape[0]
        opened = total - closed
        return {"total": total, "opened": opened, "closed": closed}

    schema = strawberry.Schema(Query)
    graphql = GraphQLRouter(schema, context_getter=lambda r: {"use_api": use_api})
    app.include_router(graphql, prefix="/graphql")
    return app


if __name__ == "__main__":  # pragma: no cover - manual run
    uvicorn.run(create_app(), host="0.0.0.0", port=8000)
