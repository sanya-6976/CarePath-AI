"""Strict Pydantic Schemas for Personalized Care-Plan Generation."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class CarePlanCategory(str, Enum):
    """Origin and classification of care plan guidance."""

    DOCTOR_STATED_PLAN = "DOCTOR_STATED_PLAN"
    PATIENT_CONFIRMED_ACTION = "PATIENT_CONFIRMED_ACTION"
    AI_GENERATED_SUPPORT = "AI_GENERATED_SUPPORT"


class CarePlanPriority(str, Enum):
    """Evidence-grounded care plan item priority."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class CarePlanItem(BaseModel):
    """Single actionable care-plan guidance item."""

    model_config = ConfigDict(extra="forbid")

    category: CarePlanCategory
    description: str = Field(min_length=1)
    priority: CarePlanPriority = Field(default=CarePlanPriority.MEDIUM)
    source_type: str = Field(min_length=1, description="Source origin e.g. CLINICIAN_NOTE, PATIENT_VERIFICATION, AI_ORGANIZATION")
    supporting_evidence: List[str] = Field(default_factory=list)
    doctor_stated: bool = Field(default=False)
    patient_verified: bool = Field(default=False)
    confidence: float = Field(ge=0.0, le=1.0)
    uncertainty: Optional[str] = None


class PersonalizedCarePlanRequest(BaseModel):
    """Input payload for generating personalized care plan."""

    model_config = ConfigDict(extra="forbid")

    patient_summary: Optional[Dict[str, Any]] = None
    clinical_extraction: Optional[Dict[str, Any]] = None
    treatment_responses: List[Dict[str, Any]] = Field(default_factory=list)
    follow_up_intelligence: Optional[Dict[str, Any]] = None
    doctor_feedback: Optional[Dict[str, Any]] = None
    patient_preferences: List[str] = Field(default_factory=list)


class PersonalizedCarePlanReport(BaseModel):
    """Master output payload for personalized care plan."""

    model_config = ConfigDict(extra="forbid")

    patient_context: str = Field(min_length=1)
    care_plan_items: List[CarePlanItem] = Field(default_factory=list)
    doctor_stated_plan: List[str] = Field(default_factory=list)
    monitoring_items: List[str] = Field(default_factory=list)
    follow_up_items: List[str] = Field(default_factory=list)
    pending_information: List[str] = Field(default_factory=list)
    questions_for_doctor: List[str] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    overall_confidence: float = Field(ge=0.0, le=1.0)
    disclaimer: str = Field(
        default=(
            "CONTINUITY OF CARE & ORGANIZATIONAL SUPPORT ONLY. "
            "THIS CARE PLAN DOES NOT PRESCRIBE, CHANGE, OR STOP MEDICATIONS. "
            "AI SUGGESTIONS MUST NEVER BE REPRESENTED AS MEDICAL ORDERS OR DOCTOR INSTRUCTIONS."
        )
    )
    processing_time_seconds: float = Field(ge=0.0)
