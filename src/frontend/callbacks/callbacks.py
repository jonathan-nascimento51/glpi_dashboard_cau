from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

import dash_bootstrap_components as dbc  # type: ignore
import pandas as pd
from dash import Dash, Input, Output, callback
from frontend.components.components import _status_fig, compute_ticket_stats


def register_callbacks(
    app: Dash,
    loader: Callable[..., List[Dict[str, Any]]],
    *,
    ticket_range: str = "0-99",
    **filters: Any,
) -> None:
    """Register Dash callbacks using ``loader`` to fetch data.

    The loader must return a list of ticket dictionaries which will be
    converted into pandas DataFrames inside each callback.

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
    def load_data(_: int) -> tuple[dict[str, str], dict[str, Any], list[Any]]:
        data = loader(ticket_range, **filters)
        df: pd.DataFrame = pd.DataFrame(data)
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
    def update_table(
        store: Optional[Dict[str, Any]], status: Optional[str]
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        rng: str = store.get("ticket_range", ticket_range) if store else ticket_range
        data = loader(rng, status=status, **filters)
        df: pd.DataFrame = pd.DataFrame(data)
        fig: Dict[str, Any] = {
            "data": [
                {
                    "type": "scattergl",
                    "mode": "markers",
                    "x": df["date_creation"],
                    "y": df["id"],
                }
            ]
        }
        return list(df.to_dict("records")), fig  # type: ignore

    @callback(
        Output("notification-container", "children"),
        Input("init-load", "n_intervals"),
    )
    def notify(_: int) -> dbc.Alert:
        try:
            loader(ticket_range, **filters)
        except Exception as exc:  # pragma: no cover - network/logic errors
            return dbc.Alert(
                f"Erro ao conectar à API: {exc}", color="danger", dismissable=True
            )
        return dbc.Alert(
            "Conexão com a API estabelecida", color="success", dismissable=True
        )
