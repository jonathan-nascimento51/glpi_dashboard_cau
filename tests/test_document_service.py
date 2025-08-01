import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.application.document_service import create_document, link_document
from backend.domain.exceptions import GLPIAPIError
from backend.infrastructure.glpi.glpi_session import GLPISession
from tests.helpers import make_cm


class DummySession(GLPISession):
    """GLPISession stub exposing an aiohttp-like client."""

    def __init__(self):
        # Avoid parent initialization logic
        self.base_url = "http://example.com/apirest.php"
        self.proxy = None
        self.verify_ssl = True
        self.ssl_ctx = None
        self._session = MagicMock()
        self._session.post = MagicMock(
            side_effect=lambda *a, **k: make_cm(201, {"id": 5})
        )

    def _init_aiohttp_session(self) -> None:
        pass

    def _build_request_headers(self, headers=None):
        hdrs = {"App-Token": "app", "Content-Type": "application/json"}
        if headers:
            hdrs |= headers
        return hdrs

    def _resolve_timeout(self):
        class T:  # simple stand-in for aiohttp.ClientTimeout
            pass

        return T()


@pytest.mark.asyncio
async def test_create_document_posts_multipart(tmp_path):
    file_path = tmp_path / "doc.txt"
    file_path.write_text("data")
    session = DummySession()

    doc_id = await create_document(session, "doc", file_path, None)

    session._session.post.assert_called_once()
    args, kwargs = session._session.post.call_args
    assert args[0].endswith("/Document")
    data = kwargs["data"]
    fields = {f[0]["name"]: f[2] for f in getattr(data, "_fields", [])}
    assert "uploadManifest" in fields
    assert json.loads(fields["uploadManifest"]) == {"input": {"name": "doc"}}
    assert "filename" in fields
    assert Path(fields["filename"].name) == file_path
    assert doc_id == 5


@pytest.mark.asyncio
async def test_create_document_missing_id(tmp_path):
    file_path = tmp_path / "doc.txt"
    file_path.write_text("data")
    session = DummySession()
    session._session.post = MagicMock(return_value=make_cm(201, {}))

    with pytest.raises(GLPIAPIError):
        await create_document(session, "doc", file_path, None)


@pytest.mark.asyncio
async def test_link_document_calls_post():
    session = AsyncMock(spec=GLPISession)

    await link_document(session, 2, "Ticket", 99)

    session.post.assert_awaited_once_with(
        "Document_Item",
        json_data={"input": {"documents_id": 2, "itemtype": "Ticket", "items_id": 99}},
    )
