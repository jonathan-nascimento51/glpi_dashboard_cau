from __future__ import annotations

from typing import Dict, cast

from fastapi import APIRouter, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from backend.application.aggregated_metrics import get_cached_aggregated
from backend.application.ticket_loader import load_tickets
from backend.services.metrics_service import calculate_dataframe_metrics


def create_metrics_router(client, cache) -> APIRouter:
    """Return a router with metrics endpoints bound to ``client`` and ``cache``."""
    router = APIRouter()

    @router.get("/metrics/summary")
    async def metrics_summary(response: Response) -> dict:
        df = await load_tickets(client=client, cache=cache, response=response)
        return calculate_dataframe_metrics(df)

    @router.get("/metrics/aggregated")
    async def metrics_aggregated() -> dict:
        metrics = await get_cached_aggregated(cache, "metrics_aggregated")
        if metrics is None:
            raise HTTPException(status_code=503, detail="metrics not available")
        return metrics

    @router.get("/metrics/levels")
    async def metrics_levels() -> Dict[str, Dict[str, int]]:
        data = await cache.get("metrics_levels")
        if data is None:
            raise HTTPException(status_code=503, detail="metrics not available")
        return cast(Dict[str, Dict[str, int]], data)

    @router.get("/breaker")
    async def breaker_metrics() -> Response:
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    return router
