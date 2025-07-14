from __future__ import annotations

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html


def render_dashboard(df: pd.DataFrame) -> html.Div:
    """Render main dashboard components."""
    from dash import dash_table, dcc

    statuses = ["All"] + sorted({str(s) for s in df["status"].dropna().unique()})
    status_options = [{"label": s, "value": s if s != "All" else ""} for s in statuses]

    return html.Div(
        [
            html.H1("GLPI Dashboard"),
            html.Div(id="notification-container"),
            dcc.Interval(id="init-load", n_intervals=0, max_intervals=1),
            dcc.Store(id="ticket-store"),
            dcc.Dropdown(
                id="status-filter",
                options=[
                    {"label": o["label"], "value": o["value"]} for o in status_options
                ],
                value="",
                clearable=False,
                style={"width": "200px"},
            ),
            html.Div(id="stats"),
            dcc.Graph(id="status-graph"),
            dcc.Graph(id="scatter-plot"),
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


def build_layout(df: pd.DataFrame | None) -> html.Div | dbc.Alert:
    """Return dashboard layout or an error message."""
    if df is None:
        return dbc.Alert(
            "Erro na conexão com o GLPI. Verifique suas credenciais.",
            color="danger",
        )
    return render_dashboard(df)
