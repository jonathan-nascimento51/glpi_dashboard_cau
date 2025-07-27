"""Dash app using live GLPI data."""

import asyncio
import logging
import os

import pandas as pd
from dash import Dash
from flask import Flask
from flask_caching import Cache
from frontend.callbacks.callbacks import register_callbacks
from frontend.layout.layout import build_layout

from backend.core.settings import (
    DASH_PORT,
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
    USE_MOCK_DATA,
)
from backend.domain.exceptions import GLPIAPIError
from backend.infrastructure.glpi import glpi_client_logging
from backend.infrastructure.glpi.glpi_session import Credentials, GLPISession
from backend.utils import process_raw

__all__ = ["create_app", "main"]

flask_app = Flask(__name__)
cache_type = os.getenv("CACHE_TYPE", "redis").lower()
cache_config: dict[str, object]
if cache_type == "simple":
    cache_config = {"CACHE_TYPE": "SimpleCache"}
else:
    cache_config = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_HOST": os.getenv("REDIS_HOST", "redis"),
        "CACHE_REDIS_PORT": int(os.getenv("REDIS_PORT", 6379)),
        "CACHE_REDIS_DB": int(os.getenv("REDIS_DB", 0)),
        "CACHE_REDIS_URL": (
            f"redis://{os.getenv('REDIS_HOST', 'redis')}:"
            f"{os.getenv('REDIS_PORT', 6379)}/{os.getenv('REDIS_DB', 0)}"
        ),
    }
cache = Cache(flask_app, config=cache_config)
if cache_type != "simple":
    try:  # pragma: no cover - optional
        cache.cache.get("test_key")
    except Exception as exc:  # pragma: no cover - Redis missing
        logging.warning("Redis unavailable, falling back to SimpleCache: %s", exc)
        cache = Cache(flask_app, config={"CACHE_TYPE": "SimpleCache"})

log_level_name = os.getenv("LOG_LEVEL", "INFO")
log_level = getattr(logging, log_level_name.upper(), logging.INFO)
glpi_client_logging.init_logging(log_level)


@cache.memoize(timeout=300)
def _fetch_api_data(
    ticket_range: str = "0-99", **filters: str
) -> list[dict[str, object]]:
    """Fetch ticket data directly from the GLPI API."""

    creds = Credentials(
        app_token=GLPI_APP_TOKEN,
        user_token=GLPI_USER_TOKEN,
        username=GLPI_USERNAME,
        password=GLPI_PASSWORD,
    )

    async def _run() -> list[dict[str, object]]:
        async with GLPISession(GLPI_BASE_URL, creds) as client:
            return await client.get_all("Ticket", range=ticket_range, **filters)

    return asyncio.run(_run())


@cache.memoize(timeout=300)
def _transform_df(ticket_range: str = "0-99", **filters: str) -> pd.DataFrame:
    """Transform raw ticket data into a normalized DataFrame."""

    data = _fetch_api_data(ticket_range, **filters)
    return process_raw(data)


def clear_cache(ticket_range: str = "0-99", **filters: str) -> None:
    """Manually invalidate cached data for a given ticket range and filters."""

    cache.delete_memoized(_fetch_api_data, ticket_range, **filters)
    cache.delete_memoized(_transform_df, ticket_range, **filters)


def load_data(ticket_range: str = "0-99", **filters: str) -> pd.DataFrame | None:
    """Load ticket data from GLPI or a local mock file."""
    if USE_MOCK_DATA:
        logging.info("Loading ticket data from mock file")
        try:
            return process_raw(pd.read_json("tests/resources/mock_tickets.json"))
        except Exception as exc:  # pragma: no cover - file errors
            logging.error("failed to load mock data: %s", exc)
            return None

    logging.info("Fetching ticket data from GLPI API")
    try:
        return _transform_df(ticket_range, **filters)
    except GLPIAPIError as exc:
        logging.error("Error contacting GLPI API: %s", exc)
        return None


def create_app(df: pd.DataFrame | None) -> Dash:
    """Create Dash application."""
    server = Flask(__name__)
    cache.init_app(server)

    # @server.route("/ping")
    # def ping() -> tuple[str, int]:
    #     """Simple health check endpoint."""
    #     return "OK", 200

    app = Dash(__name__, server=server)
    app.layout = build_layout(df)
    if df is not None:
        register_callbacks(app, load_data)
    return app


def profile_startup() -> None:
    """Profile app startup using cProfile."""
    import cProfile
    from pstats import Stats

    profiler = cProfile.Profile()
    profiler.enable()
    df = load_data()
    create_app(df)
    profiler.disable()
    Stats(profiler).sort_stats("cumulative").print_stats(10)


def main() -> None:
    """Run the Dash server."""
    df = load_data()
    app = create_app(df)
    app.run(
        host="0.0.0.0", port=DASH_PORT, debug=False, use_reloader=False, threaded=True
    )


if __name__ == "__main__":
    main()
