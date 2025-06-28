"""Wrapper around the langgraph workflow module for compatibility."""

import langgraph_workflow as _wf
from glpi_dashboard.services.glpi_session import Credentials
from .glpi_session import GLPISession
from glpi_dashboard.config.settings import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
)
from glpi_dashboard.data.pipeline import process_raw

_wf.GLPISession = GLPISession

AgentState = _wf.AgentState
supervisor = _wf.supervisor


async def fetcher(state: AgentState) -> AgentState:
    creds = Credentials(
        app_token=GLPI_APP_TOKEN,
        user_token=GLPI_USER_TOKEN,
        username=GLPI_USERNAME,
        password=GLPI_PASSWORD,
    )
    session_cls = GLPISession
    async with session_cls(GLPI_BASE_URL, creds) as client:
        tickets = await client.get("search/Ticket")
    df = process_raw(tickets.get("data", tickets))
    state["data"] = df
    state["messages"].append("fetched tickets")
    return state


analyzer = _wf.analyzer
fallback = _wf.fallback


def build_workflow() -> _wf.StateGraph:
    """Create LangGraph workflow using local fetcher wrapper."""
    workflow = _wf.StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor)
    workflow.add_node("fetcher", fetcher)
    workflow.add_node("analyzer", analyzer)
    workflow.add_node("fallback", fallback)

    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        lambda s: s["next_agent"],
        {
            "fetcher": "fetcher",
            "analyzer": "analyzer",
            "fallback": "fallback",
        },
    )

    workflow.add_edge("fetcher", "analyzer")
    workflow.add_edge("analyzer", "fallback")
    workflow.add_edge("fallback", _wf.END)

    return workflow


__all__ = [
    "AgentState",
    "supervisor",
    "fetcher",
    "analyzer",
    "fallback",
    "build_workflow",
    "GLPISession",
]
