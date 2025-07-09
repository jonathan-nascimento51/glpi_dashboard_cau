from __future__ import annotations

import contextlib
import json
import logging
from typing import AsyncGenerator, List, Optional

import pandas as pd
from fastapi import HTTPException
from fastapi.responses import Response

from backend.adapters.factory import create_glpi_session
from backend.adapters.glpi_session import GLPISession
from backend.adapters.normalization import process_raw
from backend.core.settings import MOCK_TICKETS_FILE, USE_MOCK_DATA
from backend.services.aggregated_metrics import (
    cache_aggregated_metrics,
    compute_aggregated,
    tickets_by_date,
    tickets_daily_totals,
)
from backend.utils.redis_client import redis_client
from shared.dto import CleanTicketDTO, TicketTranslator

logger = logging.getLogger(__name__)


async def load_and_translate_tickets(
    translator: Optional[TicketTranslator],
    cache=None,
    response: Optional[Response] = None,
) -> List[CleanTicketDTO]:
    """Return a list of ``CleanTicketDTO`` using the ACL pipeline."""

    if USE_MOCK_DATA or translator is None:
        df = await load_tickets(cache=cache, response=response)
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


async def load_tickets(
    client: Optional[GLPISession] = None,
    cache=None,
    response: Optional[Response] = None,
) -> pd.DataFrame:
    """Return processed ticket data from the API with caching."""

    cache = cache or redis_client
    cache_key = "tickets_api"
    cached = await cache.get(cache_key)
    if cached is not None:
        try:
            data = cached.get("data", cached) if isinstance(cached, dict) else cached
            return process_raw(data)
        except (KeyError, ValueError):
            return pd.DataFrame(data)

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

    session_created = False
    if client is None:
        client = create_glpi_session()
        session_created = True

    async def _fetch(sess: GLPISession) -> list[dict]:
        async with sess:
            return await sess.get_all("Ticket")

    try:
        data = await _fetch(client) if client else []
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
    finally:
        if session_created and client is not None:
            await client.__aexit__(None, None, None)

    if isinstance(data, dict):
        data = data.get("data", data)
    await cache.set(cache_key, {"data": data})
    try:
        return process_raw(data)
    except (KeyError, ValueError):
        return pd.DataFrame(data)


async def stream_tickets(
    client: Optional[GLPISession],
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

    session = create_glpi_session()
    if session is None:
        return 500

    try:
        async with session:
            pass
    except Exception:
        return 500
    return 200
