"""Utilities for building the Dash-based GLPI dashboard.

This subpackage groups the layout, components and callbacks used to render the
interactive service desk dashboard.
"""

from .layout import build_layout, render_dashboard

__all__ = ["render_dashboard", "build_layout"]
