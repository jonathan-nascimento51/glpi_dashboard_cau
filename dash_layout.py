"""Simple Dash layout for ticket overview."""

from __future__ import annotations

import pandas as pd
from functools import lru_cache

from dash import dash_table, dcc, html, callback, Output, Input
import plotly.express as px


@lru_cache(maxsize=1)
def _status_fig(df: pd.DataFrame) -> px.bar:
    counts = df.groupby("status").size().reset_index(name="count")
    return px.bar(counts, x="status", y="count")


def build_layout(df: pd.DataFrame) -> html.Div:
    """Build dashboard layout with lazy loading."""
    return html.Div(
        [
            html.H1("GLPI Dashboard"),
            dcc.Interval(id="init-load", n_intervals=0, max_intervals=1),
            html.Div(id="stats"),
            dcc.Graph(id="status-graph"),
            dash_table.DataTable(
                id="ticket-table",
                columns=[
                    {"name": c, "id": c}
                    for c in ["id", "name", "status", "assigned_to"]
                ],
                page_size=10,
            ),
        ]
    )


def register_callbacks(app, df: pd.DataFrame) -> None:
    @callback(
        Output("ticket-table", "data"),
        Output("status-graph", "figure"),
        Output("stats", "children"),
        Input("init-load", "n_intervals"),
    )

    # Dash callbacks must be regular functions that return a tuple of outputs.
    # Using async def would yield a coroutine and trigger a
    # SchemaTypeValidationError.
    def load_data(_):
        fig = _status_fig(df)
        total = len(df)
        closed = df[df["status"].str.lower() == "closed"].shape[0]
        opened = total - closed
        stats = [
            html.Div(f"Total: {total}"),
            html.Div(f"Abertos: {opened}"),
            html.Div(f"Fechados: {closed}"),
        ]
        return df.to_dict("records"), fig, stats
