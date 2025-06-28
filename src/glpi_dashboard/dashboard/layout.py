from __future__ import annotations

import pandas as pd
from dash import dash_table, dcc, html


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
