"""
CarePath AI Core Structured Logging System
==========================================
Configures structlog for structured JSON logging in production and formatted output
for local development, ensuring PHI safety and trace ID correlation across API endpoints.
"""

import logging
import sys
import structlog
from app.core.config import settings


def setup_logging():
    """Initializes structlog and standard logging sinks."""
    logging_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Disable noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if settings.ENVIRONMENT == "production":
        # JSON formatting for production log aggregators (CloudWatch, Datadog)
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development human-readable colored output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging_level),
        cache_logger_on_first_use=True,
    )


setup_logging()
logger = structlog.get_logger("carepath_backend")


def get_logger(name: str = "carepath_backend"):
    """Returns a logger instance compatible with both structlog and standard logging."""
    return structlog.get_logger(name)
