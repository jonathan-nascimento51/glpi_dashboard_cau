import os
import sys

import pytest

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
)  # noqa: E402

from glpi_dashboard.services import langgraph_workflow  # noqa: E402


@pytest.mark.asyncio
async def test_workflow_fetch(monkeypatch):
    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, *args, **kwargs):
            return {
                "data": [
                    {
                        "id": 1,
                        "status": "new",
                        "group": "N1",
                        "date_creation": "2024-01-01",
                        "assigned_to": "alice",
                    }
                ]
            }

    monkeypatch.setattr(
        langgraph_workflow, "GLPISession", lambda *a, **k: FakeSession()
    )

    workflow = langgraph_workflow.build_workflow().compile()
    state = {"messages": ["fetch"], "next_agent": "", "iteration_count": 0}
    result = await workflow.ainvoke(state)
    assert "fetched tickets" in result["messages"]


def test_supervisor_routes_llm(monkeypatch: pytest.MonkeyPatch):
    called = {}

    class DummyRunnable:
        def invoke(self, inp):
            called["msg"] = inp["message"]
            return langgraph_workflow.NextAgent(next_agent="analyzer")

    monkeypatch.setattr(langgraph_workflow, "supervisor_llm", DummyRunnable())
    state = {"messages": ["please analyze"], "next_agent": "", "iteration_count": 0}
    result = langgraph_workflow.supervisor(state)
    assert result["next_agent"] == "analyzer"
    assert called["msg"] == "please analyze"


def test_validation_failure_and_recovery():
    state = {
        "messages": ["metrics: {'total': 'bad'}"],
        "next_agent": "",
        "iteration_count": 0,
    }
    state = langgraph_workflow.validation_node(state)
    assert "error" in state
    state = langgraph_workflow.recovery_node(state)
    assert state["next_agent"] == "fallback"


def test_recovery_retry():
    state = {
        "messages": ["fetch"],
        "next_agent": "fetcher",
        "iteration_count": 0,
        "error": "boom",
    }
    out = langgraph_workflow.recovery_node(state)
    assert "retrying" in out["messages"]
