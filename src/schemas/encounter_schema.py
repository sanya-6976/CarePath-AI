from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class UrgencyLevelEnum(str, Enum):
    EMERGENCY = "EMERGENCY"
    URGENT = "URGENT"
    ROUTINE = "ROUTINE"
    SELF_CARE = "SELF_CARE"


class EncounterCreateRequest(BaseModel):
    chief_complaint: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Patient's primary complaint described in natural language.",
        examples=["Severe right lower abdominal pain for 12 hours with mild fever."],
    )
    symptoms_duration: Optional[str] = Field(None, examples=["12 hours"])
    symptoms_severity: Optional[int] = Field(None, ge=1, le=10, examples=[8])


class EncounterResponse(BaseModel):
    encounter_id: str
    patient_id: str
    status: str
    chief_complaint: str
    symptoms_duration: Optional[str] = None
    symptoms_severity: Optional[int] = None
    urgency_level: Optional[UrgencyLevelEnum] = None
    is_emergency: bool = False
    confidence_score: Optional[float] = None
    recommended_specialty: Optional[str] = None
    specialist_rationale: Optional[str] = None
    patient_care_plan: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProcessEncounterResponse(BaseModel):
    encounter_id: str
    status: str
    message: str
    stream_url: str
