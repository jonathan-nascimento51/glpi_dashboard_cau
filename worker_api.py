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
