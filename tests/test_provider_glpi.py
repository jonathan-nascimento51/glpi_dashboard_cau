"""Provider verification for GLPI API using Pact-Python."""

from __future__ import annotations

import os
import time
from multiprocessing import Process
from typing import Any, Dict

import pytest
import requests
from fastapi import FastAPI, HTTPException
from pact import Verifier

PROVIDER_STATE: str = "valid user"


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/_pact/provider_states")
    async def set_state(body: Dict[str, Any]) -> Dict[str, str]:
        global PROVIDER_STATE
        PROVIDER_STATE = body.get("state", "valid user")
        return {"result": "ok"}

    @app.post("/initSession")
    async def init_session(payload: Dict[str, Any]) -> Dict[str, str]:
        if PROVIDER_STATE == "valid user":
            return {"session_token": "11111111-1111-1111-1111-111111111111"}
        if PROVIDER_STATE == "invalid tokens":
            raise HTTPException(status_code=401)
        if PROVIDER_STATE == "service unavailable":
            raise HTTPException(status_code=503)
        raise HTTPException(status_code=500)

    return app


def run_server(port: int) -> None:
    import uvicorn

    uvicorn.run(create_app(), host="127.0.0.1", port=port, log_level="warning")


@pytest.fixture(scope="session")
def provider_url(unused_tcp_port: int):
    port = unused_tcp_port
    process = Process(target=run_server, args=(port,), daemon=True)
    process.start()
    for _ in range(20):
        try:
            requests.get(f"http://localhost:{port}/openapi.json", timeout=0.5)
            break
        except requests.exceptions.RequestException:
            time.sleep(0.2)
    yield f"http://localhost:{port}"
    process.terminate()
    process.join()


@pytest.mark.skipif(
    "PACT_BROKER_URL" not in os.environ,
    reason="Requires Pact Broker configuration",
)
def test_verify_against_broker(provider_url: str) -> None:
    broker_url = os.environ["PACT_BROKER_URL"]
    verifier = Verifier(provider="GLPI API", provider_base_url=provider_url)
    verify_opts = {
        "broker_url": broker_url,
        "provider_states_setup_url": f"{provider_url}/_pact/provider_states",
    }
    token = os.getenv("PACT_BROKER_TOKEN")
    if token:
        verify_opts["broker_token"] = token
    else:
        verify_opts["broker_username"] = os.getenv("PACT_BROKER_USERNAME", "")
        verify_opts["broker_password"] = os.getenv("PACT_BROKER_PASSWORD", "")

    output, _ = verifier.verify_with_broker(**verify_opts, enable_pending=True)
    assert output == 0
