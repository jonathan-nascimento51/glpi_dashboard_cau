from types import SimpleNamespace

import httpx
import pybreaker
import pytest

from examples.resilient_client import ResilientClient
from shared.utils.resilience import breaker

pytest.importorskip("httpx")
pytest.importorskip("pybreaker")


class DummyGauge:
    def __init__(self):
        self.calls = []

    def labels(self, *, state):
        return SimpleNamespace(set=lambda v: self.calls.append((state, v)))


class DummyCounter:
    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1


@pytest.mark.asyncio
async def test_resilient_client_circuit_open(monkeypatch):
    breaker.STATE_OPEN = getattr(breaker, "STATE_OPEN", pybreaker.STATE_OPEN)
    breaker.open()
    called = False

    async def fail(*a, **k):
        nonlocal called
        called = True
        return httpx.Response(200)

    monkeypatch.setattr(httpx.AsyncClient, "request", fail)
    async with ResilientClient() as client:
        resp = await client.request("GET", "http://example.com")

    assert resp.status_code == 503
    assert not called
    breaker.close()


@pytest.mark.asyncio
async def test_resilient_client_default_timeout(monkeypatch):
    async def succeed(self, method, url, **kwargs):
        return httpx.Response(200)

    monkeypatch.setattr(httpx.AsyncClient, "request", succeed)
    async with ResilientClient() as client:
        assert isinstance(client.timeout, httpx.Timeout)
        assert client.timeout.connect == 5.0
        assert client.timeout.read == 5.0
        resp = await client.request("GET", "http://example.com")
    assert resp.status_code == 200
