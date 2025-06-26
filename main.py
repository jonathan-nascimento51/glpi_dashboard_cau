"""Offline Dash app using JSON dump."""

import json
import asyncio
from pathlib import Path

import pandas as pd
from dash import Dash
from flask import Flask
from flask_compress import Compress

from config import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
    USE_MOCK,
)
from data_pipeline import process_raw
from glpi_session import Credentials, GLPISession
from mock_loader import load_mock_data
from dash_layout import build_layout, register_callbacks


DATA_FILE = Path("mock/sample_data.json")


async def _fetch_api_data() -> pd.DataFrame:
    """Fetch ticket data directly from the GLPI API."""
    creds = Credentials(
        app_token=GLPI_APP_TOKEN,
        user_token=GLPI_USER_TOKEN,
        username=GLPI_USERNAME,
        password=GLPI_PASSWORD,
    )
    async with GLPISession(GLPI_BASE_URL, creds) as client:
        data = await client.get("search/Ticket")
    return process_raw(data.get("data", data))


def load_data(path: Path = DATA_FILE) -> pd.DataFrame:
    """Load ticket data from JSON or the API depending on USE_MOCK."""
    if USE_MOCK:
        return load_mock_data(path)
    return asyncio.run(_fetch_api_data())


def create_app(df: pd.DataFrame) -> Dash:
    """Create Dash application with Gzip compression."""
    server = Flask(__name__)
    Compress(server)
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
    app.run(debug=True)
