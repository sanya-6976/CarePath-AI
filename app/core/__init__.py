"""Core Infrastructure Package.

Exposes the primary infrastructure symbols so that callers can do::

    from app.core import settings, get_logger, MedicalAIException

instead of importing from individual submodules.
"""
from app.core.config import settings
from app.core.logging import logger, get_logger
from app.core.exceptions import (
    MedicalAIException,
    OCRExtractionError,
    DICOMProcessingError,
    BioNERException,
    RAGRetrievalError,
    ServiceUnavailableError,
    InputValidationError,
    ModelInferenceError,
    http_status_for,
)
from app.core.validation import (
    validate_image_bytes,
    validate_text_input,
    validate_top_k,
)

__all__ = [
    "settings",
    "logger",
    "get_logger",
    "MedicalAIException",
    "OCRExtractionError",
    "DICOMProcessingError",
    "BioNERException",
    "RAGRetrievalError",
    "ServiceUnavailableError",
    "InputValidationError",
    "ModelInferenceError",
    "http_status_for",
    "validate_image_bytes",
    "validate_text_input",
    "validate_top_k",
]

