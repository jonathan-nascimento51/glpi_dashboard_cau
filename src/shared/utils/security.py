import logging
import os
import re

TOKEN_PATTERN = re.compile(r"^[A-Fa-f0-9]{40,}$")


def validate_glpi_tokens() -> None:
    """Validate required GLPI tokens are present and look valid."""
    logger = logging.getLogger(__name__)
    app_token = os.getenv("GLPI_APP_TOKEN")
    user_token = os.getenv("GLPI_USER_TOKEN")
    if not app_token or not user_token:
        logger.critical("GLPI tokens missing. Set GLPI_APP_TOKEN and GLPI_USER_TOKEN")
        raise SystemExit(1)
    if not TOKEN_PATTERN.match(app_token) or not TOKEN_PATTERN.match(user_token):
        logger.critical("GLPI token format appears invalid")
        raise SystemExit(1)
