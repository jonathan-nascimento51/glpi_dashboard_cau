import logging
import sys

from loguru import logger
from opentelemetry.instrumentation.logging import LoggingInstrumentor


class InterceptHandler(logging.Handler):
    """Intercepta logs do sistema e redireciona para o Loguru."""

    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(log_level: str = "INFO", serialize: bool = False):
    """Configura o Loguru como logger principal com OpenTelemetry."""

    logger.remove()
    logger.add(
        sys.stderr,
        level=log_level.upper(),
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | "
            "trace_id={extra} span_id={extra} | {message}"
        ),
        serialize=serialize,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    LoggingInstrumentor().instrument(set_logging_format=True)

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    logger.info("Logging configurado com sucesso.")


# No ponto de entrada da aplicação (ex: main.py ou worker_api.py):
# from .log_config import setup_logging
# setup_logging(serialize=True)  # Em produção, usar JSON
