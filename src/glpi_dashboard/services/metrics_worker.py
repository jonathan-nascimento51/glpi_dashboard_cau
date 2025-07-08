"""Background worker to pre-compute ticket metrics."""

from __future__ import annotations

import pandas as pd
from arq import cron, run_worker
from arq.connections import RedisSettings

from glpi_dashboard.acl import process_raw
from glpi_dashboard.config.settings import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
)
from glpi_dashboard.data.database import (
    insert_tickets,
    refresh_materialized_view,
)
from glpi_dashboard.services.aggregated_metrics import (
    cache_aggregated_metrics,
    compute_aggregated,
    tickets_by_date,
    tickets_daily_totals,
)
from glpi_dashboard.services.glpi_session import Credentials, GLPISession
from glpi_dashboard.utils.redis_client import RedisClient, redis_client


async def fetch_tickets() -> pd.DataFrame:
    """Retrieve and normalize tickets from GLPI."""
    creds = Credentials(
        app_token=GLPI_APP_TOKEN,
        user_token=GLPI_USER_TOKEN,
        username=GLPI_USERNAME,
        password=GLPI_PASSWORD,
    )
    async with GLPISession(GLPI_BASE_URL, creds) as session:
        data = await session.get_all("Ticket")
    if isinstance(data, dict):
        data = data.get("data", data)
    return process_raw(data)


async def update_metrics(ctx: dict[str, RedisClient]) -> None:
    """Fetch tickets, update the read model and cache aggregated metrics."""
    cache = ctx["cache"]
    df = await fetch_tickets()
    await insert_tickets(df.to_dict(orient="records"))
    await refresh_materialized_view()

    metrics = compute_aggregated(df)
    await cache_aggregated_metrics(cache, "metrics_aggregated", metrics)
    await cache.set("chamados_por_data", tickets_by_date(df).to_dict(orient="records"))
    await cache.set(
        "chamados_por_dia", tickets_daily_totals(df).to_dict(orient="records")
    )


async def startup(ctx: dict[str, RedisClient]) -> None:
    ctx["cache"] = redis_client


class WorkerSettings:
    redis_settings = RedisSettings()
    functions = [update_metrics]
    cron_jobs = [
        cron(update_metrics, minute={0, 10, 20, 30, 40, 50}, run_at_startup=True)
    ]
    on_startup = startup
    ctx: dict[str, RedisClient] = {}


def main() -> None:  # pragma: no cover - manual run
    """Entry point for running the ARQ worker."""
    run_worker(WorkerSettings)


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
