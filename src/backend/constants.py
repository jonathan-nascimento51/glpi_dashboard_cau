"""Shared constants for backend modules."""

from __future__ import annotations

from typing import Dict

# Mapping of service level names to GLPI group IDs
GROUP_IDS: Dict[str, int] = {
    "N1": 89,
    "N2": 90,
    "N3": 91,
    "N4": 92,
}

# Reverse mapping of GLPI group ID to service level label
GROUP_LABELS_BY_ID: Dict[int, str] = {gid: level for level, gid in GROUP_IDS.items()}

# Mapping of verbose GLPI status labels to canonical dashboard labels
STATUS_ALIAS: Dict[str, str] = {
    "processing (assigned)": "progress",
    "processing (planned)": "progress",
    "solved": "resolved",
    "closed": "resolved",
}

__all__ = ["GROUP_IDS", "GROUP_LABELS_BY_ID", "STATUS_ALIAS"]
