"""Pipeline for collecting tickets with group and user info."""

from __future__ import annotations

import logging
from typing import List, Optional

import pandas as pd

from src.api.glpi_api import GLPIClient, STATUS


def collect_tickets_with_groups(
    start: str,
    end: str,
    client: Optional[GLPIClient] = None,
) -> pd.DataFrame:
    """Fetch tickets and assignments between two dates."""

    client = client or GLPIClient()
    logging.info("Collecting tickets from %s to %s", start, end)

    criteria = [
        {"field": "date", "searchtype": "morethan", "value": start},
        {"link": "AND"},
        {"field": "date", "searchtype": "lessthan", "value": end},
    ]
    tickets = client.search(
        "Ticket",
        criteria=criteria,
        forcedisplay_ids=[1, 2, 12, 15],
    )
    rows: List[dict] = []
    for ticket in tickets:
        ticket_id = ticket["id"]
        assignments = client.search(
            "Ticket_User",
            criteria=[
                {
                    "field": "tickets_id",
                    "searchtype": "equals",
                    "value": ticket_id,
                },
                {"link": "AND"},
                {"field": "type", "searchtype": "equals", "value": 2},
            ],
        )
        for assign in assignments:
            user_id = assign.get("users_id")
            user = client.get(
                f"User/{user_id}", params={"forcedisplay[0]": "name"}
            ).json()
            group_id = assign.get("groups_id") or user.get("groups_id")
            group_name = None
            if group_id:
                group = client.get(
                    f"Group/{group_id}",
                    params={"forcedisplay[0]": "completename"},
                ).json()
                group_name = group.get("completename")
            rows.append(
                {
                    "ticket_id": ticket_id,
                    "title": ticket.get("name"),
                    "status": STATUS.get(
                        int(ticket.get("status", 0)), str(ticket.get("status"))
                    ),
                    "opened_at": ticket.get("date"),
                    "group_id": group_id,
                    "group_name": group_name,
                    "user_id": user_id,
                    "user_name": user.get("name"),
                }
            )
    df = pd.DataFrame(
        rows,
        columns=[
            "ticket_id",
            "title",
            "status",
            "opened_at",
            "group_id",
            "group_name",
            "user_id",
            "user_name",
        ],
    )
    return df
