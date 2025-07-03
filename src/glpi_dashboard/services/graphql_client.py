from __future__ import annotations

"""Lightweight GraphQL client for GLPI using ``gql`` and ``httpx``."""

from typing import Any, Dict, Optional

import json

from pydantic import BaseModel, Field

from gql import Client, gql
from gql.transport.httpx import HTTPXTransport


class GraphQLParams(BaseModel):
    """Parameters for constructing :class:`GlpiGraphQLClient`."""

    base_url: str = Field(..., description="GLPI REST base URL")
    app_token: str
    session_token: str
    timeout: float = Field(default=30.0, description="Request timeout")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")


class GlpiGraphQLClient:
    """Synchronous wrapper around :class:`gql.Client`.

    Suitable for quick scripts that only need a handful of GraphQL calls without
    setting up asynchronous infrastructure.
    """

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


def graphql_client_tool(params: GraphQLParams, query: str) -> str:
    """Execute a GraphQL query with minimal setup and return JSON or error."""

    try:
        client = GlpiGraphQLClient(
            params.base_url,
            params.app_token,
            params.session_token,
            timeout=params.timeout,
            verify_ssl=params.verify_ssl,
        )
        data = client.execute(query)
        return json.dumps(data)
    except Exception as exc:  # pragma: no cover - tool usage
        return str(exc)


__all__ = [
    "GlpiGraphQLClient",
    "GraphQLParams",
    "graphql_client_tool",
]
