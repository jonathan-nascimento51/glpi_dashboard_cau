"""Helpers for creating and linking GLPI documents."""

from __future__ import annotations

import json
from pathlib import Path

from aiohttp import FormData
from backend.domain.exceptions import GLPIAPIError
from backend.infrastructure.glpi.glpi_session import GLPISession


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
    file_handle = file_path.open("rb")
    form.add_field(
        "filename",
        file_handle,
        filename=file_path.name,
        content_type="application/octet-stream",
    )

    try:
        data = await session.post_form("Document", form)
    finally:
        file_handle.close()

    doc_id = data.get("id")
    if doc_id is None:
        raise GLPIAPIError(0, "Document creation response missing 'id'", data)
    return int(doc_id)


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
