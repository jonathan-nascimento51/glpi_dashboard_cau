"""Helpers for creating and linking GLPI documents."""

from __future__ import annotations

import json
from pathlib import Path

from aiohttp import FormData
from backend.infrastructure.glpi.glpi_session import GLPISession


async def _post_form(session: GLPISession, endpoint: str, form: FormData) -> dict:
    """Send a multipart/form-data POST request using the underlying session."""
    session._init_aiohttp_session()  # type: ignore[attr-defined]
    assert session._session is not None  # type: ignore[attr-defined]

    headers = session._build_request_headers(None)  # type: ignore[attr-defined]
    headers.pop("Content-Type", None)
    request_kwargs = {
        "headers": headers,
        "data": form,
        "proxy": session.proxy,
        "timeout": session._resolve_timeout(),  # type: ignore[attr-defined]
    }
    if not session.verify_ssl:
        request_kwargs["ssl"] = False
    elif session.ssl_ctx is not None:
        request_kwargs["ssl"] = session.ssl_ctx

    async with session._session.post(  # type: ignore[attr-defined]
        f"{session.base_url}/{endpoint}",
        **request_kwargs,
    ) as resp:
        resp.raise_for_status()
        return await resp.json()


async def create_document(
    session: GLPISession,
    name: str,
    file_path: Path,
    linked_item: tuple[str, int] | None = None,
) -> int:
    """Upload a document to GLPI and return its ID."""
    manifest: dict[str, dict[str, object]] = {"input": {"name": name}}
    if linked_item is not None:
        itemtype, items_id = linked_item
        manifest["input"].update({"itemtype": itemtype, "items_id": items_id})

    form = FormData()
    form.add_field(
        "uploadManifest", json.dumps(manifest), content_type="application/json"
    )
    form.add_field(
        "filename",
        file_path.read_bytes(),
        filename=file_path.name,
        content_type="application/octet-stream",
    )

    data = await _post_form(session, "Document", form)
    if "id" not in data:
        raise ValueError(f"API response does not contain 'id': {data}")
    return int(data["id"])


async def link_document(
    session: GLPISession, document_id: int, itemtype: str, items_id: int
) -> None:
    """Link an existing document to another GLPI item."""
    payload = {
        "input": {
            "documents_id": document_id,
            "itemtype": itemtype,
            "items_id": items_id,
        }
    }
    await session.post("Document_Item", json_data=payload)
