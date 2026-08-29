"""Strict Pydantic Schemas for Treatment-Response Analysis."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ResponseClassification(str, Enum):
    """Classification of treatment response based on empirical evidence."""

    IMPROVED = "IMPROVED"
    NO_CLEAR_RESPONSE = "NO_CLEAR_RESPONSE"
    WORSENED = "WORSENED"
    MIXED_RESPONSE = "MIXED_RESPONSE"
    STABLE = "STABLE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class CausalityLevel(str, Enum):
    """Causal link relationship between treatment and outcome."""

    TEMPORAL_ASSOCIATION = "TEMPORAL_ASSOCIATION"
    DOCUMENTED_CLINICAL_ASSOCIATION = "DOCUMENTED_CLINICAL_ASSOCIATION"
    UNKNOWN = "UNKNOWN"


class SymptomComparison(BaseModel):
    """Before vs after symptom status comparison."""

    model_config = ConfigDict(extra="forbid")

    symptom_name: str = Field(min_length=1)
    baseline_status: str = Field(min_length=1, description="Status prior to treatment")
    post_treatment_status: str = Field(min_length=1, description="Status after treatment")
    observed_change: str = Field(description="IMPROVED, WORSENED, UNCHANGED, UNCERTAIN")
    evidence: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)


class LabComparison(BaseModel):
    """Before vs after laboratory metric comparison."""

    model_config = ConfigDict(extra="forbid")

    metric_name: str = Field(min_length=1)
    baseline_value: Optional[str] = None
    baseline_unit: Optional[str] = None
    post_treatment_value: Optional[str] = None
    post_treatment_unit: Optional[str] = None
    direction_of_change: str = Field(description="DECREASED, INCREASED, UNCHANGED, NOT_COMPARABLE")
    evidence: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)


class TreatmentResponseItem(BaseModel):
    """Structured response evaluation for a single treatment event."""

    model_config = ConfigDict(extra="forbid")

    treatment_name: str = Field(min_length=1)
    treatment_type: str = Field(default="MEDICATION", description="MEDICATION, PROCEDURE, THERAPY")
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    indication: Optional[str] = None
    baseline_observations: List[str] = Field(default_factory=list)
    follow_up_observations: List[str] = Field(default_factory=list)
    symptom_comparisons: List[SymptomComparison] = Field(default_factory=list)
    lab_comparisons: List[LabComparison] = Field(default_factory=list)
    response_classification: ResponseClassification = Field(default=ResponseClassification.INSUFFICIENT_DATA)
    evidence: List[str] = Field(default_factory=list)
    causality_level: CausalityLevel = Field(default=CausalityLevel.UNKNOWN)
    multiple_contributors: bool = Field(default=False, description="True if concurrent treatments overlap")
    conflicts: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    data_sufficiency: bool = Field(default=True)
    source_references: List[str] = Field(default_factory=list)


class TreatmentResponseRequest(BaseModel):
    """Input request for evaluating treatment response."""

    model_config = ConfigDict(extra="forbid")

    treatment_events: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of treatment dicts e.g. [{'treatment_name': '...', 'start_date': '...'}]",
    )
    symptoms: List[Dict[str, Any]] = Field(default_factory=list)
    labs: List[Dict[str, Any]] = Field(default_factory=list)
    doctor_feedback: Optional[str] = None
    clinical_notes: Optional[str] = None
    timeline_events: List[Dict[str, Any]] = Field(default_factory=list)


class TreatmentResponseReport(BaseModel):
    """Response payload for treatment-response analysis."""

    model_config = ConfigDict(extra="forbid")

    analyzed_treatments: List[TreatmentResponseItem] = Field(default_factory=list)
    insufficient_data_cases: List[str] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    overall_confidence: float = Field(ge=0.0, le=1.0)
    disclaimer: str = Field(
        default=(
            "EVIDENCE-ANALYSIS ONLY. THIS SUBSYSTEM DESCRIBES DOCUMENTED OBSERVED OUTCOMES "
            "AND DOES NOT ISSUE PRESCRIPTIONS, RECOMMEND TREATMENT CHANGES, OR ESTABLISH UNPROVEN CAUSALITY."
        )
    )
    processing_time_seconds: float = Field(ge=0.0)
