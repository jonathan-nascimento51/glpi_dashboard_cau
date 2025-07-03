"""Initialize the glpi_dashboard package and optional tracing."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def _setup_langsmith() -> None:
    """Enable LangSmith tracing if the relevant variables are set."""

    if not os.getenv("LANGCHAIN_TRACING_V2"):
        return
    api_key = os.getenv("LANGCHAIN_API_KEY")
    project = os.getenv("LANGCHAIN_PROJECT")

    if not api_key:
        logger.warning("LANGCHAIN_TRACING_V2 is set but LANGCHAIN_API_KEY is missing")
        return

    try:
        from langsmith import Client

        Client(api_key=api_key, project_name=project)
        if project:
            logger.info("LangSmith tracing enabled for project %s", project)
        else:
            logger.info("LangSmith tracing enabled")
    except Exception as exc:  # pragma: no cover - optional feature
        logger.warning("Failed to enable LangSmith tracing: %s", exc)


_setup_langsmith()
