"""Pydantic schemas for CarePath AI OCR and medical document extraction."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BoundingBox(BaseModel):
    """Axis-aligned bounding box around extracted text."""

    model_config = ConfigDict(extra="forbid")

    x_min: int = Field(ge=0)
    y_min: int = Field(ge=0)
    x_max: int = Field(ge=0)
    y_max: int = Field(ge=0)

    @field_validator("x_max")
    @classmethod
    def validate_x_bounds(cls, value: int, info) -> int:
        x_min = info.data.get("x_min")
        if x_min is not None and value < x_min:
            raise ValueError("x_max must be greater than or equal to x_min.")
        return value

    @field_validator("y_max")
    @classmethod
    def validate_y_bounds(cls, value: int, info) -> int:
        y_min = info.data.get("y_min")
        if y_min is not None and value < y_min:
            raise ValueError("y_max must be greater than or equal to y_min.")
        return value


class ExtractedTextLine(BaseModel):
    """A single OCR text segment with confidence and source page."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: Optional[BoundingBox] = None
    page_number: int = Field(default=1, ge=1)


class LabMetricItem(BaseModel):
    """A laboratory value explicitly extracted from a medical document."""

    model_config = ConfigDict(extra="forbid")

    test_name: str = Field(min_length=1)
    value: str = Field(min_length=1)
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    status: Optional[str] = None


class PrescriptionItem(BaseModel):
    """Medication information explicitly present in an OCR document."""

    model_config = ConfigDict(extra="forbid")

    drug_name: str = Field(min_length=1)
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None


class OCRResult(BaseModel):
    """Complete structured result produced by the OCR engine."""

    model_config = ConfigDict(extra="forbid")

    filename: str = Field(min_length=1)

    document_type: str = Field(
        min_length=1,
        description=(
            "Detected document category such as PRESCRIPTION, "
            "LAB_REPORT, CLINICAL_NOTE, or GENERAL_MEDICAL."
        ),
    )

    raw_text: str = Field(min_length=1)

    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
    )

    page_count: int = Field(
        default=1,
        ge=1,
    )

    lab_metrics: list[LabMetricItem] = Field(
        default_factory=list,
    )

    prescriptions: list[PrescriptionItem] = Field(
        default_factory=list,
    )

    text_lines: list[ExtractedTextLine] = Field(
        default_factory=list,
    )

    processing_time_seconds: float = Field(
        ge=0.0,
    )