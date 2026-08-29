"""Strict Pydantic Schemas for Case-Specific Question Generation."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.patient_summary import PatientSummaryReport
from app.schemas.ocr import PrescriptionItem, LabMetricItem
from app.models.common import ClinicalTimelineEvent


class QuestionCategory(str, Enum):
    """Controlled vocabulary for case-specific question categories."""

    SYMPTOM_CLARIFICATION = "SYMPTOM_CLARIFICATION"
    HISTORY = "HISTORY"
    MEDICATION = "MEDICATION"
    TREATMENT_RESPONSE = "TREATMENT_RESPONSE"
    LAB_FINDING = "LAB_FINDING"
    DIAGNOSIS_CLARIFICATION = "DIAGNOSIS_CLARIFICATION"
    TIMELINE = "TIMELINE"
    MISSING_INFORMATION = "MISSING_INFORMATION"
    FOLLOW_UP = "FOLLOW_UP"


class QuestionPriority(str, Enum):
    """Clinical priority tier for generated questions."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class CaseSpecificQuestion(BaseModel):
    """A single, validated case-specific question for a doctor."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(
        min_length=5,
        description="Targeted, case-specific question to ask the doctor or patient.",
    )
    category: QuestionCategory = Field(
        description="Functional clinical category of the question.",
    )
    priority: QuestionPriority = Field(
        description="Clinical priority tier based on case risk and data urgency.",
    )
    reason: str = Field(
        min_length=5,
        description="Explicit explanation of why this question is relevant to THIS specific patient case.",
    )
    supporting_information: List[str] = Field(
        default_factory=list,
        description="Direct extracted facts or clinical context that triggered this question.",
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score representing relevance to the available patient data.",
    )


class CaseQuestionRequest(BaseModel):
    """Input payload to request case-specific question generation."""

    model_config = ConfigDict(extra="forbid")

    patient_summary: Optional[PatientSummaryReport] = None
    clinical_notes: Optional[str] = None
    symptoms: List[str] = Field(default_factory=list)
    diagnoses: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    lab_metrics: List[LabMetricItem] = Field(default_factory=list)
    prescriptions: List[PrescriptionItem] = Field(default_factory=list)
    timeline_events: List[ClinicalTimelineEvent] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    max_questions: int = Field(default=10, ge=1, le=50)


class CaseQuestionsReport(BaseModel):
    """Validated response payload containing case-specific questions."""

    model_config = ConfigDict(extra="forbid")

    questions: List[CaseSpecificQuestion] = Field(default_factory=list)
    total_question_count: int = Field(ge=0)
    source_context_summary: str = Field(
        min_length=1,
        description="Summary of patient context sources used for question generation.",
    )
    data_completeness: str = Field(
        default="COMPLETE",
        description="Assessment of patient data completeness: COMPLETE, PARTIAL, INSUFFICIENT.",
    )
    insufficient_data: bool = Field(default=False)
    disclaimer: str = Field(
        default=(
            "FOR CLINICAL DECISION SUPPORT AND CLARIFICATION ONLY. "
            "THESE QUESTIONS ARE GENERATED TO ASSIST CLINICAL NAVIGATION AND DO NOT CONSTITUTE MEDICAL DIAGNOSES OR TREATMENT ORDERS."
        )
    )
    processing_time_seconds: float = Field(ge=0.0)
