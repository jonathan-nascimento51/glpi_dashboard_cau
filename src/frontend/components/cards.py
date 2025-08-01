"""Reusable Dash components for ticket status summaries.

This module defines a simple card component for displaying a summary of
ticket counts grouped by status. The component is intentionally
framework-agnostic beyond Dash itself: it relies only on standard
Dash and dash_bootstrap_components primitives and can therefore be
composed easily within an existing layout.
"""

from __future__ import annotations



import dash_bootstrap_components as dbc
from dash import html


def TicketStatusCard(title: str, status_data: dict[str, int]) -> dbc.Card:
    """Render a card summarising ticket statuses for a given service level.

    Args:
        title: The heading to display at the top of the card (e.g. "Nível 1").
        status_data: A mapping of status names to counts. The keys should be
            lowercased status codes (e.g. ``"new"``), though any strings
            provided will be displayed as capitalised labels.

    Returns:
        A Dash Bootstrap Components ``Card`` instance ready for use in a
        layout.
    """
    # Create a list of paragraphs: one per status. Capitalise the status
    # names to make them more user friendly and include a colon separator.
    status_items = []
    for status, count in status_data.items():
        label = status.replace("_", " ").title()
        status_items.append(html.P(f"{label}: {count}", className="card-text"))

    card_body = dbc.CardBody(
        [
            html.H5(title, className="card-title"),
            *status_items,
        ]
    )
    return dbc.Card(card_body, className="h-100")
