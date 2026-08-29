"""Structured Logging Configuration.

Provides a :func:`get_logger` factory that returns a named child logger
under the ``carepath_ai`` root.  The root logger's level is driven by
``settings.LOG_LEVEL`` so it can be adjusted via the ``LOG_LEVEL``
environment variable without code changes.

Backward compatibility
----------------------
The module-level ``logger`` assignment is retained so that any existing
import ``from app.core.logging import logger`` continues to resolve to the
``carepath_ai`` root logger without modification.
"""
import logging
import sys

# Defer settings import to avoid circular imports at module load time.
# ``settings`` is fully initialised by the time any service calls get_logger.
_ROOT_LOGGER_NAME = "carepath_ai"
_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _build_root_logger() -> logging.Logger:
    """Initialise the root ``carepath_ai`` logger exactly once."""
    root = logging.getLogger(_ROOT_LOGGER_NAME)
    if root.handlers:
        # Already configured — avoid adding duplicate handlers.
        return root

    # Resolve log level from settings (safe to import here; config has no
    # transitive dependency on logging).
    try:
        from app.core.config import settings as _settings
        level_str = _settings.LOG_LEVEL
    except Exception:
        level_str = "INFO"

    level = getattr(logging, level_str.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=_FORMAT, datefmt=_DATE_FORMAT))

    root.setLevel(level)
    root.addHandler(handler)
    root.propagate = False
    return root


def get_logger(name: str = _ROOT_LOGGER_NAME) -> logging.Logger:
    """Return a named child logger under the ``carepath_ai`` root.

    Parameters
    ----------
    name:
        Logger name.  Conventionally pass ``__name__`` from the calling
        module so that log records include the full module path, e.g.
        ``carepath_ai.app.services.vision_engine``.

    Returns
    -------
    logging.Logger
        A configured child logger that inherits the root handler.

    Examples
    --------
    >>> from app.core.logging import get_logger
    >>> log = get_logger(__name__)
    >>> log.info("Vision engine initialised.")
    """
    _build_root_logger()
    if name == _ROOT_LOGGER_NAME:
        return logging.getLogger(_ROOT_LOGGER_NAME)
    return logging.getLogger(f"{_ROOT_LOGGER_NAME}.{name}")


# ---------------------------------------------------------------------------
# Backward-compatible module-level binding
# Existing code: ``from app.core.logging import logger``  ← still works.
# ---------------------------------------------------------------------------
logger: logging.Logger = get_logger(_ROOT_LOGGER_NAME)


def setup_logging():
    """Initializes logging sink for backward compatibility."""
    _build_root_logger()

