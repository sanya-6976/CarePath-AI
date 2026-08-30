"""Structured Logging Configuration.
Configures structlog for structured logging across CarePath AI.
"""
import logging
import sys
import structlog

_ROOT_LOGGER_NAME = "carepath_ai"


def setup_logging():
    """Initializes structlog and standard logging sinks."""
    try:
        from app.core.config import settings
        debug = getattr(settings, "DEBUG", True)
    except Exception:
        debug = True

    logging_level = logging.DEBUG if debug else logging.INFO

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    processors = shared_processors + [
        structlog.processors.JSONRenderer()
    ]

    try:
        structlog.configure(
            processors=processors,
            logger_factory=structlog.PrintLoggerFactory(),
            wrapper_class=structlog.make_filtering_bound_logger(logging_level),
            cache_logger_on_first_use=True,
        )
    except Exception:
        pass


setup_logging()


def get_logger(name: str = _ROOT_LOGGER_NAME):
    """Returns a structlog logger instance supporting keyword arguments."""
    return structlog.get_logger(name)


logger = get_logger(_ROOT_LOGGER_NAME)


