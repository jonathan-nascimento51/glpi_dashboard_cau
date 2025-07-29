"""Update cached metrics in response to ticket events."""

from __future__ import annotations

import logging
from typing import Any, Dict

from arq import run_worker
from arq.connections import RedisSettings

from backend.adapters.factory import create_glpi_sdk
from backend.application.aggregated_metrics import (
    cache_aggregated_metrics,
    compute_aggregated,
    status_by_group,
    tickets_by_date,
    tickets_daily_totals,
)
from backend.infrastructure.glpi.normalization import process_raw
from shared.utils.redis_client import RedisClient, redis_client


async def _load_cached_tickets(cache: RedisClient) -> list[Dict[str, Any]]:
    cached = await cache.get("tickets_api")
    if cached is None:
        return []
    # Ensure the result is always a list of dicts
    if isinstance(cached, list) and all(isinstance(item, dict) for item in cached):
        return cached
    return []


async def update_metrics(ctx: Dict[str, Any], ticket: Dict[str, Any]) -> None:
    """Update the Redis read model using a single ticket payload."""

    cache: RedisClient = ctx.get("cache") or redis_client
    tickets = await _load_cached_tickets(cache)

    updated = False
    ticket_id = ticket.get("id")
    for existing in tickets:
        if existing.get("id") == ticket_id:
            existing.update(ticket)
            updated = True
            break
    if not updated:
        tickets.append(ticket)

    await cache.set("tickets_api", tickets)

    df = process_raw(tickets)
    metrics = compute_aggregated(df)
    await cache_aggregated_metrics(cache, "metrics_aggregated", metrics)

    sdk = create_glpi_sdk()
    if sdk is not None:
        try:
            groups = df.get("group")
            level_values = []
            if groups is not None:
                level_values = [str(v) for v in groups.dropna().unique() if v]
            levels = {lvl: lvl for lvl in level_values}
            counts = sdk.get_ticket_counts_by_level("groups_id_assign", levels)
            await cache.set("metrics_levels", counts)
        except (
            ConnectionError,
            TimeoutError,
            RuntimeError,  # Replace with specific SDK-related exceptions if applicable
        ) as exc:  # pragma: no cover - network failures
            logging.error("failed to fetch counts via SDK: %s", exc)
            await cache.set("metrics_levels", status_by_group(df))
    else:
        await cache.set("metrics_levels", status_by_group(df))
    await cache.set(
        "chamados_por_data", tickets_by_date(df).to_dict(orient="records")
    )  # Key for /chamados/por-data
    await cache.set(
        "chamados_por_dia", tickets_daily_totals(df).to_dict(orient="records")
    )


async def startup(
    ctx: dict[str, Any],
) -> None:  # pragma: no cover - used by ARQ
    ctx["cache"] = redis_client


async def shutdown(
    ctx: dict[str, Any],
) -> None:  # pragma: no cover - used by ARQ
    cache: RedisClient | None = ctx.get("cache")
    if cache is not None and hasattr(cache, "close"):
        await cache.close()


class WorkerSettings:  # pragma: no cover - used by ``run_worker``
    redis_settings = RedisSettings()
    functions = [update_metrics]
    cron_jobs: list = []
    on_startup = startup
    on_shutdown = shutdown
    ctx: dict[str, Any] = {}


def main() -> None:  # pragma: no cover - manual run
    """CLI for running the worker API."""
    run_worker(WorkerSettings())
