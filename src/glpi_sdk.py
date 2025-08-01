from __future__ import annotations

from collections.abc import Iterable

from py_glpi.connection import GLPISession
from py_glpi.resources.tickets import Tickets

#: Mapping of ticket status names to their corresponding numeric codes in the GLPI system.
STATUS_CODES: Dict[str, int] = {"new": 1, "pending": 4, "solved": 5}


def count_by_levels(
    session: GLPISession, levels: Iterable[str]
) -> Dict[str, Dict[str, int]]:
    """Return status counts for each level using ``py_glpi``.

    Parameters
    ----------
    session:
        Established ``GLPISession``.
    levels:
        Iterable of level identifiers (e.g. N1, N2).
    """
    tickets = Tickets(session)
    results: Dict[str, Dict[str, int]] = {}

    for level in levels:
        level_counts: Dict[str, int] = {}
        for status_name, status_id in STATUS_CODES.items():
            criteria = [
                {"field": "groups_id_assign", "searchtype": "equals", "value": level},
                {"link": "AND"},
                {"field": "status", "searchtype": "equals", "value": status_id},
            ]
            level_counts[status_name] = tickets.count(criteria=criteria)
        results[level] = level_counts

    return results
