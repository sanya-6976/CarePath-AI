"""Custom Application Exceptions.

All CarePath AI exceptions extend :class:`MedicalAIException`.  Each
exception carries an ``error_code`` string that is surfaced in API error
responses so that clients can distinguish between error categories without
parsing human-readable messages.

HTTP Mapping
------------
Use :func:`http_status_for` in FastAPI exception handlers to translate a
:class:`MedicalAIException` into the appropriate HTTP status code.
"""
from __future__ import annotations


class MedicalAIException(Exception):
    """Base exception for CarePath AI platform.

    Parameters
    ----------
    message:
        Human-readable description of the error.
    error_code:
        Machine-readable error code string (snake_case).  Defaults to
        ``"internal_error"``.
    """

    def __init__(self, message: str, error_code: str = "internal_error") -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


# ---------------------------------------------------------------------------
# Existing exception types (unchanged — preserving all existing call sites)
# ---------------------------------------------------------------------------


class OCRExtractionError(MedicalAIException):
    """Raised when OCR document parsing fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="ocr_extraction_error")


class DICOMProcessingError(MedicalAIException):
    """Raised when DICOM parsing or image analysis fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="dicom_processing_error")


class BioNERException(MedicalAIException):
    """Raised when entity extraction fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="bio_ner_error")


class RAGRetrievalError(MedicalAIException):
    """Raised when vector database search fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="rag_retrieval_error")


# ---------------------------------------------------------------------------
# New exception types
# ---------------------------------------------------------------------------


class ServiceUnavailableError(MedicalAIException):
    """Raised when a required AI backend (model, DB, API) is not reachable.

    Use this when the engine itself could not initialise or a downstream
    dependency is down, so the caller can distinguish between an inference
    error and a service availability issue.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="service_unavailable")


class InputValidationError(MedicalAIException):
    """Raised when user-supplied input fails domain validation.

    Examples: empty image bytes, text exceeding maximum length, ``top_k``
    out of the valid range.  This maps to HTTP 422 (Unprocessable Entity).
    """

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="input_validation_error")


class ModelInferenceError(MedicalAIException):
    """Raised when a model inference step fails unexpectedly.

    Use this to wrap low-level ML framework exceptions (PyTorch, EasyOCR,
    Gemini API) so that callers receive a consistent typed exception rather
    than a raw third-party error.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="model_inference_error")


# ---------------------------------------------------------------------------
# HTTP Status Mapping Helper
# ---------------------------------------------------------------------------

# HTTP status integers used below — plain literals are version-stable and avoid
# transitive Starlette deprecation warnings from symbolic constant names.
_HTTP_422 = 422  # Unprocessable Content (formerly Unprocessable Entity)
_HTTP_500 = 500  # Internal Server Error
_HTTP_503 = 503  # Service Unavailable

_STATUS_MAP: dict[type, int] = {
    InputValidationError: _HTTP_422,
    ServiceUnavailableError: _HTTP_503,
    OCRExtractionError: _HTTP_422,
    DICOMProcessingError: _HTTP_422,
    BioNERException: _HTTP_500,
    RAGRetrievalError: _HTTP_500,
    ModelInferenceError: _HTTP_500,
    MedicalAIException: _HTTP_500,
}


def http_status_for(exc: MedicalAIException) -> int:
    """Return the appropriate HTTP status code for a :class:`MedicalAIException`.

    Walks the MRO of *exc* so that subclasses resolve correctly even when
    not explicitly listed in the mapping table.

    Parameters
    ----------
    exc:
        The exception instance to classify.

    Returns
    -------
    int
        An HTTP status code (e.g. ``422``, ``503``, ``500``).
    """
    for cls in type(exc).__mro__:
        if cls in _STATUS_MAP:
            return _STATUS_MAP[cls]
    return _HTTP_500

