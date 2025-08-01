"""Dash application for displaying GLPI ticket status summaries.

This script defines a minimal Dash app that retrieves aggregated ticket
counts by status and by support level from a FastAPI backend and
presents them as a series of cards. It is designed to be self‑contained
for demonstration purposes. In a full project this code would
integrate into the existing Dash application infrastructure.
"""

from __future__ import annotations

import json
import logging
from typing import Dict

import dash_bootstrap_components as dbc
import requests
from dash import Dash, html
from frontend.components.cards import TicketStatusCard

logger = logging.getLogger(__name__)


def fetch_summary(base_url: str) -> Dict[str, Dict[str, int]]:
    """Fetch the ticket summary from the backend API.

    Args:
        base_url: The base URL of the backend (e.g. ``"http://localhost:8000"``).

    Returns:
        A dictionary mapping level names to status counts. If the request
        fails or returns invalid JSON, an empty dict is returned.
    """
    endpoint = f"{base_url}/api/tickets/summary-per-level"
    try:
        response = requests.get(endpoint, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception:
        logger.exception("Failed to fetch ticket summary from %s", endpoint)
        return {}


def create_layout(summary: Dict[str, Dict[str, int]]) -> html.Div:
    """Construct the Dash layout based on the provided summary data."""
    cards = []
    # Define friendly names for each level. If the summary does not contain a
    # given level, an empty dict will be passed to the card.
    level_titles = {"N1": "Nível 1", "N2": "Nível 2", "N3": "Nível 3", "N4": "Nível 4"}
    for level_key in ["N1", "N2", "N3", "N4"]:
        status_data = summary.get(level_key, {})
        cards.append(
            dbc.Col(
                TicketStatusCard(
                    title=level_titles[level_key], status_data=status_data
                ),
                width=3,
            )
        )
    # Arrange the cards in a single row
    row = dbc.Row(cards, className="g-3")
    container = dbc.Container([row], fluid=True, className="py-4")
    return html.Div([container])


def build_app(base_url: str = "http://localhost:8000") -> Dash:
    """Create and configure the Dash application."""
    summary_data = fetch_summary(base_url)
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = create_layout(summary_data)
    return app


if __name__ == "__main__":
    # When run directly, bootstrap the app pointing at a locally running
    # backend. Adjust the base_url if your backend runs elsewhere.
    dash_app = build_app(base_url="http://localhost:8000")
    dash_app.run_server(debug=True, host="0.0.0.0", port=8050)
