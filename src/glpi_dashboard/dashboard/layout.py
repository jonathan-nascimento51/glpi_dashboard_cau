from __future__ import annotations

import pandas as pd
from dash import dash_table, dcc, html
import dash_bootstrap_components as dbc


def render_dashboard(df: pd.DataFrame) -> html.Div:
    """Render main dashboard components."""
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
                    for c in [
                        "id",
                        "name",
                        "status",
                        "assigned_to",
                        "group",
                        "date_creation",
                    ]
                ],
                page_size=10,
            ),
        ]
    )


def build_layout(df: pd.DataFrame | None) -> html.Div:
    """Return dashboard layout or an error message."""
    if df is None:
        return dbc.Alert(
            "Erro na conexão com o GLPI. Verifique suas credenciais.",
            color="danger",
        )
    return render_dashboard(df)
