import logging
import os


def setup_logging(level: str | int | None = None) -> None:
    """Configure basic logging once."""
    if level is None:
        env_level = os.getenv("LOG_LEVEL", "INFO")
        level = getattr(logging, env_level.upper(), logging.INFO)

    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
