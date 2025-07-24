import json
import time
from typing import Any, Dict, List, Optional

import requests
from backend.core.settings import GLPI_APP_TOKEN, GLPI_BASE_URL
from backend.infrastructure.glpi.glpi_auth import GLPIAuthClient
from backend.infrastructure.glpi.glpi_client import SearchCriteriaBuilder
from shared.utils.logging import get_logger

from glpi_http_utils import http_request_with_retry

logger = get_logger(__name__)


class GLPITicketClient:
    """Simple client to fetch GLPI tickets using REST search."""

    def __init__(
        self,
        base_url: str = GLPI_BASE_URL,
        app_token: str = GLPI_APP_TOKEN,
        auth_client: Optional[GLPIAuthClient] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.app_token = app_token
        self.auth_client = auth_client or GLPIAuthClient(base_url, app_token)
        self.session = session or requests.Session()

    def _build_params(
        self, filters: Optional[Dict[str, str]], page: int, page_size: int
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"range": f"{(page-1)*page_size}-{page*page_size-1}"}
        if filters:
            builder = SearchCriteriaBuilder()
            for field, value in filters.items():
                builder.add(field, value)
            params.update(builder.build())
        return params

    def list_tickets(
        self,
        filters: Optional[Dict[str, str]] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> List[Dict[str, Any]]:
        """Return tickets matching ``filters`` using GLPI search."""

        token = self.auth_client.get_session_token()
        params = self._build_params(filters, page, page_size)
        headers = {
            "App-Token": self.app_token,
            "Session-Token": token,
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/search/Ticket"
        log_data = {"page": page, "page_size": page_size, "filters": filters}
        start = time.perf_counter()
        resp = http_request_with_retry(
            self.session,
            "GET",
            url,
            headers=headers,
            params=params,
            auth_client=self.auth_client,
        )
        resp.raise_for_status()
        data = resp.json()
        tickets: List[Dict[str, Any]] = data.get("data", data)
        duration = time.perf_counter() - start
        logger.info(
            json.dumps(
                {
                    "event": "list_tickets",
                    **log_data,
                    "count": len(tickets),
                    "duration": duration,
                }
            )
        )
        return tickets
