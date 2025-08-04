# ruff: noqa: E402
import asyncio
import json
import sys
import time
from types import ModuleType, SimpleNamespace

import pytest

structlog = ModuleType("structlog")
setattr(structlog, "get_logger", lambda *a, **k: SimpleNamespace())
contextvars = ModuleType("contextvars")
setattr(contextvars, "bind_contextvars", lambda *a, **k: None)
setattr(contextvars, "clear_contextvars", lambda: None)
setattr(contextvars, "merge_contextvars", lambda *a, **k: None)
setattr(structlog, "contextvars", contextvars)
sys.modules.setdefault("structlog", structlog)
sys.modules.setdefault("structlog.contextvars", contextvars)
httpx_mod = ModuleType("httpx")
setattr(httpx_mod, "AsyncClient", object)
sys.modules.setdefault("httpx", httpx_mod)
sys.modules.setdefault("redis.asyncio", ModuleType("redis.asyncio"))

from backend.application import batch_fetch
from backend.schemas.ticket_models import CleanTicketDTO


class DummyClient:
    def __init__(self, delay: float = 0.01) -> None:
        self.delay = delay
        self.calls: list[list[int]] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def fetch_tickets_by_ids(self, ids: list[int]):
        self.calls.append(ids)
        await asyncio.sleep(self.delay)
        return [CleanTicketDTO(id=i, status="new") for i in ids]


@pytest.mark.asyncio
async def test_fetch_all_tickets(monkeypatch):
    client = DummyClient()
    monkeypatch.setattr(batch_fetch, "GLPISession", lambda *a, **k: object())
    monkeypatch.setattr(batch_fetch, "GlpiApiClient", lambda *a, **k: client)

    ids = [1, 2, 3]
    data = await batch_fetch.fetch_all_tickets(ids)

    assert client.calls == [ids]
    assert [d["id"] for d in data] == ids


@pytest.mark.asyncio
async def test_async_vs_sync_benchmark(monkeypatch):
    client = DummyClient()
    monkeypatch.setattr(batch_fetch, "GLPISession", lambda *a, **k: object())
    monkeypatch.setattr(batch_fetch, "GlpiApiClient", lambda *a, **k: client)
    ids = list(range(20))

    start = time.perf_counter()
    async_result = await batch_fetch.fetch_all_tickets(ids)
    async_duration = time.perf_counter() - start

    seq_client = DummyClient()

    async def sequential() -> list[dict]:
        out = []
        for tid in ids:
            res = await seq_client.fetch_tickets_by_ids([tid])
            out.extend(res)
        return [t.model_dump() for t in out]

    start = time.perf_counter()
    sync_result = await sequential()
    sync_duration = time.perf_counter() - start

    assert async_result == sync_result
    assert async_duration < sync_duration


@pytest.mark.asyncio
async def test_fetch_all_tickets_tool_error(monkeypatch):
    async def boom(_ids):
        raise RuntimeError("fail")

    monkeypatch.setattr(batch_fetch, "fetch_all_tickets", boom)
    out = await batch_fetch.fetch_all_tickets_tool(
        batch_fetch.BatchFetchParams(ids=[1])
    )
    data = json.loads(out)
    assert data["error"]["details"] == "fail"
