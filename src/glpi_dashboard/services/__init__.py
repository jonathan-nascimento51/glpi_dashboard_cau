"""Service layer exports for the GLPI dashboard."""

from .batch_fetch import BatchFetchParams, fetch_all_tickets, fetch_all_tickets_tool
from .exceptions import (
    HTTP_STATUS_ERROR_MAP,
    GLPIAPIError,
    GLPIBadRequestError,
    GLPIForbiddenError,
    GLPIInternalServerError,
    GLPINotFoundError,
    GLPITooManyRequestsError,
    GLPIUnauthorizedError,
    glpi_retry,
    parse_error,
)
from .glpi_api_client import (
    ApiClientParams,
    GlpiApiClient,
    GLPIAPIClient,
    fetch_tickets_tool,
)
from .glpi_rest_client import (
    GLPIClient,
    GraphQLQueryParams,
    RestClientParams,
    graphql_query_tool,
)
from .glpi_session import (
    Credentials,
    GLPISession,
    SessionParams,
    open_session_tool,
)
from .tool_error import ToolError
from .graphql_client import (
    GlpiGraphQLClient,
    GraphQLClientQueryParams,
    GraphQLParams,
    graphql_client_tool,
)

try:  # pragma: no cover - optional dependency during tests
    from .langgraph_workflow import AgentState, build_workflow
except Exception:  # pragma: no cover - fallback if langgraph missing
    AgentState = object  # type: ignore[misc,assignment]

    def build_workflow(*_args, **_kwargs):
        raise ImportError("langgraph is required for workflow features")


__all__ = [
    "Credentials",
    "GLPISession",
    "SessionParams",
    "open_session_tool",
    "ToolError",
    "GLPIAPIClient",
    "GlpiApiClient",
    "ApiClientParams",
    "fetch_tickets_tool",
    "GLPIClient",
    "RestClientParams",
    "GraphQLQueryParams",
    "graphql_query_tool",
    "GraphQLParams",
    "GraphQLClientQueryParams",
    "graphql_client_tool",
    "GlpiGraphQLClient",
    "GLPIAPIError",
    "GLPIBadRequestError",
    "GLPIUnauthorizedError",
    "GLPIForbiddenError",
    "GLPINotFoundError",
    "GLPITooManyRequestsError",
    "GLPIInternalServerError",
    "HTTP_STATUS_ERROR_MAP",
    "glpi_retry",
    "parse_error",
    "build_workflow",
    "AgentState",
    "fetch_all_tickets",
    "BatchFetchParams",
    "fetch_all_tickets_tool",
]
