from __future__ import annotations

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, callback

from frontend.components.components import _status_fig, compute_ticket_stats


def _get_filtered(df: pd.DataFrame, status: str | None) -> pd.DataFrame:
    """Return dataframe optionally filtered by status."""
    return df[df["status"] == status.lower()] if status else df


def register_callbacks(app, loader, *, ticket_range: str = "0-99", **filters) -> None:
    """Register Dash callbacks using ``loader`` to fetch data.

    Example
    -------
    >>> from dashboard_app import load_data
    >>> register_callbacks(app, load_data)
    """

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
        # Convert fig to dict if it's a plotly.graph_objs.Figure
        if hasattr(fig, "to_dict"):
            fig = fig.to_dict()
        elif not isinstance(fig, dict):
            fig = {}
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

    @callback(
        Output("notification-container", "children"),
        Input("init-load", "n_intervals"),
    )
    def notify(_: int) -> dbc.Alert:
        try:
            loader(ticket_range, **filters)
        except Exception as exc:  # pragma: no cover - network/logic errors
            return dbc.Alert(
                f"Erro ao conectar ao GLPI: {exc}", color="danger", dismissable=True
            )
        return dbc.Alert(
            "Conex\u00e3o com GLPI estabelecida", color="success", dismissable=True
        )
