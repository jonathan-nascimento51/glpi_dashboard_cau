from __future__ import annotations

import logging
from typing import Optional

from backend.core.settings import (
    CLIENT_TIMEOUT_SECONDS,
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
    USE_MOCK_DATA,
    VERIFY_SSL,
)
from backend.infrastructure.glpi.glpi_session import Credentials, GLPISession
from shared.dto import TicketTranslator

from .mapping_service import MappingService

logger = logging.getLogger(__name__)


def create_glpi_session() -> Optional[GLPISession]:
    """Instantiate :class:`GLPISession` using settings."""

    try:
        creds = Credentials(
            app_token=GLPI_APP_TOKEN,
            user_token=GLPI_USER_TOKEN,
            username=GLPI_USERNAME,
            password=GLPI_PASSWORD,
        )
        return GLPISession(
            GLPI_BASE_URL,
            creds,
            verify_ssl=VERIFY_SSL,
            timeout=CLIENT_TIMEOUT_SECONDS,
        )
    except Exception as exc:  # pragma: no cover - init failures
        logger.exception("GLPI session init failed: %s", exc)
        return None


def create_ticket_translator() -> Optional[TicketTranslator]:
    """Return a translator for GLPI tickets or ``None`` when offline."""

    if USE_MOCK_DATA:
        return None

    session = create_glpi_session()
    if session is None:
        return None

    mapper = MappingService(session)
    return TicketTranslator(mapper)
