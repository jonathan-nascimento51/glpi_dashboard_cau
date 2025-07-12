from unittest.mock import ANY

import pytest
from gql import Client

from backend.adapters.graphql_client import GlpiGraphQLClient


@pytest.fixture
def mock_gql_client(mocker):
    """Mocks the gql.Client and its transport."""
    mock_client_instance = mocker.MagicMock(spec=Client)
    mock_client_class = mocker.patch(
        "backend.adapters.graphql_client.Client", return_value=mock_client_instance
    )
    # Make gql.gql a pass-through function for simplicity in tests
    mocker.patch("backend.adapters.graphql_client.gql", side_effect=lambda q: q)
    return mock_client_class, mock_client_instance


def test_client_initialization(mocker):
    """
    Verifies that GlpiGraphQLClient initializes the gql.Client
    with a correctly configured AIOHTTPTransport.
    """
    mock_transport_class = mocker.patch(
        "backend.adapters.graphql_client.AIOHTTPTransport"
    )
    mocker.patch("backend.adapters.graphql_client.Client")

    client = GlpiGraphQLClient(
        "http://example.com/apirest.php",
        app_token="APP",
        session_token="SESS",
    )

    assert client is not None
    mock_transport_class.assert_called_once_with(
        url="http://example.com/apirest.php/graphql",
        headers={"App-Token": "APP", "Session-Token": "SESS"},
    )


def test_execute_forwards_query(mock_gql_client):
    """Verifies that the execute method forwards the query to the gql client."""
    _mock_client_class, mock_client_instance = mock_gql_client
    mock_client_instance.execute.return_value = {"data": {"ok": True}}

    client = GlpiGraphQLClient("http://example.com", "app", "sess")
    result = client.execute("query { ping }", {"a": 1})

    mock_client_instance.execute.assert_called_once_with(ANY, variable_values={"a": 1})
    assert result == {"data": {"ok": True}}
