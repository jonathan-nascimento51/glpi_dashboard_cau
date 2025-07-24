import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from backend.application.document_service import create_document, link_document
from backend.domain.exceptions import GLPIAPIError
from backend.infrastructure.glpi.glpi_session import GLPISession


class DummySession(GLPISession):
    """GLPISession stub exposing an aiohttp-like client."""

    def __init__(self):
        self.base_url = "http://example.com/apirest.php"
        self.post_form = AsyncMock(return_value={"id": 5})
        self.post = AsyncMock()


@pytest.mark.asyncio
async def test_create_document_posts_multipart(tmp_path):
    file_path = tmp_path / "doc.txt"
    file_path.write_text("data")
    session = DummySession()

    doc_id = await create_document(session, "doc", file_path, None)

    session.post_form.assert_awaited_once()
    call = session.post_form.await_args
    assert call is not None
    args, kwargs = call
    assert args[0] == "Document"
    form = args[1]
    fields = {f[0]["name"]: f[2] for f in getattr(form, "_fields", [])}
    assert fields["uploadManifest"] == json.dumps({"input": {"name": "doc"}})
    assert Path(fields["filename"].name) == file_path
    assert doc_id == 5


@pytest.mark.asyncio
async def test_create_document_missing_id(tmp_path):
    file_path = tmp_path / "doc.txt"
    file_path.write_text("data")
    session = DummySession()
    session.post_form.return_value = {}

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
