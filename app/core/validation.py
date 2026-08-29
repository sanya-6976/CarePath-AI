"""Shared Input Validation Helpers for CarePath AI Services.

These functions are called at the top of every service method that accepts
user-supplied input.  They raise :class:`~app.core.exceptions.InputValidationError`
with a descriptive message so that the global FastAPI exception handler can
return a structured HTTP 422 response.

Design
------
- No third-party dependencies beyond the standard library and Pydantic.
- All functions are pure (no I/O, no side-effects).
- Each validator raises on failure; success is a silent no-op.
"""
from __future__ import annotations

from app.core.exceptions import InputValidationError


def validate_image_bytes(data: bytes, max_mb: int = 20) -> None:
    """Validate that *data* is a non-empty byte payload within the size limit.

    Parameters
    ----------
    data:
        Raw image or document bytes submitted by the caller.
    max_mb:
        Maximum allowed payload size in megabytes.  Defaults to 20 MB.

    Raises
    ------
    InputValidationError
        If *data* is empty or exceeds *max_mb*.
    """
    if not data:
        raise InputValidationError(
            "Image or document bytes must not be empty."
        )
    max_bytes = max_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise InputValidationError(
            f"Uploaded file size ({len(data) / 1024 / 1024:.1f} MB) exceeds "
            f"the maximum allowed size of {max_mb} MB."
        )


def validate_text_input(text: str, min_len: int = 1, max_len: int = 32_768) -> None:
    """Validate that *text* is within the required length bounds.

    Parameters
    ----------
    text:
        Clinical text string provided by the caller.
    min_len:
        Minimum acceptable character length (inclusive).  Defaults to 1.
    max_len:
        Maximum acceptable character length (inclusive).  Defaults to 32,768.

    Raises
    ------
    InputValidationError
        If *text* is blank, shorter than *min_len*, or longer than *max_len*.
    """
    if not isinstance(text, str):
        raise InputValidationError("Text input must be a string.")
    stripped = text.strip()
    if len(stripped) < min_len:
        raise InputValidationError(
            f"Text input must be at least {min_len} character(s) after stripping whitespace. "
            f"Got {len(stripped)} character(s)."
        )
    if len(text) > max_len:
        raise InputValidationError(
            f"Text input exceeds the maximum allowed length of {max_len} characters. "
            f"Got {len(text)} characters."
        )


def validate_top_k(k: int, min_k: int = 1, max_k: int = 10) -> None:
    """Validate that *k* is within the acceptable retrieval range.

    Parameters
    ----------
    k:
        The ``top_k`` integer value from a RAG query request.
    min_k:
        Minimum allowed value (inclusive).  Defaults to 1.
    max_k:
        Maximum allowed value (inclusive).  Defaults to 10.

    Raises
    ------
    InputValidationError
        If *k* is outside the [*min_k*, *max_k*] range.
    """
    if not isinstance(k, int):
        raise InputValidationError(
            f"top_k must be an integer, got {type(k).__name__}."
        )
    if not (min_k <= k <= max_k):
        raise InputValidationError(
            f"top_k must be between {min_k} and {max_k} inclusive, got {k}."
        )
