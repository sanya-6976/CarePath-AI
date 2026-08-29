from __future__ import annotations

import io
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import cv2
import numpy as np
from PIL import Image, ImageOps
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import (
    InputValidationError,
    ModelInferenceError,
    OCRExtractionError,
    ServiceUnavailableError,
)
from app.core.interfaces import (
    ServiceAvailability,
    ServiceHealthStatus,
    TextExtractionService,
)
from app.core.logging import get_logger
from app.core.validation import validate_image_bytes
from app.schemas.ocr import (
    BoundingBox,
    ExtractedTextLine,
    LabMetricItem,
    OCRResult,
    PrescriptionItem,
)

logger = get_logger(__name__)


@dataclass(frozen=True)
class _OCRPage:
    """Normalized OCR input page."""

    page_number: int
    image: np.ndarray


@dataclass(frozen=True)
class _OCRLine:
    """Backend-independent OCR line representation."""

    text: str
    confidence: float
    bbox: BoundingBox | None
    page_number: int


class OCREngine(TextExtractionService):
    """
    Production medical-document OCR engine.

    Supported inputs:
    - PNG, JPEG, WEBP, BMP, TIFF
    - PDF documents

    OCR backends:
    - Tesseract
    - EasyOCR

    The backend is selected lazily and can be configured through
    ``OCR_BACKEND``. No synthetic or hardcoded OCR output is ever produced.
    """

    _SERVICE_NAME = "CarePath OCR Engine"
    _SERVICE_VERSION = "1.0.0"

    _SUPPORTED_IMAGE_FORMATS = {
        "PNG",
        "JPEG",
        "WEBP",
        "BMP",
        "TIFF",
    }

    _SUPPORTED_MIME_TYPES = {
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/bmp",
        "image/tiff",
        "application/pdf",
    }

    def __init__(self) -> None:
        self._backend_name: str | None = None
        self._backend: Any | None = None
        self._backend_error: str | None = None
        self._initialize_backend()

    # ------------------------------------------------------------------
    # Public service interface
    # ------------------------------------------------------------------

    def health_check(self) -> ServiceHealthStatus:
        """Return the current OCR service readiness."""
        if self._backend_name is None:
            return ServiceHealthStatus(
                availability=ServiceAvailability.UNAVAILABLE,
                backend=None,
                message=self._backend_error or "No OCR backend is available.",
            )

        return ServiceHealthStatus(
            availability=ServiceAvailability.AVAILABLE,
            backend=self._backend_name,
            message=f"{self._backend_name} OCR backend is ready.",
        )

    def get_service_info(self) -> dict[str, Any]:
        """Return non-sensitive service metadata."""
        health = self.health_check()

        return {
            "name": self._SERVICE_NAME,
            "version": self._SERVICE_VERSION,
            "status": health.availability.value,
            "backend": self._backend_name,
            "supported_formats": sorted(self._SUPPORTED_IMAGE_FORMATS)
            + ["PDF"],
            "max_upload_size_mb": settings.MAX_UPLOAD_SIZE_MB,
            "min_confidence_threshold": settings.OCR_MIN_CONFIDENCE,
        }

    # ------------------------------------------------------------------
    # Main extraction entry point
    # ------------------------------------------------------------------

    def extract_text(
        self,
        document_bytes: bytes,
        filename: str = "document",
        content_type: str | None = None,
    ) -> OCRResult:
        """
        Extract text from an image or PDF document.

        Raises:
            InputValidationError: Invalid or unsupported input.
            ServiceUnavailableError: No OCR backend is available.
            OCRExtractionError: Document decoding/extraction failure.
            ModelInferenceError: OCR backend inference failure.
        """
        started_at = time.perf_counter()

        self._validate_input(
            document_bytes=document_bytes,
            filename=filename,
            content_type=content_type,
        )

        if self._backend_name is None:
            raise ServiceUnavailableError(
                self._backend_error
                or "No supported OCR backend is available."
            )

        try:
            pages = self._load_pages(
                document_bytes=document_bytes,
                filename=filename,
                content_type=content_type,
            )
        except (InputValidationError, OCRExtractionError):
            raise
        except Exception as exc:
            logger.exception("Failed to prepare OCR document: %s", filename)
            raise OCRExtractionError(
                f"Unable to prepare document '{filename}' for OCR."
            ) from exc

        if not pages:
            raise OCRExtractionError(
                f"Document '{filename}' contains no readable pages."
            )

        extracted_lines: list[_OCRLine] = []

        for page in pages:
            try:
                processed_image = self._preprocess_image(page.image)
                page_lines = self._run_backend(
                    processed_image,
                    page_number=page.page_number,
                )
                extracted_lines.extend(page_lines)
            except ModelInferenceError:
                raise
            except Exception as exc:
                logger.exception(
                    "OCR inference failed for %s page %d",
                    filename,
                    page.page_number,
                )
                raise ModelInferenceError(
                    f"OCR inference failed on page {page.page_number} "
                    f"of '{filename}'."
                ) from exc

        normalized_lines = self._normalize_lines(extracted_lines)

        if not normalized_lines:
            raise OCRExtractionError(
                f"No readable text was extracted from '{filename}'."
            )

        raw_text = self._build_raw_text(normalized_lines)
        confidence = self._calculate_overall_confidence(normalized_lines)

        document_type = self._classify_document_type(raw_text)
        lab_metrics = self._parse_lab_metrics(raw_text)
        prescriptions = self._parse_prescriptions(raw_text)

        elapsed = round(time.perf_counter() - started_at, 4)

        try:
            return OCRResult(
                filename=filename,
                document_type=document_type,
                raw_text=raw_text,
                confidence_score=confidence,
                page_count=len(pages),
                lab_metrics=lab_metrics,
                prescriptions=prescriptions,
                text_lines=[
                    ExtractedTextLine(
                        text=line.text,
                        confidence=line.confidence,
                        bbox=line.bbox,
                        page_number=line.page_number,
                    )
                    for line in normalized_lines
                ],
                processing_time_seconds=elapsed,
            )
        except ValidationError as exc:
            logger.exception("Invalid OCR result generated for %s", filename)
            raise OCRExtractionError(
                "OCR extraction completed but produced an invalid result."
            ) from exc

    # ------------------------------------------------------------------
    # Backend initialization
    # ------------------------------------------------------------------

    def _initialize_backend(self) -> None:
        """
        Initialize the configured OCR backend lazily.

        ``OCR_BACKEND=auto`` tries Tesseract first and EasyOCR second.
        """
        configured_backend = getattr(
            settings,
            "OCR_BACKEND",
            "auto",
        ).strip().lower()

        if configured_backend not in {"auto", "tesseract", "easyocr"}:
            self._backend_error = (
                f"Unsupported OCR_BACKEND '{configured_backend}'. "
                "Expected auto, tesseract, or easyocr."
            )
            logger.error(self._backend_error)
            return

        candidates = (
            ["tesseract", "easyocr"]
            if configured_backend == "auto"
            else [configured_backend]
        )

        errors: list[str] = []

        for backend_name in candidates:
            try:
                if backend_name == "tesseract":
                    self._initialize_tesseract()
                else:
                    self._initialize_easyocr()

                self._backend_error = None
                logger.info(
                    "OCR backend initialized: %s",
                    self._backend_name,
                )
                return

            except Exception as exc:
                message = f"{backend_name}: {exc}"
                errors.append(message)
                if configured_backend == "auto" and backend_name == "tesseract":
                    logger.debug("Tesseract not available in auto mode, falling back to EasyOCR: %s", message)
                else:
                    logger.warning(
                        "Unable to initialize OCR backend: %s",
                        message,
                    )

        self._backend_name = None
        self._backend = None
        self._backend_error = (
            "No OCR backend could be initialized. "
            + " | ".join(errors)
        )

    def _initialize_tesseract(self) -> None:
        """Initialize and validate the Tesseract executable."""
        import pytesseract

        configured_path = getattr(
            settings,
            "TESSERACT_CMD",
            "",
        ).strip()

        if configured_path:
            pytesseract.pytesseract.tesseract_cmd = configured_path

        version = pytesseract.get_tesseract_version()

        self._backend_name = "tesseract"
        self._backend = pytesseract

        logger.info(
            "Tesseract initialized successfully: %s",
            version,
        )

    def _initialize_easyocr(self) -> None:
        """Initialize EasyOCR without exposing its implementation to callers."""
        import easyocr

        languages = getattr(
            settings,
            "EASYOCR_LANGUAGES",
            "en",
        )

        language_list = [
            language.strip()
            for language in languages.split(",")
            if language.strip()
        ]

        if not language_list:
            language_list = ["en"]

        gpu = bool(
            getattr(
                settings,
                "EASYOCR_GPU",
                False,
            )
        )

        self._backend = easyocr.Reader(
            language_list,
            gpu=gpu,
            verbose=False,
        )
        self._backend_name = "easyocr"

    # ------------------------------------------------------------------
    # Input validation
    # ------------------------------------------------------------------

    def _validate_input(
        self,
        document_bytes: bytes,
        filename: str,
        content_type: str | None,
    ) -> None:
        if not document_bytes:
            raise InputValidationError("The uploaded document is empty.")

        if not filename or not filename.strip():
            raise InputValidationError("A valid filename is required.")

        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

        if len(document_bytes) > max_bytes:
            raise InputValidationError(
                f"Document exceeds the maximum allowed size of "
                f"{settings.MAX_UPLOAD_SIZE_MB} MB."
            )

        normalized_content_type = (
            content_type.lower().split(";")[0].strip()
            if content_type
            else None
        )

        extension = Path(filename).suffix.lower()

        if normalized_content_type in self._SUPPORTED_MIME_TYPES:
            return

        if extension in {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".bmp",
            ".tif",
            ".tiff",
            ".pdf",
        }:
            return

        raise InputValidationError(
            f"Unsupported document format: '{extension or 'unknown'}'."
        )

    # ------------------------------------------------------------------
    # Document loading
    # ------------------------------------------------------------------

    def _load_pages(
        self,
        document_bytes: bytes,
        filename: str,
        content_type: str | None,
    ) -> list[_OCRPage]:
        is_pdf = self._is_pdf(
            document_bytes=document_bytes,
            filename=filename,
            content_type=content_type,
        )

        if is_pdf:
            return self._load_pdf_pages(document_bytes)

        try:
            image = Image.open(io.BytesIO(document_bytes))
            image.load()

            if image.format not in self._SUPPORTED_IMAGE_FORMATS:
                raise InputValidationError(
                    f"Unsupported image format: {image.format or 'unknown'}."
                )

            image = ImageOps.exif_transpose(image).convert("RGB")
            image_np = np.asarray(image)

            if image_np.size == 0:
                raise OCRExtractionError("Image contains no pixel data.")

            return [
                _OCRPage(
                    page_number=1,
                    image=image_np,
                )
            ]

        except InputValidationError:
            raise
        except Exception as exc:
            raise OCRExtractionError(
                f"Unable to decode image document '{filename}'."
            ) from exc

    def _load_pdf_pages(self, document_bytes: bytes) -> list[_OCRPage]:
        """Render every PDF page using PyMuPDF."""
        try:
            import fitz
        except ImportError as exc:
            raise ServiceUnavailableError(
                "PyMuPDF is required for PDF OCR processing."
            ) from exc

        try:
            document = fitz.open(
                stream=document_bytes,
                filetype="pdf",
            )
        except Exception as exc:
            raise OCRExtractionError(
                "Unable to open the uploaded PDF document."
            ) from exc

        pages: list[_OCRPage] = []

        try:
            if document.page_count == 0:
                raise OCRExtractionError(
                    "The uploaded PDF contains no pages."
                )

            max_pages = getattr(
                settings,
                "OCR_MAX_PDF_PAGES",
                50,
            )

            if document.page_count > max_pages:
                raise InputValidationError(
                    f"PDF contains {document.page_count} pages, exceeding "
                    f"the maximum allowed {max_pages} pages."
                )

            dpi = max(
                150,
                min(
                    int(getattr(settings, "OCR_PDF_DPI", 200)),
                    400,
                ),
            )

            scale = dpi / 72.0
            matrix = fitz.Matrix(scale, scale)

            for index in range(document.page_count):
                page = document.load_page(index)
                pixmap = page.get_pixmap(
                    matrix=matrix,
                    alpha=False,
                )

                image = Image.frombytes(
                    "RGB",
                    [pixmap.width, pixmap.height],
                    pixmap.samples,
                )

                pages.append(
                    _OCRPage(
                        page_number=index + 1,
                        image=np.asarray(image),
                    )
                )

            return pages

        finally:
            document.close()

    @staticmethod
    def _is_pdf(
        document_bytes: bytes,
        filename: str,
        content_type: str | None,
    ) -> bool:
        if content_type:
            normalized = content_type.lower().split(";")[0].strip()
            if normalized == "application/pdf":
                return True

        if document_bytes[:4] == b"%PDF":
            return True

        return Path(filename).suffix.lower() == ".pdf"

    # ------------------------------------------------------------------
    # Image preprocessing
    # ------------------------------------------------------------------

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Normalize document images before OCR.

        Processing:
        - RGB/BGR normalization
        - grayscale conversion
        - denoising
        - contrast enhancement
        - adaptive thresholding when appropriate
        """
        if image is None or image.size == 0:
            raise OCRExtractionError("OCR received an empty image.")

        if image.ndim == 2:
            gray = image
        elif image.ndim == 3 and image.shape[2] >= 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            raise OCRExtractionError(
                f"Unsupported image shape for OCR: {image.shape}."
            )

        gray = cv2.normalize(
            gray,
            None,
            alpha=0,
            beta=255,
            norm_type=cv2.NORM_MINMAX,
        )

        denoised = cv2.fastNlMeansDenoising(
            gray,
            None,
            h=10,
            templateWindowSize=7,
            searchWindowSize=21,
        )

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8),
        )

        enhanced = clahe.apply(denoised)

        thresholded = cv2.adaptiveThreshold(
            enhanced,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            11,
        )

        return thresholded

    # ------------------------------------------------------------------
    # OCR backend execution
    # ------------------------------------------------------------------

    def _run_backend(
        self,
        image: np.ndarray,
        page_number: int,
    ) -> list[_OCRLine]:
        if self._backend_name == "tesseract":
            return self._run_tesseract(
                image=image,
                page_number=page_number,
            )

        if self._backend_name == "easyocr":
            return self._run_easyocr(
                image=image,
                page_number=page_number,
            )

        raise ServiceUnavailableError(
            "OCR backend is not initialized."
        )

    def _run_tesseract(
        self,
        image: np.ndarray,
        page_number: int,
    ) -> list[_OCRLine]:
        import pandas as pd
        from pytesseract import Output

        try:
            data = self._backend.image_to_data(
                image,
                output_type=Output.DICT,
                config="--oem 3 --psm 6",
            )
        except Exception as exc:
            raise ModelInferenceError(
                "Tesseract OCR inference failed."
            ) from exc

        lines: list[_OCRLine] = []

        for index, text_value in enumerate(data.get("text", [])):
            text = str(text_value).strip()

            if not text:
                continue

            try:
                confidence = float(data["conf"][index])
            except (KeyError, ValueError, TypeError):
                confidence = 0.0

            if confidence < 0:
                continue

            confidence /= 100.0

            x = int(data["left"][index])
            y = int(data["top"][index])
            width = int(data["width"][index])
            height = int(data["height"][index])

            bbox = BoundingBox(
                x_min=max(0, x),
                y_min=max(0, y),
                x_max=max(x, x + width),
                y_max=max(y, y + height),
            )

            lines.append(
                _OCRLine(
                    text=text,
                    confidence=round(
                        min(max(confidence, 0.0), 1.0),
                        4,
                    ),
                    bbox=bbox,
                    page_number=page_number,
                )
            )

        # Explicitly keep pandas imported only for environments where
        # pytesseract's dataframe-backed output is configured; avoid unused
        # runtime coupling otherwise.
        _ = pd

        return lines

    def _run_easyocr(
        self,
        image: np.ndarray,
        page_number: int,
    ) -> list[_OCRLine]:
        try:
            results = self._backend.readtext(
                image,
                detail=1,
                paragraph=False,
                width_ths=0.7,
                text_threshold=0.5,
                low_text=0.3,
                link_threshold=0.3,
            )
        except Exception as exc:
            raise ModelInferenceError(
                "EasyOCR inference failed."
            ) from exc

        lines: list[_OCRLine] = []

        for result in results:
            if len(result) != 3:
                continue

            coordinates, text, probability = result

            text = str(text).strip()

            if not text:
                continue

            bbox = self._easyocr_bbox(coordinates)

            lines.append(
                _OCRLine(
                    text=text,
                    confidence=round(
                        min(max(float(probability), 0.0), 1.0),
                        4,
                    ),
                    bbox=bbox,
                    page_number=page_number,
                )
            )

        return lines

    @staticmethod
    def _easyocr_bbox(
        coordinates: Sequence[Sequence[float]],
    ) -> BoundingBox | None:
        if len(coordinates) < 4:
            return None

        try:
            xs = [float(point[0]) for point in coordinates]
            ys = [float(point[1]) for point in coordinates]

            return BoundingBox(
                x_min=max(0, int(min(xs))),
                y_min=max(0, int(min(ys))),
                x_max=max(0, int(max(xs))),
                y_max=max(0, int(max(ys))),
            )
        except (TypeError, ValueError, IndexError):
            return None

    # ------------------------------------------------------------------
    # Output normalization
    # ------------------------------------------------------------------

    def _normalize_lines(
        self,
        lines: Iterable[_OCRLine],
    ) -> list[_OCRLine]:
        normalized: list[_OCRLine] = []

        for line in lines:
            text = " ".join(line.text.split()).strip()

            if not text:
                continue

            normalized.append(
                _OCRLine(
                    text=text,
                    confidence=round(
                        min(max(line.confidence, 0.0), 1.0),
                        4,
                    ),
                    bbox=line.bbox,
                    page_number=line.page_number,
                )
            )

        normalized.sort(
            key=lambda item: (
                item.page_number,
                item.bbox.y_min if item.bbox else 0,
                item.bbox.x_min if item.bbox else 0,
            )
        )

        return normalized

    @staticmethod
    def _build_raw_text(lines: Sequence[_OCRLine]) -> str:
        current_page: int | None = None
        output: list[str] = []

        for line in lines:
            if current_page is not None and line.page_number != current_page:
                output.append("")

            output.append(line.text)
            current_page = line.page_number

        return "\n".join(output).strip()

    def _calculate_overall_confidence(
        self,
        lines: Sequence[_OCRLine],
    ) -> float:
        if not lines:
            return 0.0

        weighted_sum = 0.0
        total_weight = 0.0

        for line in lines:
            weight = max(len(line.text), 1)
            weighted_sum += line.confidence * weight
            total_weight += weight

        return round(
            min(max(weighted_sum / total_weight, 0.0), 1.0),
            4,
        )

    # ------------------------------------------------------------------
    # Document classification
    # ------------------------------------------------------------------

    @staticmethod
    def _classify_document_type(text: str) -> str:
        """
        Classify document type using explicit textual signals.

        This is document classification only; it does not diagnose disease.
        """
        normalized = text.lower()

        prescription_score = 0
        lab_score = 0
        clinical_score = 0

        prescription_terms = (
            "prescription",
            "rx",
            "dosage",
            "dose",
            "tablet",
            "capsule",
            "take ",
            "frequency",
        )

        lab_terms = (
            "laboratory",
            "lab report",
            "reference range",
            "hemoglobin",
            "haemoglobin",
            "glucose",
            "creatinine",
            "platelet",
            "wbc",
            "rbc",
            "cholesterol",
        )

        clinical_terms = (
            "clinical note",
            "medical history",
            "assessment",
            "diagnosis",
            "discharge summary",
            "chief complaint",
            "examination",
        )

        prescription_score = sum(
            1 for term in prescription_terms if term in normalized
        )
        lab_score = sum(
            1 for term in lab_terms if term in normalized
        )
        clinical_score = sum(
            1 for term in clinical_terms if term in normalized
        )

        scores = {
            "PRESCRIPTION": prescription_score,
            "LAB_REPORT": lab_score,
            "CLINICAL_NOTE": clinical_score,
        }

        best_type, best_score = max(
            scores.items(),
            key=lambda item: item[1],
        )

        if best_score > 0:
            return best_type

        return "GENERAL_MEDICAL"

    # ------------------------------------------------------------------
    # Structured medical extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_lab_metrics(text: str) -> list[LabMetricItem]:
        """
        Extract clearly formatted laboratory values.

        This parser intentionally remains conservative. It only returns
        values that match known lab-test patterns and never invents values.
        """
        import re

        patterns = (
            re.compile(
                r"""
                \b
                (?P<name>
                    Hemoglobin|Haemoglobin|Hb|HbA1c|WBC|RBC|
                    Glucose|Cholesterol|Creatinine|Platelets|
                    Platelet\s+Count
                )
                \s*[:=]?\s*
                (?P<value>\d+(?:\.\d+)?)
                \s*
                (?P<unit>
                    g/dL|mg/dL|mmol/L|mg/L|µmol/L|umol/L|%
                    |10\^?3/uL|10\^?9/L|/uL
                )?
                """,
                re.IGNORECASE | re.VERBOSE,
            ),
        )

        results: list[LabMetricItem] = []

        for pattern in patterns:
            for match in pattern.finditer(text):
                name = " ".join(match.group("name").split())
                value = match.group("value")
                unit = match.group("unit") or None

                results.append(
                    LabMetricItem(
                        test_name=name,
                        value=value,
                        unit=unit,
                    )
                )

        return results

    @staticmethod
    def _parse_prescriptions(text: str) -> list[PrescriptionItem]:
        """
        Extract explicitly formatted medication/dosage/frequency patterns.

        This parser does not infer medication instructions that are absent
        from the OCR text.
        """
        import re

        pattern = re.compile(
            r"""
            (?:
                \bRx\b\s*[:\-]?\s*
            )?
            (?P<drug>[A-Za-z][A-Za-z0-9\-/]*(?:\s+[A-Za-z][A-Za-z0-9\-/]*){0,3})
            \s+
            (?P<dosage>
                \d+(?:\.\d+)?
                \s*
                (?:mg|g|mcg|µg|ml|mL|mg/mL)
            )
            (?:
                \s*
                (?P<frequency>
                    once\s+daily|
                    twice\s+daily|
                    three\s+times\s+daily|
                    thrice\s+daily|
                    every\s+\d+\s+(?:hours?|hrs?)|
                    b\.?i\.?d\.?|
                    t\.?i\.?d\.?|
                    q\.?d\.?
                )
            )?
            (?:
                \s*
                (?:for\s+)
                (?P<duration>\d+\s+(?:days?|weeks?))
            )?
            """,
            re.IGNORECASE | re.VERBOSE,
        )

        results: list[PrescriptionItem] = []
        seen: set[tuple[str, str, str, str]] = set()

        blocked_terms = {
            "hemoglobin",
            "haemoglobin",
            "glucose",
            "creatinine",
            "cholesterol",
            "platelets",
            "wbc",
            "rbc",
            "laboratory",
            "reference",
            "normal",
        }

        for match in pattern.finditer(text):
            drug = " ".join(match.group("drug").split()).strip()

            if drug.lower() in blocked_terms:
                continue

            dosage = (match.group("dosage") or "").strip()
            frequency = (
                (match.group("frequency") or "").strip()
                or None
            )
            duration = (
                (match.group("duration") or "").strip()
                or None
            )

            key = (
                drug.lower(),
                dosage.lower(),
                (frequency or "").lower(),
                (duration or "").lower(),
            )

            if key in seen:
                continue

            seen.add(key)

            results.append(
                PrescriptionItem(
                    drug_name=drug,
                    dosage=dosage,
                    frequency=frequency,
                    duration=duration,
                )
            )

        return results


ocr_engine = OCREngine()