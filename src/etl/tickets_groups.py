from __future__ import annotations

"""Pipeline to collect tickets and their group assignments."""

import datetime as dt
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from src.api.glpi_api import GLPIClient

log = logging.getLogger(__name__)

STATUS = {1: "New", 2: "Processing", 3: "Assigned", 5: "Solved", 6: "Closed"}


def collect_tickets_with_groups(
    start: str, end: str, client: Optional[GLPIClient] = None
) -> pd.DataFrame:
    """Return a dataframe with ticket/group/user assignments."""

    client = client or GLPIClient()
    client.start_session()

    criteria = [
        {"field": "date", "searchtype": "morethan", "value": start},
        {"link": "AND"},
        {"field": "date", "searchtype": "lessthan", "value": end},
    ]
    forcedisplay = [1, 2, 12, 15]
    tickets = client.search(
        "Ticket",
        criteria=criteria,
        forcedisplay_ids=forcedisplay,
    )

    rows: list[dict] = []
    for t in tickets:
        tid = int(t["id"])
        ticket_assigns = client.search(
            "Ticket_User",
            criteria=[
                {"field": "tickets_id", "value": tid},
                {"link": "AND"},
                {"field": "type", "value": 2},
            ],
        )
        for assign in ticket_assigns:
            group_id = assign.get("groups_id")
            user_id = assign.get("users_id")
            group_name = None
            user_name = None
            if group_id:
                g = client.get(
                    f"Group/{group_id}",
                    params={"forcedisplay[0]": "completename"},
                ).json()
                group_name = g.get("completename")
            elif user_id:
                u = client.get(
                    f"User/{user_id}", params={"forcedisplay[0]": "name"}
                ).json()
                user_name = u.get("name")
                group_id = u.get("groups_id")
                if group_id:
                    g = client.get(
                        f"Group/{group_id}",
                        params={"forcedisplay[0]": "completename"},
                    ).json()
                    group_name = g.get("completename")
            rows.append(
                {
                    "ticket_id": tid,
                    "title": t.get("name"),
                    "status": STATUS.get(
                        int(t.get("status", 0)),
                        str(t.get("status")),
                    ),
                    "opened_at": t.get("date"),
                    "group_id": group_id,
                    "group_name": group_name,
                    "user_id": user_id,
                    "user_name": user_name,
                }
            )
    df = pd.DataFrame(rows)
    if not df.empty:
        df["opened_at"] = pd.to_datetime(df["opened_at"], errors="coerce")
    return df


def save_parquet(df: pd.DataFrame, path: Path | str) -> Path:
    """Persist dataframe to Parquet."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    return path


def pipeline(start: str, end: str, outfile: Optional[str] = None) -> Path:
    """Collect data and persist to ``datasets`` directory."""
    outfile = outfile or (
        f"datasets/tickets_groups_{dt.date.today():%Y%m%d}.parquet"
    )
    df = collect_tickets_with_groups(start, end)
    return save_parquet(df, outfile)
