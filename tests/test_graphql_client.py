from src.backend.adapters.graphql_client import GlpiGraphQLClient


def test_client_initialization():
    client = GlpiGraphQLClient(
        "http://example.com/apirest.php",
        app_token="APP",
        session_token="SESS",
    )
    transport = client._client.transport
    assert transport.url == "http://example.com/apirest.php/graphql"
    assert transport.kwargs["headers"]["App-Token"] == "APP"
    assert transport.kwargs["headers"]["Session-Token"] == "SESS"


def test_execute_forwards_query(monkeypatch):
    client = GlpiGraphQLClient(
        "http://example.com/apirest.php",
        app_token="APP",
        session_token="SESS",
    )

    called = {}

    def fake_execute(doc, variable_values=None):
        called["query"] = doc.loc.source.body
        called["vars"] = variable_values
        return {"data": {"ok": True}}

    monkeypatch.setattr(client._client, "execute", fake_execute)
    result = client.execute("query { ping }", {"a": 1})

    assert called["query"] == "query { ping }"
    assert called["vars"] == {"a": 1}
    assert result == {"data": {"ok": True}}
