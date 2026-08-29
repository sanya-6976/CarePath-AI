"""Strict Pydantic Schemas for Doctor Feedback Interpretation."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.patient_summary import PatientSummaryReport


class DoctorStatementType(str, Enum):
    """Origin and evidence classification for clinician statements."""

    DOCTOR_STATED = "DOCTOR_STATED"
    PATIENT_REPORTED = "PATIENT_REPORTED"
    EXTRACTED_FROM_RECORD = "EXTRACTED_FROM_RECORD"
    AI_INTERPRETATION = "AI_INTERPRETATION"
    UNCERTAIN = "UNCERTAIN"
    CONFLICTING = "CONFLICTING"


class MemoryCategory(str, Enum):
    """Classification for candidate items ready for CarePath Memory persistence."""

    LONG_TERM_CLINICAL_FACT = "LONG_TERM_CLINICAL_FACT"
    CURRENT_CLINICAL_STATUS = "CURRENT_CLINICAL_STATUS"
    MEDICATION_INFORMATION = "MEDICATION_INFORMATION"
    ALLERGY_INFORMATION = "ALLERGY_INFORMATION"
    TREATMENT_EVENT = "TREATMENT_EVENT"
    DIAGNOSTIC_EVENT = "DIAGNOSTIC_EVENT"
    FOLLOW_UP_INSTRUCTION = "FOLLOW_UP_INSTRUCTION"
    DOCTOR_PREFERENCE_NOTE = "DOCTOR_PREFERENCE_NOTE"
    TEMPORARY_CONTEXT = "TEMPORARY_CONTEXT"
    NOT_MEMORY_WORTHY = "NOT_MEMORY_WORTHY"


class InterpretedFeedbackItem(BaseModel):
    """A discrete clinical finding or observation extracted from doctor feedback."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    category: str = Field(description="CLINICAL_OBSERVATION, DIAGNOSIS, SYMPTOM, TREATMENT_STATUS, UNRESOLVED_CONCERN")
    statement_type: DoctorStatementType = Field(default=DoctorStatementType.DOCTOR_STATED)
    confidence: float = Field(ge=0.0, le=1.0)
    source_snippet: Optional[str] = None


class DoctorMedicationInstruction(BaseModel):
    """Doctor-stated medication instruction or change."""

    model_config = ConfigDict(extra="forbid")

    drug_name: str = Field(min_length=1)
    action: str = Field(default="VERIFIED", description="INITIATE, CONTINUE, MODIFY_DOSAGE, DISCONTINUE, VERIFIED")
    doctor_stated_instruction: str = Field(min_length=1, description="Verbatim instruction stated by doctor")
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    statement_type: DoctorStatementType = Field(default=DoctorStatementType.DOCTOR_STATED)
    confidence: float = Field(ge=0.0, le=1.0)


class DoctorFollowUpInstruction(BaseModel):
    """Explicit follow-up instruction provided by the clinician."""

    model_config = ConfigDict(extra="forbid")

    instruction_text: str = Field(min_length=1)
    timeframe: Optional[str] = Field(default=None, description="e.g. '2 weeks', '1 month'")
    trigger_conditions: Optional[str] = Field(default=None, description="e.g. 'if symptoms worsen'")
    is_explicit_doctor_instruction: bool = Field(default=True)
    confidence: float = Field(ge=0.0, le=1.0)


class DoctorReferralItem(BaseModel):
    """Specialist referral explicitly recommended by the clinician."""

    model_config = ConfigDict(extra="forbid")

    specialty: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    urgency: Optional[str] = Field(default="ROUTINE", description="ROUTINE, URGENT, EMERGENCY")
    supporting_doctor_statement: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)


class DoctorFeedbackConflict(BaseModel):
    """Contradiction between doctor feedback and pre-existing patient records."""

    model_config = ConfigDict(extra="forbid")

    conflicting_topic: str = Field(min_length=1)
    record_statement: str = Field(min_length=1)
    doctor_statement: str = Field(min_length=1)
    conflict_description: str = Field(min_length=1)
    uncertainty_status: str = Field(default="REQUIRES_CLINICAL_RECONCILIATION")


class MemoryCandidateItem(BaseModel):
    """CarePath Memory candidate item structured for future continuity-of-care storage."""

    model_config = ConfigDict(extra="forbid")

    content: str = Field(min_length=1)
    category: MemoryCategory
    statement_type: DoctorStatementType
    importance_score: float = Field(ge=0.0, le=1.0)
    reason: str = Field(min_length=1)


class DoctorFeedbackRequest(BaseModel):
    """Input payload to request doctor feedback interpretation."""

    model_config = ConfigDict(extra="forbid")

    doctor_notes: Optional[str] = None
    question_answers: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Answers to case-specific questions e.g. [{'question': '...', 'answer': '...'}]",
    )
    existing_summary: Optional[PatientSummaryReport] = None
    doctor_id: Optional[str] = None
    consultation_date: Optional[str] = None


class DoctorFeedbackInterpretationReport(BaseModel):
    """Master response payload containing interpreted doctor feedback and memory candidates."""

    model_config = ConfigDict(extra="forbid")

    interpreted_items: List[InterpretedFeedbackItem] = Field(default_factory=list)
    clinical_observations: List[str] = Field(default_factory=list)
    confirmed_diagnoses: List[str] = Field(default_factory=list)
    medications: List[DoctorMedicationInstruction] = Field(default_factory=list)
    follow_up_instructions: List[DoctorFollowUpInstruction] = Field(default_factory=list)
    referrals: List[DoctorReferralItem] = Field(default_factory=list)
    conflicts: List[DoctorFeedbackConflict] = Field(default_factory=list)
    memory_candidates: List[MemoryCandidateItem] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)
    source_references: List[str] = Field(default_factory=list)
    overall_confidence: float = Field(ge=0.0, le=1.0)
    disclaimer: str = Field(
        default=(
            "FOR CLINICAL CONTINUITY SUPPORT AND MEMORY STRUCTURE ONLY. "
            "DOCTOR STATEMENTS ARE INTERPRETED AS STATED BY THE CLINICIAN. "
            "THIS SUBSYSTEM DOES NOT GENERATE AI PRESCRIPTIONS OR MEDICAL ORDERS."
        )
    )
    processing_time_seconds: float = Field(ge=0.0)
