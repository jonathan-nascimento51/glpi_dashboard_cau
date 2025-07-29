from __future__ import annotations

from typing import Dict, List, Mapping, Optional

from py_glpi.connection import GLPISession  # type: ignore
from py_glpi.models import FilterCriteria, ResourceNotFound  # type: ignore
from py_glpi.resources.tickets import Ticket, Tickets  # type: ignore
from py_glpi.resources.users import Users  # type: ignore

from shared.dto import STATUS_MAP as STATUS_LABEL_MAP

# Map ticket status names to their numeric codes used by the GLPI API.
_STATUS_INV = {label.lower(): code for code, label in STATUS_LABEL_MAP.items()}
STATUS_MAP: Dict[str, int] = {
    "new": _STATUS_INV.get("new", 1),
    # The GLPI API uses "processing (assigned)" to represent tickets in the "processing" state.
    "processing": _STATUS_INV.get("processing (assigned)", 2),
    "waiting": _STATUS_INV.get("processing (planned)", 3),
    "solved": _STATUS_INV.get("solved", 5),
    "closed": _STATUS_INV.get("closed", 6),
}


class GLPISDK:
    """Synchronous helper that wraps :mod:`py_glpi` for common queries."""

    def __init__(
        self,
        api_url: str,
        app_token: str,
        *,
        user_token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        # GLPISession expects auth_type to be "basic" or "user_auth"
        # and user_token, user, password to be str (not None)
        if user_token:
            auth_type = "user_auth"
            _user_token = user_token
        else:
            auth_type = "basic"
            _user_token = ""
        _user = username if username is not None else ""
        _password = password if password is not None else ""
        self._client = GLPISession(
            api_url=api_url,
            app_token=app_token,
            auth_type=auth_type,
            user_token=_user_token,
            user=_user,
            password=_password,
        )
        self._tickets = Tickets(self._client)

    def list_tickets_by_level(self, level_field: str, level_value: int) -> List[Ticket]:
        """Return all tickets where ``level_field`` equals ``level_value``."""
        criteria = FilterCriteria(
            field_uid=level_field,
            operation="equals",
            value=level_value,
        )
        try:
            return self._tickets.search(criteria)
        except ResourceNotFound:
            return []

    def get_ticket_priority_and_requester(
        self, ticket_id: int
    ) -> Mapping[str, Optional[str]]:
        """Return priority label and requester name for ``ticket_id``."""
        try:
            ticket = self._tickets.get(ticket_id)
        except ResourceNotFound:
            return {"priority": None, "requester": None}

        priority = getattr(ticket, "priority_string", None)
        requester = None
        user_id = getattr(ticket, "users_id_recipient", None)
        if user_id:
            try:
                user = Users(self._client).get(user_id)
                requester = getattr(user, "name", None)
            except ResourceNotFound:
                requester = None
        return {"priority": priority, "requester": requester}

    def get_ticket_counts_by_level(
        self, level_field: str, levels: Mapping[str, int]
    ) -> Dict[str, Dict[str, int]]:
        """Return status counts for each level key/value pair."""
        results: Dict[str, Dict[str, int]] = {}
        for name, value in levels.items():
            tickets = self.list_tickets_by_level(level_field, value)
            status_list = [t.status for t in tickets]
            results[name] = {
                key: status_list.count(code) for key, code in STATUS_MAP.items()
            }
        return results
