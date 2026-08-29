"""Production-grade clinical NLP and medical entity schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


EntityCategory = Literal[
    "SYMPTOM",
    "MEDICATION",
    "ANATOMY",
    "PROCEDURE",
    "DIAGNOSIS",
    "LAB_METRIC",
]


class EntitySpan(BaseModel):
    """Character offsets identifying where an entity came from."""

    model_config = ConfigDict(extra="forbid")

    start: int = Field(ge=0)
    end: int = Field(ge=0)

    @field_validator("end")
    @classmethod
    def validate_end(cls, value: int, info) -> int:
        start = info.data.get("start")
        if start is not None and value <= start:
            raise ValueError("Entity end offset must be greater than start.")
        return value


class MedicalEntity(BaseModel):
    """A clinically relevant entity extracted from source text."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)

    normalized_text: str | None = None

    category: EntityCategory

    icd10_code: str | None = None
    snomed_ct: str | None = None

    negated: bool = False

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    context: str | None = None

    span: EntitySpan | None = None

    source: Literal[
        "clinical_pattern",
        "medication_pattern",
        "lab_pattern",
        "nlp_model",
    ] = "clinical_pattern"


class MedicationInstruction(BaseModel):
    """Medication administration information explicitly present in text."""

    model_config = ConfigDict(extra="forbid")

    medication: str = Field(min_length=1)

    dosage: str | None = None
    route: str | None = None
    frequency: str | None = None
    duration: str | None = None

    negated: bool = False

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )


class BioNERResult(BaseModel):
    """Complete structured clinical NLP extraction result."""

    model_config = ConfigDict(extra="forbid")

    input_text: str = Field(min_length=1)

    entities: list[MedicalEntity] = Field(
        default_factory=list,
    )

    symptoms: list[str] = Field(
        default_factory=list,
    )

    medications: list[str] = Field(
        default_factory=list,
    )

    diagnoses: list[str] = Field(
        default_factory=list,
    )

    medication_instructions: list[MedicationInstruction] = Field(
        default_factory=list,
    )

    processing_time_seconds: float = Field(
        ge=0.0,
    )

    model_backend: str = "clinical_pattern_engine"

    overall_confidence: float = Field(
        ge=0.0,
        le=1.0,
    )