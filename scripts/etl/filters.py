"""Utility filters for GLPI ticket DataFrames."""

import pandas as pd


def by_status(df: pd.DataFrame, status: str) -> pd.DataFrame:
    """Return tickets matching a given status."""
    return df[df["status"].str.lower() == status.lower()]


def by_group(df: pd.DataFrame, group: str) -> pd.DataFrame:
    """Return tickets belonging to a specific group."""
    return df[df["group"].str.lower() == group.lower()]


def by_technician(df: pd.DataFrame, tech: str) -> pd.DataFrame:
    """Return tickets assigned to a specific technician."""
    return df[df["assigned_to"].str.lower() == tech.lower()]
