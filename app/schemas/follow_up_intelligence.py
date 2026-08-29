"""Strict Pydantic Schemas for Follow-Up Intelligence."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class FollowUpType(str, Enum):
    """Categorization of follow-up requirements."""

    REVIEW_CONSULTATION = "REVIEW_CONSULTATION"
    REPEAT_INVESTIGATION = "REPEAT_INVESTIGATION"
    MONITORING_REQUIREMENT = "MONITORING_REQUIREMENT"
    SYMPTOM_REASSESSMENT = "SYMPTOM_REASSESSMENT"
    TREATMENT_RESPONSE_REASSESSMENT = "TREATMENT_RESPONSE_REASSESSMENT"
    REFERRAL_FOLLOW_UP = "REFERRAL_FOLLOW_UP"
    PENDING_REPORT = "PENDING_REPORT"
    UNRESOLVED_ISSUE = "UNRESOLVED_ISSUE"


class FollowUpStatus(str, Enum):
    """Status classification of follow-up requirements."""

    UPCOMING = "UPCOMING"
    DUE = "DUE"
    OVERDUE = "OVERDUE"
    COMPLETED = "COMPLETED"
    PENDING_INFORMATION = "PENDING_INFORMATION"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    NO_FOLLOW_UP_DOCUMENTED = "NO_FOLLOW_UP_DOCUMENTED"


class FollowUpPriority(str, Enum):
    """Evidence-grounded urgency/priority level."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class FollowUpItem(BaseModel):
    """Individual follow-up requirement or insight."""

    model_config = ConfigDict(extra="forbid")

    follow_up_type: FollowUpType
    status: FollowUpStatus
    priority: FollowUpPriority = Field(default=FollowUpPriority.MEDIUM)
    description: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    supporting_evidence: List[str] = Field(default_factory=list)
    source: str = Field(min_length=1, description="Origin: DOCTOR_STATED_FOLLOW_UP or AI_FOLLOW_UP_INSIGHT")
    deadline_date: Optional[str] = None
    is_doctor_stated: bool = Field(default=True)
    confidence: float = Field(ge=0.0, le=1.0)


class FollowUpIntelligenceRequest(BaseModel):
    """Input payload for analyzing follow-up needs."""

    model_config = ConfigDict(extra="forbid")

    treatment_responses: List[Dict[str, Any]] = Field(default_factory=list)
    symptom_trends: List[Dict[str, Any]] = Field(default_factory=list)
    doctor_feedback: Optional[str] = None
    patient_summary: Optional[Dict[str, Any]] = None
    extracted_info: Optional[Dict[str, Any]] = None
    current_date: Optional[str] = Field(default=None, description="ISO date string for overdue calculation e.g. '2026-08-15'")


class FollowUpIntelligenceReport(BaseModel):
    """Master response payload for follow-up intelligence."""

    model_config = ConfigDict(extra="forbid")

    follow_up_items: List[FollowUpItem] = Field(default_factory=list)
    pending_information: List[str] = Field(default_factory=list)
    unresolved_issues: List[str] = Field(default_factory=list)
    data_sufficiency: bool = Field(default=True)
    overall_confidence: float = Field(ge=0.0, le=1.0)
    disclaimer: str = Field(
        default=(
            "CARE-CONTINUITY SUPPORT ONLY. DOCTOR INSTRUCTIONS CARRY HIGHER AUTHORITY THAN AI INSIGHTS. "
            "THIS SUBSYSTEM DOES NOT GENERATE MEDICAL ORDERS OR INDEPENDENTLY CHANGE MEDICATIONS."
        )
    )
    processing_time_seconds: float = Field(ge=0.0)
