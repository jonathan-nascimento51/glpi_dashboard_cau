from __future__ import annotations

import contextlib
import json
import logging
from typing import AsyncGenerator, List, Optional

import pandas as pd
from fastapi import HTTPException
from fastapi.responses import Response

from backend.adapters.factory import create_glpi_session
from backend.application.aggregated_metrics import (
    cache_aggregated_metrics,
    compute_aggregated,
    tickets_by_date,
    tickets_daily_totals,
)
from backend.application.glpi_api_client import GlpiApiClient
from backend.core.settings import MOCK_TICKETS_FILE, USE_MOCK_DATA
from backend.infrastructure.glpi.normalization import process_raw
from shared.dto import CleanTicketDTO
from shared.utils.redis_client import redis_client

logger = logging.getLogger(__name__)


async def load_and_translate_tickets(
    client: Optional[GlpiApiClient] = None,
    cache=None,
    response: Optional[Response] = None,
) -> List[CleanTicketDTO]:
    """Return tickets translated using :class:`GlpiApiClient`."""

    cache = cache or redis_client
    cache_key = "tickets_clean"

    cached = await cache.get(cache_key)
    if cached is not None:
        with contextlib.suppress(Exception):
            data = cached.get("data", cached)
            return [CleanTicketDTO.model_validate(d) for d in data]

    if USE_MOCK_DATA or client is None:
        df = await load_tickets(client=client, cache=cache, response=response)
        records = df.astype(object).where(pd.notna(df), None).to_dict("records")
        tickets = [CleanTicketDTO.model_validate(r) for r in records]
    else:
        try:
            async with client:
                tickets = await client.fetch_tickets()
        except Exception as exc:  # pragma: no cover - network errors
            logger.exception("Failed to fetch from GLPI: %s", exc)
            if response is not None:
                response.headers["X-Warning"] = "using mock data"
            df = await load_tickets(client=None, cache=cache, response=response)
            records = df.astype(object).where(pd.notna(df), None).to_dict("records")
            for rec in records:
                rec.setdefault("priority", 0)
                status = rec.get("status")
                if isinstance(status, str) and not status.isdigit():
                    rec["status"] = 0
            tickets = [CleanTicketDTO.model_validate(r) for r in records]

    await cache.set(cache_key, {"data": [t.model_dump() for t in tickets]})
    return tickets


async def load_tickets(
    client: Optional[GlpiApiClient] = None,
    cache=None,
    response: Optional[Response] = None,
) -> pd.DataFrame:
    """Return processed ticket data from the API with caching."""

    cache = cache or redis_client
    cache_key = "tickets_clean"
    cached = await cache.get(cache_key)
    if cached is not None:
        try:
            data = cached.get("data", cached)
            df = pd.DataFrame(data)
            if "created_at" in df.columns:
                df["date_creation"] = pd.to_datetime(df["created_at"])
            return df
        except Exception:
            return pd.DataFrame(cached)

    if USE_MOCK_DATA or client is None:
        try:
            with open(MOCK_TICKETS_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as exc:  # pragma: no cover - file errors
            logger.error("Failed to load mock data: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        df = process_raw(data)
        metrics = compute_aggregated(df)
        await cache_aggregated_metrics(cache, "metrics_aggregated", metrics)
        await cache.set(
            "chamados_por_data", tickets_by_date(df).to_dict(orient="records")
        )
        await cache.set(
            "chamados_por_dia", tickets_daily_totals(df).to_dict(orient="records")
        )
        await cache.set(cache_key, {"data": df.to_dict(orient="records")})
        return df

    try:
        async with client:
            tickets = await client.fetch_tickets()
        data = [t.model_dump() for t in tickets]
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
        df = process_raw(data)
        metrics = compute_aggregated(df)
        await cache_aggregated_metrics(cache, "metrics_aggregated", metrics)
        await cache.set(
            "chamados_por_data", tickets_by_date(df).to_dict(orient="records")
        )
        await cache.set(
            "chamados_por_dia", tickets_daily_totals(df).to_dict(orient="records")
        )
        await cache.set(cache_key, {"data": df.to_dict(orient="records")})
        return df

    df = pd.DataFrame(data)
    if "created_at" in df.columns:
        df["date_creation"] = pd.to_datetime(df["created_at"])
    metrics = compute_aggregated(df)
    await cache_aggregated_metrics(cache, "metrics_aggregated", metrics)
    await cache.set("chamados_por_data", tickets_by_date(df).to_dict(orient="records"))
    await cache.set(
        "chamados_por_dia", tickets_daily_totals(df).to_dict(orient="records")
    )
    await cache.set(cache_key, {"data": data})
    return df


async def stream_tickets(
    client: Optional[GlpiApiClient],
    cache=None,
    response: Optional[Response] = None,
) -> AsyncGenerator[bytes, None]:
    """Yield progress events followed by final ticket data."""

    yield b"fetching...\n"
    df = await load_tickets(client=client, cache=cache, response=response)
    yield b"processing...\n"
    data = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")
    yield json.dumps(data).encode()


async def check_glpi_connection() -> int:
    """Return HTTP status based on GLPI connectivity."""

    if USE_MOCK_DATA:
        return 200

    session = create_glpi_session()
    if session is None:
        return 500

    try:
        async with session:
            pass
    except Exception:
        return 500
    return 200
