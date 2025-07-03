from __future__ import annotations

import pandas as pd
from dash import callback, Output, Input

from .components import _status_fig, compute_ticket_stats


def _get_filtered(df: pd.DataFrame, status: str | None) -> pd.DataFrame:
    """Return dataframe optionally filtered by status."""
    if status:
        return df[df["status"] == status.lower()]
    return df


def register_callbacks(app, loader, *, ticket_range: str = "0-99", **filters) -> None:
    """Register Dash callbacks using ``loader`` to fetch data."""

    @callback(
        Output("ticket-store", "data"),
        Output("status-graph", "figure"),
        Output("stats", "children"),
        Input("init-load", "n_intervals"),
    )
    def load_data(_: int) -> tuple[dict, dict, list]:
        df = loader(ticket_range, **filters)
        fig = _status_fig(df)
        stats = compute_ticket_stats(df)
        return {"ticket_range": ticket_range}, fig, stats

    @callback(
        Output("ticket-table", "data"),
        Output("scatter-plot", "figure"),
        Input("ticket-store", "data"),
        Input("status-filter", "value"),
    )
    def update_table(store: dict, status: str | None) -> tuple[list[dict], dict]:
        rng = store.get("ticket_range", ticket_range) if store else ticket_range
        df = loader(rng, **filters)
        filtered = _get_filtered(df, status)
        fig = {
            "data": [
                {
                    "type": "scattergl",
                    "mode": "markers",
                    "x": filtered["date_creation"],
                    "y": filtered["id"],
                }
            ]
        }
        return filtered.to_dict("records"), fig
