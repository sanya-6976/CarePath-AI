from src.agents.state import CarePathState, UrgencyLevel
from src.core.logging import logger

_EMERGENCY_KEYWORDS = [
    "crushing chest pain", "chest pain", "shortness of breath",
    "sudden weakness", "face drooping", "slurred speech",
    "anaphylaxis", "throat closing", "unconscious", "unresponsive",
    "coughing blood", "vomiting blood", "suicidal", "stroke",
    "heart attack", "cardiac arrest",
]


def _has_emergency_keywords(complaint: str) -> bool:
    text = complaint.lower()
    return any(kw in text for kw in _EMERGENCY_KEYWORDS)


def supervisor_router(state: CarePathState) -> str:
    """
    Dynamic Supervisor Router.
    Evaluates CarePathState invariants and request_type to determine next node.
    Supports HITL pause/resume and specific workflow intents.
    """
    logger.info(
        "supervisor_evaluating_state",
        encounter_id=state.get("encounter_id"),
        is_emergency=state.get("is_emergency"),
        request_type=state.get("request_type"),
        is_paused=state.get("is_paused"),
    )

    # ── 1. Safety Gate — HIGHEST PRIORITY OVERRIDE ──────────────────────────
    if state.get("is_emergency"):
        if state.get("patient_care_plan"):
            return "__end__"
        return "safety"

    complaint = state.get("chief_complaint", "")
    severity = state.get("symptoms_severity") or 0
    if _has_emergency_keywords(complaint) or severity >= 9:
        if not state.get("emergency_reasoning"):
            return "safety"

    # ── 2. Human-In-The-Loop (HITL) Pause ────────────────────────────────────
    if state.get("is_paused") or state.get("awaiting_doctor_review"):
        logger.info("workflow_paused_for_human_review", encounter_id=state.get("encounter_id"))
        return "__end__"

    req_type = state.get("request_type")

    # ── 3. Intent-Specific Direct Routing ────────────────────────────────────
    if req_type == "document":
        attachments = state.get("attachments", [])
        if any(not a.get("processed") for a in attachments):
            return "docs"
        return "__end__"

    if req_type == "medication":
        if not state.get("doc_ocr_extracted_text") and state.get("attachments"):
            return "docs"
        if not state.get("extracted_medications"):
            return "medication"
        return "__end__"

    if req_type == "evidence":
        if not state.get("rag_evidence_docs"):
            return "evidence"
        return "__end__"

    if req_type == "doctor_bridge":
        if not state.get("doctor_brief"):
            return "doctor_bridge"
        return "__end__"

    if req_type == "referral":
        if not state.get("recommended_specialty"):
            return "referral"
        return "__end__"

    if req_type == "care_plan":
        if not state.get("patient_care_plan"):
            return "care_plan"
        return "__end__"

    # ── 4. Perception Phase (Image & Document Attachments) ────────────────────
    attachments = state.get("attachments", [])
    if any(a.get("file_type") == "IMAGE" and not a.get("processed") for a in attachments):
        return "vision"
    if any(a.get("file_type") == "DOCUMENT" and not a.get("processed") for a in attachments):
        return "docs"

    # ── 5. Intake Normalization ──────────────────────────────────────────────
    if not state.get("structured_symptoms"):
        return "intake"

    # ── 6. Memory & Reasoning Pipeline ──────────────────────────────────────
    if state.get("memory_context") is None:
        return "memory"

    if not state.get("patient_timeline"):
        return "timeline"
    if not state.get("rag_evidence_docs"):
        return "evidence"
    if not state.get("clinical_hypotheses"):
        return "clinical_reasoning"

    if state.get("confidence_score", 1.0) < 0.60 and state.get("needs_more_info"):
        return "__end__"

    if not state.get("recommended_specialty"):
        return "referral"

    if not state.get("patient_care_plan"):
        return "care_plan"

    if not state.get("follow_up_schedule"):
        return "follow_up"

    return "__end__"
