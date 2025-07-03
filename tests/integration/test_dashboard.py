"""Integration tests for the dashboard app."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest
from aiohttp import web

ROOT = Path(__file__).resolve().parents[2]
main_globals = runpy.run_path(ROOT / "main.py")
main = type("Module", (), main_globals)


@pytest.fixture()
async def mock_glpi_server(unused_tcp_port):
    async def init_session(request):
        return web.json_response({"session_token": "tok"})

    async def search_ticket(request):
        data = {
            "data": [
                {
                    "id": 1,
                    "status": 5,
                    "group": "N2",
                    "assigned_to": "bob",
                    "name": "t2",
                    "date_creation": "2024-01-02T00:00:00Z",
                }
            ]
        }
        headers = {"Content-Range": "0-0/1"}
        return web.json_response(data, headers=headers)

    app = web.Application()
    app.router.add_get("/apirest.php/initSession", init_session)
    app.router.add_get("/apirest.php/search/Ticket", search_ticket)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", unused_tcp_port)
    await site.start()
    yield f"http://localhost:{unused_tcp_port}/apirest.php"
    await runner.cleanup()


@pytest.mark.asyncio
async def test_dashboard_flows(dash_duo, mock_glpi_server, monkeypatch):
    monkeypatch.setenv("GLPI_BASE_URL", mock_glpi_server)
    monkeypatch.setenv("GLPI_APP_TOKEN", "app")
    monkeypatch.setenv("GLPI_USER_TOKEN", "tok")
    monkeypatch.delenv("USE_MOCK_DATA", raising=False)

    df = main.load_data()
    app = main.create_app(df)

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("h1", "GLPI Dashboard", timeout=10)
    dash_duo.percy_snapshot("login")

    dash_duo.select_dcc_dropdown("#status-filter", "Solved")
    dash_duo.wait_for_text_to_equal("#stats div:nth-child(3)", "Fechados: 1")
    dash_duo.percy_snapshot("search")

    dash_duo.select_dcc_dropdown("#status-filter", "All")
    dash_duo.wait_for_text_to_equal("#stats div:nth-child(1)", "Total: 1")
    dash_duo.percy_snapshot("chart_update")
