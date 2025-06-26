"""Offline Dash app using JSON dump."""

import json
from pathlib import Path

import pandas as pd
from dash import Dash
from flask import Flask
from flask_compress import Compress

from data_pipeline import process_raw
from dash_layout import build_layout, register_callbacks


DATA_FILE = Path("mock/sample_data.json")


def load_data(path: Path = DATA_FILE) -> pd.DataFrame:
    """Load and process ticket data from JSON."""
    with path.open() as f:
        raw = json.load(f)
    return process_raw(raw)


def create_app(df: pd.DataFrame) -> Dash:
    """Create Dash application with Gzip compression."""
    server = Flask(__name__)
    Compress(server)
    app = Dash(__name__, server=server)
    app.layout = build_layout(df)
    register_callbacks(app, df)
    return app


def profile_startup() -> None:
    """Profile app startup using cProfile."""
    import cProfile
    from pstats import Stats

    profiler = cProfile.Profile()
    profiler.enable()
    df = load_data()
    create_app(df)
    profiler.disable()
    Stats(profiler).sort_stats("cumulative").print_stats(10)


if __name__ == "__main__":
    df = load_data()
    app = create_app(df)
    app.run_server(debug=True)
