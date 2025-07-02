"""Dash app using live GLPI data."""

import asyncio

import pandas as pd
from dash import Dash
from flask import Flask
import logging

from src.glpi_dashboard.config.settings import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
    USE_MOCK_DATA,
)
from src.glpi_dashboard.data.pipeline import process_raw
from src.glpi_dashboard.services.glpi_api_client import GlpiApiClient
from src.glpi_dashboard.services.exceptions import GLPIAPIError
from src.glpi_dashboard.logging_config import setup_logging
from src.glpi_dashboard.dashboard.layout import build_layout
from src.glpi_dashboard.dashboard.callbacks import register_callbacks

setup_logging()


async def _fetch_api_data() -> pd.DataFrame:
    """Fetch ticket data directly from the GLPI API."""

    def _sync_fetch() -> list[dict]:
        with GlpiApiClient(
            GLPI_BASE_URL,
            GLPI_APP_TOKEN,
            GLPI_USER_TOKEN,
            username=GLPI_USERNAME,
            password=GLPI_PASSWORD,
        ) as client:
            return client.get_all("Ticket")

    try:
        data = await asyncio.to_thread(_sync_fetch)
    except Exception as exc:  # Broad catch logs unexpected failures
        logging.error("Failed to fetch data from GLPI API: %s", exc)
        raise

    return process_raw(data)


def load_data() -> pd.DataFrame | None:
    """Load ticket data from GLPI or a local mock file."""
    if USE_MOCK_DATA:
        logging.info("Loading ticket data from mock file")
        try:
            return process_raw(pd.read_json("data/mock_tickets.json"))
        except Exception as exc:  # pragma: no cover - file errors
            logging.error("Failed to load mock data: %s", exc)
            return None

    logging.info("Fetching ticket data from GLPI API")
    try:
        return asyncio.run(_fetch_api_data())
    except GLPIAPIError as exc:
        logging.error("Error contacting GLPI API: %s", exc)
        return None


def create_app(df: pd.DataFrame | None) -> Dash:
    """Create Dash application."""
    server = Flask(__name__)

    @server.route("/ping")
    def ping() -> tuple[str, int]:
        """Simple health check endpoint."""
        return "OK", 200

    app = Dash(__name__, server=server)
    app.layout = build_layout(df)
    if df is not None:
        register_callbacks(app, df)
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


if __name__ == "__main__":
    df = load_data()
    app = create_app(df)
    import os

    port = int(os.getenv("DASH_PORT", "8050"))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False, threaded=True)
