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
)
from src.glpi_dashboard.data.pipeline import process_raw
from src.glpi_dashboard.services.glpi_session import Credentials, GLPISession
from src.glpi_dashboard.logging_config import setup_logging
from src.glpi_dashboard.dashboard.layout import build_layout
from src.glpi_dashboard.dashboard.callbacks import register_callbacks

setup_logging()


async def _fetch_api_data() -> pd.DataFrame:
    """Fetch ticket data directly from the GLPI API."""
    creds = Credentials(
        app_token=GLPI_APP_TOKEN,
        user_token=GLPI_USER_TOKEN,
        username=GLPI_USERNAME,
        password=GLPI_PASSWORD,
    )
    try:
        async with GLPISession(GLPI_BASE_URL, creds) as client:
            data = await client.get("search/Ticket")
    except Exception as exc:  # Broad catch logs unexpected failures
        logging.error("Failed to fetch data from GLPI API: %s", exc)
        raise
    return process_raw(data.get("data", data))


def load_data() -> pd.DataFrame:
    """Always fetch ticket data from the GLPI API."""
    logging.info("Fetching ticket data from GLPI API")
    return asyncio.run(_fetch_api_data())


def create_app(df: pd.DataFrame) -> Dash:
    """Create Dash application."""
    server = Flask(__name__)
    app = Dash(__name__, server=server)
    app.layout = build_layout(df)
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
