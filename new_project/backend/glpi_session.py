from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Credentials(BaseModel):
    """Authentication data for the GLPI API."""

    app_token: str
    user_token: str | None = None
    username: str | None = None
    password: str | None = None


class GLPISession:
    """Very small placeholder async session."""

    def __init__(self, base_url: str, credentials: Credentials) -> None:
        self.base_url = base_url
        self.credentials = credentials

    async def __aenter__(self) -> "GLPISession":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def get_all_paginated(
        self, itemtype: str, page_size: int = 100, **params: Any
    ) -> list[dict[str, Any]]:
        """Return an empty result set.

        Real logic should call the GLPI REST API.
        """

        return []
