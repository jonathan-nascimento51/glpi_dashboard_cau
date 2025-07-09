"""Pytest configuration for the project.

This ensures the project sources under ``src`` are available when tests are
imported as plugins and registers ``test_glpi_session`` as a plugin.
"""

import os
import sys

# Add the ``src`` directory to ``sys.path`` so modules like ``backend`` and
# ``frontend`` are discoverable without requiring an editable install.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

pytest_plugins = ("tests.test_glpi_session",)
