"""Dash app using the worker API for ticket metrics."""

import json
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
from shared.utils.logging import init_logging

__all__ = ["create_app", "main"]

WORKER_BASE_URL = os.getenv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000")
log_level_name = os.getenv("LOG_LEVEL", "INFO")
log_level = getattr(logging, log_level_name.upper(), logging.INFO)
init_logging(log_level)


def _fetch_aggregated_metrics() -> dict[str, Any]:
    """Return aggregated metrics from the worker API."""

    url = f"{WORKER_BASE_URL}/v1/metrics/aggregated"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        logging.error("Failed to fetch metrics from %s: %s", url, exc)
        return {}


def load_data(ticket_range: str = "0-99", **filters: str) -> list[dict[str, Any]]:
    """Load ticket data from the worker or a local mock file.

    Parameters
    ----------
    ticket_range:
        Inclusive range of ticket IDs to fetch in the format ``"start-end"``.
    **filters:
        Additional filter parameters forwarded to the worker API, such as
        ``status`` or ``technician``.
    """

    if USE_MOCK_DATA:
        logging.info("Loading ticket data from mock file")
        try:
            with open("tests/resources/mock_tickets.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:  # pragma: no cover - file errors
            logging.error("failed to load mock data: %s", exc)
            raise

    url = f"{WORKER_BASE_URL}/v1/tickets"
    filtered_filters = {k: v for k, v in filters.items() if v is not None}
    params = {"range": ticket_range, **filtered_filters}
    logging.info("Fetching ticket data from %s with params %s", url, params)
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        logging.error("Error contacting worker API: %s", exc)
        raise


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
    try:
        data = load_data()
    except Exception as exc:
        logging.error("Failed to load data for profiling: %s", exc)
        data = []
    df = pd.DataFrame(data) if data else None
    create_app(df)
    profiler.disable()
    Stats(profiler).sort_stats("cumulative").print_stats(10)


def main() -> None:
    """Run the Dash server."""
    try:
        data = load_data()
    except Exception as exc:
        logging.error("Failed to load initial data: %s", exc)
        data = []
    df = pd.DataFrame(data) if data else None
    app = create_app(df)
    app.run(
        host="0.0.0.0", port=DASH_PORT, debug=False, use_reloader=False, threaded=True
    )


if __name__ == "__main__":
    main()
