"""Update cached metrics in response to ticket events."""

from __future__ import annotations

from typing import Any, Dict, Optional

from arq import run_worker
from arq.connections import RedisSettings

from glpi_dashboard.acl import process_raw
from glpi_dashboard.services.aggregated_metrics import (
    cache_aggregated_metrics,
    compute_aggregated,
    tickets_by_date,
    tickets_daily_totals,
)
from glpi_dashboard.utils.redis_client import RedisClient, redis_client


async def _load_cached_tickets(cache: RedisClient) -> list[Dict[str, Any]]:
    cached = await cache.get("tickets_api")
    if cached is None:
        return []
    return list(cached)


async def update_metrics(
    ticket: Dict[str, Any], cache: Optional[RedisClient] = None
) -> None:
    """Update the Redis read model using a single ticket payload."""

    cache = cache or redis_client
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
    await cache.set("chamados_por_data", tickets_by_date(df).to_dict(orient="records"))
    await cache.set(
        "chamados_por_dia", tickets_daily_totals(df).to_dict(orient="records")
    )


async def startup(
    ctx: dict[str, RedisClient],
) -> None:  # pragma: no cover - used by ARQ
    ctx["cache"] = redis_client


class WorkerSettings:  # pragma: no cover - used by ``run_worker``
    redis_settings = RedisSettings()
    functions = [update_metrics]
    cron_jobs: list = []
    on_startup = startup
    ctx: dict[str, RedisClient] = {}


def main() -> None:  # pragma: no cover - manual run
    run_worker(WorkerSettings)


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
