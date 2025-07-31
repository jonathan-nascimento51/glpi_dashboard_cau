import dash
from dash import html

app = dash.Dash(__name__)

app.layout = html.Div([html.H1("GLPI Dashboard Novo")])

if __name__ == "__main__":
if __name__ == "__main__":
    import os
    debug = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    app.run_server(host="0.0.0.0", port=8050, debug=debug)
