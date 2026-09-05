from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict
from pydantic import BaseModel, Field


class UrgencyCategory(str, Enum):
    EMERGENCY = "EMERGENCY"      # Immediate short-circuit to ER
    URGENT = "URGENT"            # Care needed within 24-48 hours
    ROUTINE = "ROUTINE"          # Scheduled specialist appointment
    SELF_CARE = "SELF_CARE"      # Non-urgent home monitoring / symptom tracking


class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class AttachmentType(str, Enum):
    IMAGE = "IMAGE"
    DOCUMENT = "DOCUMENT"


class AgentAlert(BaseModel):
    alert_id: str
    agent_name: str
    severity: AlertSeverity
    code: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AttachmentArtifact(BaseModel):
    attachment_id: str
    file_type: AttachmentType
    file_path: str
    mime_type: str
    processed: bool = False
    processing_error: Optional[str] = None


class VisionResultItem(BaseModel):
    attachment_id: str
    visual_findings: List[str]
    detected_features: List[str]
    confidence: float
    raw_response: Dict[str, Any] = Field(default_factory=dict)


class DocOCRResultItem(BaseModel):
    attachment_id: str
    document_type: str  # e.g., "Lab Report", "Prescription", "Discharge Summary"
    extracted_text: str
    structured_data: Dict[str, Any] = Field(default_factory=dict) # e.g., {"WBC": "14.2", "Hb": "12.0"}
    confidence: float


class TimelineEvent(BaseModel):
    event_id: str
    timestamp_description: str # e.g., "3 days ago", "Onset 2026-08-10"
    event_type: str # "SYMPTOM", "MEDICATION", "PROCEDURE", "LAB_TEST"
    description: str
    source_agent: str


class EvidenceItem(BaseModel):
    evidence_id: str
    source_title: str
    guideline_reference: str
    content_snippet: str
    relevance_score: float
    recommended_specialty: str
    urgency_hint: UrgencyCategory


class ClinicalHypothesis(BaseModel):
    hypothesis_id: str
    condition_name: str
    rationale: str
    likelihood_score: float # 0.0 - 1.0
    key_supporting_factors: List[str]
    key_opposing_factors: List[str] = Field(default_factory=list)


class SpecialistReferral(BaseModel):
    primary_specialty: str
    secondary_specialty: Optional[str] = None
    urgency: UrgencyCategory
    clinical_rationale: str
    suggested_timeframe: str # e.g. "Immediate (ER)", "Within 24 Hours", "Within 1-2 Weeks"
    preparation_instructions: List[str] # e.g., "Bring prior CBC report", "Fasting blood test required"


class CarePlan(BaseModel):
    action_items: List[str]
    questions_for_doctor: List[str]
    red_flag_warning_signs: List[str]
    home_care_guidance: Optional[str] = None


class FollowUpSchedule(BaseModel):
    recommended_check_in_hours: int
    check_in_trigger: str # e.g., "Assess if fever persists above 101F"
    monitoring_instructions: List[str]


class AgentExecutionLog(BaseModel):
    step_id: str
    agent_name: str
    started_at: datetime
    completed_at: datetime
    status: str # "SUCCESS", "FAILED", "SKIPPED", "INTERRUPTED"
    state_delta_keys: List[str]
    error_message: Optional[str] = None


class AgentStatus(BaseModel):
    agent_name: str
    status: str # "Waiting", "Running", "Completed", "Warning", "Failed", "Skipped"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    summary: Optional[str] = None
    reason_for_execution: Optional[str] = None
    user_action_required: Optional[str] = None


class CarePathState(TypedDict):
    """
    Central Shared Graph State for CarePath AI Multi-Agent Architecture.
    
    This immutable TypedDict represents the complete snapshot of the patient's
    navigation journey across all agent transitions.
    """
    # 1. Encounter Identity & Context
    encounter_id: str
    patient_id: str
    started_at: datetime
    
    # 2. Patient Inputs & Raw Data
    chief_complaint: str
    symptoms_duration: Optional[str]
    symptoms_severity: Optional[int] # 1 to 10 scale
    attachments: List[AttachmentArtifact]
    
    # 3. Perception Agent Outputs
    structured_symptoms: List[str]
    demographics: Dict[str, Any]
    vision_results: List[VisionResultItem]
    ocr_results: List[DocOCRResultItem]
    
    # 3.5 Historical Context (Phase 2)
    historical_context: List[Dict[str, Any]]
    previous_analysis: Optional[Dict[str, Any]]
    changed_factors: Optional[List[str]]
    new_information: Optional[List[str]]
    missing_information: Optional[List[str]]
    
    # 4. Patient Chronology & Synthesis
    patient_timeline: List[TimelineEvent]
    
    # 5. RAG & Evidence Retrieval
    retrieved_evidence: List[EvidenceItem]
    
    # 6. Clinical Reasoning & Triage
    clinical_hypotheses: List[ClinicalHypothesis]
    confidence_score: float # Aggregate confidence [0.0 - 1.0]
    urgency_level: UrgencyCategory
    is_emergency: bool
    emergency_reasoning: Optional[str]
    
    # 7. Human-in-the-Loop & Information Gaps
    needs_more_info: bool
    missing_info_queries: List[str]
    human_approved: bool
    human_feedback: Optional[str]
    
    # 8. Navigation & Action Deliverables
    referral: Optional[SpecialistReferral]
    care_plan: Optional[CarePlan]
    follow_up: Optional[FollowUpSchedule]
    
    # 8.5 Shared Patient Context & Grok Critic Review
    patient_context: Optional[Dict[str, Any]]
    grok_review: Optional[Dict[str, Any]]

    # 9. System Diagnostics & Observability
    alerts: List[AgentAlert]
    execution_history: List[AgentExecutionLog]
    agent_status_tracking: Dict[str, AgentStatus]
    next_agent: str
    error_state: Optional[str]
