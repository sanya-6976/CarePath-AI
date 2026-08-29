"""Canonical Shared AI Domain Models for CarePath AI.

These are internal value objects used across all AI modules.  They are
**not** FastAPI response models — those live in ``app/schemas/``.  The
separation exists so that service logic can be unit-tested independently
of the HTTP layer.

Design principles
-----------------
- Immutable after construction (``model_config = ConfigDict(frozen=True)``).
- All fields have explicit types; no untyped ``Any``.
- Enum-backed category/severity fields to prevent magic strings.
- Pydantic v2 validators enforce domain invariants at construction time.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class EntityCategory(str, Enum):
    """Controlled vocabulary for medical entity categories."""

    SYMPTOM = "SYMPTOM"
    MEDICATION = "MEDICATION"
    DIAGNOSIS = "DIAGNOSIS"
    ANATOMY = "ANATOMY"
    PROCEDURE = "PROCEDURE"
    LAB_METRIC = "LAB_METRIC"
    UNKNOWN = "UNKNOWN"


class SeverityLevel(str, Enum):
    """Clinical severity classification."""

    NORMAL = "NORMAL"
    MILD = "MILD"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"
    CRITICAL = "CRITICAL"


class FindingType(str, Enum):
    """Type discriminator for AIFinding objects."""

    IMAGING = "IMAGING"
    LAB = "LAB"
    CLINICAL_NLP = "CLINICAL_NLP"
    OCR_EXTRACTED = "OCR_EXTRACTED"
    SYNTHESISED = "SYNTHESISED"


class InsightType(str, Enum):
    """Classifies the nature of a ClinicalInsight."""

    DIFFERENTIAL_DIAGNOSIS = "DIFFERENTIAL_DIAGNOSIS"
    CARE_PATH = "CARE_PATH"
    DRUG_INTERACTION = "DRUG_INTERACTION"
    RISK_STRATIFICATION = "RISK_STRATIFICATION"
    GUIDELINE_RECOMMENDATION = "GUIDELINE_RECOMMENDATION"


# ---------------------------------------------------------------------------
# Core Value Objects
# ---------------------------------------------------------------------------


class PatientContext(BaseModel):
    """Optional demographic and clinical context carried through a request.

    All fields are optional so that modules can operate without a complete
    patient record.  ``patient_id`` should be treated as an opaque
    identifier and MUST NOT contain real PHI in production without
    appropriate de-identification controls in the calling layer.
    """

    model_config = ConfigDict(frozen=True)

    patient_id: Optional[str] = Field(
        default=None,
        description="Opaque patient identifier (de-identified in production).",
        max_length=128,
    )
    age: Optional[int] = Field(
        default=None,
        ge=0,
        le=150,
        description="Patient age in years.",
    )
    gender: Optional[str] = Field(
        default=None,
        description="Patient biological sex or gender identity (free text).",
        max_length=64,
    )
    chief_complaint: Optional[str] = Field(
        default=None,
        description="Free-text chief complaint or reason for visit.",
        max_length=1024,
    )
    relevant_history: Optional[str] = Field(
        default=None,
        description="Relevant past medical history, allergies, or comorbidities.",
        max_length=4096,
    )


class ConfidenceScore(BaseModel):
    """Typed confidence representation produced by any AI inference step.

    ``value`` is always in [0.0, 1.0].  ``method`` identifies the inference
    approach (e.g. ``"regex"``, ``"neural"``, ``"heuristic"``,
    ``"ensemble"``).  ``calibrated`` signals whether temperature scaling or
    Platt scaling was applied.
    """

    model_config = ConfigDict(frozen=True)

    value: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence probability in the range [0, 1].",
    )
    method: str = Field(
        default="heuristic",
        description="Inference method that produced this score.",
        max_length=64,
    )
    calibrated: bool = Field(
        default=False,
        description="Whether the score has been post-hoc calibrated.",
    )

    @field_validator("value")
    @classmethod
    def _value_precision(cls, v: float) -> float:
        """Round to 4 decimal places to avoid floating-point noise in JSON."""
        return round(v, 4)


class Evidence(BaseModel):
    """A single piece of supporting evidence retrieved by RAG or extracted by NLP.

    ``relevance_score`` is the cosine-similarity or keyword-rank score
    returned by the vector database / keyword ranker.
    """

    model_config = ConfigDict(frozen=True)

    source: str = Field(
        ...,
        description="Canonical source name (e.g. 'ATS/IDSA Guidelines 2024').",
        min_length=1,
        max_length=256,
    )
    content: str = Field(
        ...,
        description="Verbatim excerpt or paraphrase from the source.",
        min_length=1,
    )
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Relevance score of this evidence to the query.",
    )
    citation: Optional[str] = Field(
        default=None,
        description="Human-readable citation string (e.g. 'Author et al., Journal, Year').",
        max_length=512,
    )


class MedicalEntityRecord(BaseModel):
    """Normalised medical entity shared across NLP and OCR extraction outputs.

    This is the internal representation.  It maps 1-to-1 with
    ``app.schemas.nlp.MedicalEntity`` but is decoupled from the HTTP layer
    so that service-level code can consume it without importing FastAPI schemas.
    """

    model_config = ConfigDict(frozen=True)

    text: str = Field(
        ...,
        description="Surface form of the extracted entity.",
        min_length=1,
        max_length=512,
    )
    category: EntityCategory = Field(
        ...,
        description="Semantic category of the entity.",
    )
    icd10_code: Optional[str] = Field(
        default=None,
        description="ICD-10 code if available (e.g. 'J18.9').",
        max_length=16,
    )
    snomed_ct: Optional[str] = Field(
        default=None,
        description="SNOMED-CT concept identifier if available.",
        max_length=64,
    )
    negated: bool = Field(
        default=False,
        description="True when the entity is preceded by a negation cue.",
    )
    confidence: ConfidenceScore = Field(
        ...,
        description="Confidence score for this entity extraction.",
    )


class AIFinding(BaseModel):
    """A discrete clinical finding produced by any AI module.

    Used internally to aggregate findings from Vision, OCR, and NLP
    before final synthesis in the CarePathEngine.
    """

    model_config = ConfigDict(frozen=True)

    finding_type: FindingType = Field(
        ...,
        description="Module origin of this finding.",
    )
    description: str = Field(
        ...,
        description="Human-readable description of the finding.",
        min_length=1,
        max_length=2048,
    )
    confidence: ConfidenceScore = Field(
        ...,
        description="Overall confidence in this finding.",
    )
    severity: SeverityLevel = Field(
        default=SeverityLevel.NORMAL,
        description="Clinical severity classification.",
    )
    supporting_evidence: List[Evidence] = Field(
        default_factory=list,
        description="Evidence items that support this finding.",
    )


class ClinicalInsight(BaseModel):
    """Top-level synthesised insight produced by the CarePathEngine.

    Each insight represents one coherent recommendation, diagnosis
    differential, or risk stratification item.
    """

    model_config = ConfigDict(frozen=True)

    insight_type: InsightType = Field(
        ...,
        description="Classification of this insight.",
    )
    summary: str = Field(
        ...,
        description="Concise summary of the insight (1-3 sentences).",
        min_length=1,
        max_length=2048,
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Ordered list of actionable recommendations.",
    )
    confidence: ConfidenceScore = Field(
        ...,
        description="Overall confidence in this clinical insight.",
    )
    evidence: List[Evidence] = Field(
        default_factory=list,
        description="Supporting evidence for this insight.",
    )
    disclaimer: str = Field(
        default=(
            "FOR CLINICAL DECISION SUPPORT ONLY. "
            "All insights must be verified by a licensed healthcare provider."
        ),
        description="Mandatory clinical disclaimer.",
    )


class ClinicalTimelineEvent(BaseModel):
    """Chronological clinical timeline event."""

    model_config = ConfigDict(frozen=True)

    event_date: Optional[str] = Field(
        default=None,
        description="ISO date or relative timeframe (e.g. '2026-08-10', 'Day 3').",
        max_length=64,
    )
    category: str = Field(
        default="GENERAL",
        description="Event classification (e.g. SYMPTOM_ONSET, LAB_TEST, SURGERY, MEDICATION, GENERAL).",
        max_length=64,
    )
    title: str = Field(
        ...,
        description="Short title summarizing the event.",
        min_length=1,
        max_length=256,
    )
    details: str = Field(
        default="",
        description="Detailed description of the clinical event.",
        max_length=2048,
    )

