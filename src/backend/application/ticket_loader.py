from __future__ import annotations

import json
import logging
from pathlib import Path
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

PROJECT_ROOT = Path(__file__).resolve().parents[3]

logger = logging.getLogger(__name__)


async def _process_and_cache_df(
    df: pd.DataFrame, cache, cache_key: str
) -> pd.DataFrame:
    """Process a DataFrame, update derivative caches, and cache the main result."""
    if "created_at" in df.columns and "date_creation" not in df.columns:
        df["date_creation"] = pd.to_datetime(df["created_at"])

    # Create a copy to avoid modifying the original DataFrame in place
    df_to_cache = df.copy()
    # Convert datetime columns to ISO 8601 strings for JSON serialization
    for col in df_to_cache.select_dtypes(include=["datetime64[ns]"]).columns:
        df_to_cache[col] = df_to_cache[col].dt.isoformat()

    metrics = compute_aggregated(df)
    await cache_aggregated_metrics(cache, "metrics_aggregated", metrics)
    await cache.set("chamados_por_data", tickets_by_date(df).to_dict(orient="records"))
    await cache.set(
        "chamados_por_dia", tickets_daily_totals(df).to_dict(orient="records")
    )
    await cache.set(cache_key, {"data": df_to_cache.to_dict(orient="records")})
    return df


async def load_and_translate_tickets(
    client: Optional[GlpiApiClient] = None,
    cache=None,
    response: Optional[Response] = None,
) -> List[CleanTicketDTO]:
    """Return tickets translated using :class:`GlpiApiClient`."""
    df = await load_tickets(client=client, cache=cache, response=response)
    records = df.astype(object).where(pd.notna(df), None).to_dict("records")
    return [CleanTicketDTO.model_validate(r) for r in records]


async def load_tickets(
    client: Optional[GlpiApiClient] = None,
    cache=None,
    response: Optional[Response] = None,
) -> pd.DataFrame:
    """Return processed ticket data from the API with caching.

    This function implements a cache-aside pattern:
    1. Try to fetch the processed DataFrame from the cache.
    2. On a cache miss, fetch raw data from the GLPI API or a mock file.
    3. Process the raw data into a DataFrame.
    4. Populate the cache with the processed data and derived metrics.
    5. Return the DataFrame.
    """
    cache = cache or redis_client
    cache_key = "tickets_clean"
    mock_file_path = PROJECT_ROOT / MOCK_TICKETS_FILE

    cached = await cache.get(cache_key)
    if cached is not None:
        logger.debug("Cache HIT for key: %s", cache_key)
        try:
            data = cached.get("data", cached)
            df = pd.DataFrame(data)
            if "created_at" in df.columns and "date_creation" not in df.columns:
                df["date_creation"] = pd.to_datetime(df["created_at"])
            return df
        except Exception as exc:
            logger.warning("Failed to load from cache, will refetch: %s", exc)

    logger.debug("Cache MISS for key: %s", cache_key)
    data = None
    if USE_MOCK_DATA or client is None:
        if response:
            response.headers["X-Warning"] = "using mock data"
        logger.info("Loading ticket data from mock file: %s", mock_file_path)
        try:
            with open(mock_file_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as exc:  # pragma: no cover - file errors
            logger.error("Failed to load mock data: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc)) from exc
    else:
        logger.info("Fetching ticket data from GLPI API")
        try:
            async with client:
                tickets = await client.fetch_tickets()
            data = [t.model_dump() for t in tickets]
        except Exception as exc:
            logger.exception(
                "Failed to fetch from GLPI, falling back to mock data: %s", exc
            )
            if response:
                response.headers["X-Warning"] = "using mock data due to API failure"
            try:
                with open(mock_file_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
            except Exception as file_exc:
                logger.error("Failed to load mock data on fallback: %s", file_exc)
                raise HTTPException(status_code=500, detail=str(file_exc)) from file_exc

    if data is None:
        raise HTTPException(status_code=500, detail="Failed to load any ticket data")

    df = process_raw(data)
    return await _process_and_cache_df(df, cache, cache_key)


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
