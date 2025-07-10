"""Lightweight GraphQL client for GLPI using ``gql`` and ``httpx``."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from gql import Client, gql
from gql.transport.httpx import HTTPXTransport
from pydantic import BaseModel, Field

from shared.resilience import retry_api_call


class GraphQLParams(BaseModel):
    """Parameters for constructing :class:`GlpiGraphQLClient`."""

    base_url: str = Field(..., description="GLPI REST base URL")
    app_token: str
    session_token: str
    timeout: float = Field(default=30.0, description="Request timeout")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")


class GraphQLClientQueryParams(GraphQLParams):
    """Input parameters for :func:`graphql_client_tool` including the query."""

    query: str = Field(..., description="GraphQL query string")


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
        ssl_ctx = False if not verify_ssl else None
        transport = HTTPXTransport(
            url=url,
            headers=headers,
            timeout=timeout,
            ssl=ssl_ctx,
        )
        self._client = Client(transport=transport, fetch_schema_from_transport=False)

    @retry_api_call
    def execute(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a GraphQL query and return the response data."""

        document = gql(query)
        return self._client.execute(document, variable_values=variables or {})


def graphql_client_tool(params: GraphQLClientQueryParams) -> str:
    """Execute a GraphQL query with minimal setup and return JSON or error.

    This tool mirrors :func:`graphql_query_tool` but relies on the synchronous
    :class:`GlpiGraphQLClient`. Use it in workflows from ``AGENTS.md`` when
    asynchronous infrastructure isn't available.
    """

    try:
        client = GlpiGraphQLClient(
            params.base_url,
            params.app_token,
            params.session_token,
            timeout=params.timeout,
            verify_ssl=params.verify_ssl,
        )
        data = client.execute(params.query)
        return json.dumps(data)
    except Exception as exc:  # pragma: no cover - tool usage
        return str(exc)


__all__ = [
    "GlpiGraphQLClient",
    "GraphQLParams",
    "GraphQLClientQueryParams",
    "graphql_client_tool",
]
