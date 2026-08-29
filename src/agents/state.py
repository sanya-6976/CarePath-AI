from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict


class UrgencyLevel(str, Enum):
    EMERGENCY = "EMERGENCY"  # Immediate short-circuit to ER
    URGENT = "URGENT"        # Care within 24-48 hours
    ROUTINE = "ROUTINE"      # Scheduled specialist appointment
    SELF_CARE = "SELF_CARE"  # Non-urgent guidance / home monitoring


class AttachmentType(str, Enum):
    IMAGE = "IMAGE"
    DOCUMENT = "DOCUMENT"


class AttachmentMeta(TypedDict):
    attachment_id: str
    file_type: AttachmentType
    file_url: str
    processed: bool


class AgentExecutionStep(TypedDict):
    agent_name: str
    timestamp: str
    status: str
    output_summary: str


class CarePathState(TypedDict):
    """
    Central State Schema passed through the LangGraph multi-agent engine.
    Supports Sprint 1 & Sprint 2 multi-agent workflows.
    """
    # Encounter & Workflow Metadata
    encounter_id: str
    patient_id: str
    request_type: Optional[str]  # "encounter", "document", "medication", "evidence", "doctor_bridge", "referral", "care_plan"

    # Initial Patient Complaints & Inputs
    chief_complaint: str
    symptoms_duration: Optional[str]
    symptoms_severity: Optional[int]  # 1-10
    attachments: List[AttachmentMeta]

    # Memory & Historical Context
    memory_context: List[Dict[str, Any]]

    # Perception & OCR Agent Outputs
    extracted_demographics: Dict[str, Any]
    structured_symptoms: List[str]
    vision_analysis_results: List[Dict[str, Any]]
    doc_ocr_extracted_text: List[Dict[str, Any]]
    extracted_medications: List[Dict[str, Any]]
    patient_timeline: List[Dict[str, Any]]

    # Evidence & Clinical Reasoning Outputs
    rag_evidence_docs: List[Dict[str, Any]]
    clinical_hypotheses: List[Dict[str, Any]]
    confidence_score: float  # 0.0 to 1.0
    needs_more_info: bool
    missing_info_prompt: Optional[str]

    # Doctor Bridge & Human-In-The-Loop (HITL) State
    doctor_brief: Optional[Dict[str, Any]]
    doctor_questions: List[str]
    doctor_feedback: Optional[Dict[str, Any]]
    is_paused: bool
    awaiting_doctor_review: bool

    # Triage & Safety Flags
    urgency_level: UrgencyLevel
    is_emergency: bool
    emergency_reasoning: Optional[str]

    # Referral & Action Plan Outputs
    recommended_specialty: Optional[str]
    specialist_rationale: Optional[str]
    referral_details: Optional[Dict[str, Any]]
    patient_care_plan: List[str]
    care_plan_details: Optional[Dict[str, Any]]
    follow_up_schedule: Dict[str, Any]

    # LangGraph Orchestration & Router State
    next_agent: str
    execution_history: List[AgentExecutionStep]
    error_state: Optional[str]
