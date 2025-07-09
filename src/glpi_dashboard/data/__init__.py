"""Compatibility exports for legacy data imports.

New code should import modules from :mod:`backend.db` or :mod:`backend.services`.
"""

import sys
from importlib import import_module

from backend.db import database
from backend.utils import pipeline

sys.modules[__name__ + ".tickets_groups"] = import_module(
    "backend.services.tickets_groups"
)

__all__ = ["database", "pipeline", "tickets_groups"]
