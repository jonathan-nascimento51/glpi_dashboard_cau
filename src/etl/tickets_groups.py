from __future__ import annotations

"""Pipeline to collect tickets and their group assignments."""

import datetime as dt
import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import os

import asyncio
from glpi_dashboard.services.glpi_session import GLPISession, Credentials
from glpi_dashboard.config.settings import (
    GLPI_BASE_URL,
    GLPI_APP_TOKEN,
    GLPI_USERNAME,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    FETCH_PAGE_SIZE,
)

log = logging.getLogger(__name__)

STATUS = {1: "New", 2: "Processing", 3: "Assigned", 5: "Solved", 6: "Closed"}


async def collect_tickets_with_groups(
    start: str, end: str, session: Optional[GLPISession] = None
) -> pd.DataFrame:
    """Return a dataframe with ticket/group/user assignments."""

    base_url = os.getenv("GLPI_BASE_URL", GLPI_BASE_URL)
    app_token = os.getenv("GLPI_APP_TOKEN", GLPI_APP_TOKEN)
    user_token = os.getenv("GLPI_USER_TOKEN", GLPI_USER_TOKEN)
    username = os.getenv("GLPI_USERNAME", GLPI_USERNAME)
    password = os.getenv("GLPI_PASSWORD", GLPI_PASSWORD)

    created = False
    if session is None:
        creds = Credentials(
            app_token=app_token,
            user_token=user_token,
            username=username,
            password=password,
        )
        session = GLPISession(base_url, creds)
        created = True

    async def get_all(item: str, **params: dict) -> list[dict]:
        params = {**params, "expand_dropdowns": 1}
        endpoint = f"search/{item}" if not item.startswith("search/") else item
        results: list[dict] = []
        offset = 0
        while True:
            page_params = {
                **params,
                "range": f"{offset}-{offset + FETCH_PAGE_SIZE - 1}",
            }
            data = await session.get(endpoint, params=page_params)
            page = data.get("data", data)
            if isinstance(page, dict):
                page = [page]
            results.extend(page)
            if len(page) < FETCH_PAGE_SIZE:
                break
            offset += FETCH_PAGE_SIZE
        return results

    async def fetch(endpoint: str, params: Optional[dict] = None):
        if endpoint.startswith("search/"):
            item = endpoint.split("/", 1)[1]
            return await get_all(item, **(params or {}))
        data = await session.get(endpoint, params=params)
        if isinstance(data, dict):
            inner = data.get("data")
            if (
                isinstance(inner, list)
                and inner
                and not any(
                    k in inner[0]
                    for k in [
                        "name",
                        "completename",
                        "users_id",
                        "groups_id",
                    ]
                )
            ):
                data = await session.get(endpoint, params=params)
        return data

    async def collect() -> pd.DataFrame:

        criteria = [
            {"field": "date", "searchtype": "morethan", "value": start},
            {"link": "AND"},
            {"field": "date", "searchtype": "lessthan", "value": end},
        ]
        forcedisplay = [1, 2, 12, 15]
        rows: list[dict] = []
        offset = 0
        while True:
            params = {
                "criteria": criteria,
                "forcedisplay": forcedisplay,
                "range": f"{offset}-{offset + FETCH_PAGE_SIZE - 1}",
            }
            tickets = await fetch("search/Ticket", params=params)
            if isinstance(tickets, dict):
                tickets = tickets.get("data", tickets)
            if not tickets:
                break
            for t in tickets:
                tid = int(t["id"])
                ticket_assigns = await fetch(
                    "search/Ticket_User",
                    params={
                        "criteria": [
                            {"field": "tickets_id", "value": tid},
                            {"link": "AND"},
                            {"field": "type", "value": 2},
                        ]
                    },
                )
                if isinstance(ticket_assigns, dict):
                    ticket_assigns = ticket_assigns.get("data", ticket_assigns)
                for assign in ticket_assigns:
                    group_id = assign.get("groups_id")
                    user_id = assign.get("users_id")
                    group_name = None
                    user_name = None
                    if group_id:
                        g = await fetch(
                            f"Group/{group_id}",
                            params={"forcedisplay[0]": "completename"},
                        )
                        group_name = g.get("completename")
                    elif user_id:
                        u = await fetch(
                            f"User/{user_id}",
                            params={"forcedisplay[0]": "name"},
                        )
                        user_name = u.get("name")
                        group_id = u.get("groups_id")
                        if group_id:
                            g = await fetch(
                                f"Group/{group_id}",
                                params={"forcedisplay[0]": "completename"},
                            )
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
            if len(tickets) < FETCH_PAGE_SIZE:
                break
            offset += FETCH_PAGE_SIZE
        df = pd.DataFrame(rows)
        if not df.empty:
            df["opened_at"] = pd.to_datetime(df["opened_at"], errors="coerce")
        return df

    if created:
        async with session:
            return await collect()
    return await collect()


def save_parquet(df: pd.DataFrame, path: Path | str) -> Path:
    """Persist dataframe to Parquet."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    return path


def pipeline(start: str, end: str, outfile: Optional[str] = None) -> Path:
    """Collect data and persist to ``datasets`` directory."""
    outfile = outfile or (f"datasets/tickets_groups_{dt.date.today():%Y%m%d}.parquet")
    df = asyncio.run(collect_tickets_with_groups(start, end))
    return save_parquet(df, outfile)
