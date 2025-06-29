import logging


def setup_logging(level: int = logging.INFO) -> None:
    """Configure basic logging once."""
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
