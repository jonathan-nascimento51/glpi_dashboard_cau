"""Service layer exports for the GLPI dashboard."""

from .glpi_session import (
    Credentials,
    GLPISession,
    SessionParams,
    open_session_tool,
)
from .glpi_api_client import (
    GlpiApiClient,
    GLPIAPIClient,
    ApiClientParams,
    fetch_tickets_tool,
)
from .graphql_client import GlpiGraphQLClient, GraphQLParams, graphql_client_tool
from .glpi_rest_client import GLPIClient, RestClientParams, graphql_query_tool
from .langgraph_workflow import AgentState, build_workflow  # re-export for tests
from .batch_fetch import (
    fetch_all_tickets,
    BatchFetchParams,
    fetch_all_tickets_tool,
)
from .exceptions import (
    GLPIAPIError,
    GLPIBadRequestError,
    GLPIUnauthorizedError,
    GLPIForbiddenError,
    GLPINotFoundError,
    GLPITooManyRequestsError,
    GLPIInternalServerError,
    HTTP_STATUS_ERROR_MAP,
    glpi_retry,
    parse_error,
)

__all__ = [
    "Credentials",
    "GLPISession",
    "SessionParams",
    "open_session_tool",
    "GLPIAPIClient",
    "GlpiApiClient",
    "ApiClientParams",
    "fetch_tickets_tool",
    "GLPIClient",
    "RestClientParams",
    "graphql_query_tool",
    "GraphQLParams",
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
