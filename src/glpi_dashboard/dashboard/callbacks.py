from __future__ import annotations

import pandas as pd
from dash import callback, Output, Input

from .components import _status_fig, compute_ticket_stats


def register_callbacks(app, df: pd.DataFrame) -> None:
    @callback(
        Output("ticket-store", "data"),
        Output("status-graph", "figure"),
        Output("stats", "children"),
        Input("init-load", "n_intervals"),
    )
    def load_data(_):
        fig = _status_fig(df)
        stats = compute_ticket_stats(df)
        return df.to_dict("records"), fig, stats

    app.clientside_callback(
        """
        function(records, status){
            let rows = records;
            if(status){
                rows = records.filter(r => r.status === status);
            }
            const figPatch = new window.dash_clientside.Patch();
            figPatch.data = [{
                type: 'scattergl',
                mode: 'markers',
                x: rows.map(r => r.date_creation),
                y: rows.map(r => r.id)
            }];
            return [rows, figPatch];
        }
        """,
        Output("ticket-table", "data"),
        Output("scatter-plot", "figure"),
        Input("ticket-store", "data"),
        Input("status-filter", "value"),
    )
