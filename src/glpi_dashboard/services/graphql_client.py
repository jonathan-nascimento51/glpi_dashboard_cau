from __future__ import annotations

"""Lightweight GraphQL client for GLPI using ``gql`` and ``httpx``."""

from typing import Any, Dict, Optional

from gql import Client, gql
from gql.transport.httpx import HTTPXTransport


class GlpiGraphQLClient:
    """Synchronous wrapper around :class:`gql.Client`."""

    def __init__(
        self,
        base_url: str,
        app_token: str,
        session_token: str,
        *,
        timeout: float = 30.0,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize the client with the GraphQL endpoint and credentials."""

        url = base_url.rstrip("/") + "/graphql"
        headers = {"App-Token": app_token, "Session-Token": session_token}
        transport = HTTPXTransport(
            url=url,
            headers=headers,
            timeout=timeout,
            verify=verify_ssl,
        )
        self._client = Client(transport=transport, fetch_schema_from_transport=False)

    def execute(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a GraphQL query and return the response data."""

        document = gql(query)
        return self._client.execute(document, variable_values=variables or {})


__all__ = ["GlpiGraphQLClient"]
