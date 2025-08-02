"""Dash app using the worker API for ticket metrics."""

import logging
import os
from typing import Any

import dash_bootstrap_components as dbc
import pandas as pd
import requests
from dash import Dash
from flask import Flask
from frontend.callbacks.callbacks import register_callbacks
from frontend.layout.layout import build_layout

from backend.core.settings import DASH_PORT, USE_MOCK_DATA
from backend.infrastructure.glpi.normalization import process_raw
from shared.utils.logging import init_logging

__all__ = ["create_app", "main"]

WORKER_BASE_URL = os.getenv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000")
log_level_name = os.getenv("LOG_LEVEL", "INFO")
log_level = getattr(logging, log_level_name.upper(), logging.INFO)
init_logging(log_level)


def _fetch_api_data(ticket_range: str = "0-99", **filters: str) -> list[dict[str, Any]]:
    """Fetch ticket data from the worker API."""

    url = f"{WORKER_BASE_URL}/v1/tickets"
    try:
        resp = requests.get(url, params={"range": ticket_range, **filters}, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        logging.error("Failed to fetch tickets from %s: %s", url, exc)
        raise


async def _fetch_aggregated_metrics_async() -> dict[str, Any]:
    """Return aggregated metrics from the worker API asynchronously."""

    url = f"{WORKER_BASE_URL}/v1/metrics/aggregated"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as resp:
                resp.raise_for_status()
                return await resp.json()
    except aiohttp.ClientError as exc:
        logging.error("Failed to fetch metrics from %s: %s", url, exc)
        raise

def _fetch_aggregated_metrics() -> dict[str, Any]:
    """Synchronous wrapper for the async metrics fetcher."""
    try:
        return asyncio.run(_fetch_aggregated_metrics_async())
    except RuntimeError:
        # If already in an event loop (e.g., in Jupyter), use create_task
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_fetch_aggregated_metrics_async())
def _transform_df(ticket_range: str = "0-99", **filters: str) -> pd.DataFrame:
    """Transform raw ticket data into a normalized DataFrame."""

    data = _fetch_api_data(ticket_range, **filters)
    return process_raw(data)


def load_data(ticket_range: str = "0-99", **filters: str) -> pd.DataFrame | None:
    """Load ticket data from the worker or a local mock file."""
    if USE_MOCK_DATA:
        logging.info("Loading ticket data from mock file")
        try:
            return process_raw(pd.read_json("tests/resources/mock_tickets.json"))
        except Exception as exc:  # pragma: no cover - file errors
            logging.error("failed to load mock data: %s", exc)
            return None

    logging.info("Fetching ticket data from worker API")
    try:
        metrics = _fetch_aggregated_metrics()
        logging.info("Aggregated metrics: %s", metrics)
        return _transform_df(ticket_range, **filters)
    except requests.RequestException as exc:
        logging.error("Error contacting worker API: %s", exc)
        return None


def create_app(df: pd.DataFrame | None) -> Dash:
    """Create Dash application."""
    server = Flask(__name__)

    # @server.route("/ping")
    # def ping() -> tuple[str, int]:
    #     """Simple health check endpoint."""
    #     return "OK", 200

    app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
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
