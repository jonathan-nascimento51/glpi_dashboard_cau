import logging
import sys
from types import FrameType

from loguru import logger
from opentelemetry.instrumentation.logging import LoggingInstrumentor


class InterceptHandler(logging.Handler):
    """Intercept standard logging and route to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: int | str = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame: FrameType | None = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(log_level: str = "INFO", serialize: bool = False) -> None:
    """Configure structured logging with Loguru and OpenTelemetry."""

    logger.remove()
    logger.add(
        sys.stderr,
        level=log_level.upper(),
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} | "
            "trace_id={extra[trace_id]} span_id={extra[span_id]} | {message}"
        ),
        serialize=serialize,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    LoggingInstrumentor().instrument(set_logging_format=True)

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    logger.info("Logging configurado com sucesso.")
