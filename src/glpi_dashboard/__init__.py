"""Initialize the glpi_dashboard package and optional tracing."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def _setup_langsmith() -> None:
    """Enable LangSmith tracing if the relevant variables are set."""

    if os.getenv("LANGCHAIN_TRACING_V2"):
        try:
            from langsmith import Client

            Client()  # validates API key and project
            logger.info("LangSmith tracing enabled")
        except Exception as exc:  # pragma: no cover - optional feature
            logger.warning("Failed to enable LangSmith tracing: %s", exc)


_setup_langsmith()
