"""Public interface for GLPI infrastructure helpers."""

import contextlib

with contextlib.suppress(ImportError):
    from .glpi_client import (
        GLPIClientAuthError,
        GLPIClientError,
        GLPIClientNotFound,
        GLPIClientRateLimit,
        GLPIClientServerError,
        GLPISessionManager,
        SearchCriteriaBuilder,
        get_secret,
    )
    from .glpi_session import GLPISession

__all__ = [
    "GLPISessionManager",
    "GLPISession",
    "GLPIClientError",
    "GLPIClientAuthError",
    "GLPIClientNotFound",
    "GLPIClientRateLimit",
    "GLPIClientServerError",
    "SearchCriteriaBuilder",
    "get_secret",
]
