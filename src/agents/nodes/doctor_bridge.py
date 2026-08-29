from datetime import datetime
from typing import Dict, Any, List
from src.agents.state import CarePathState
from src.core.logging import logger


async def doctor_bridge_node(state: CarePathState) -> Dict[str, Any]:
    """
    LangGraph Node — CarePath Doctor Bridge Agent.
    Generates a doctor-ready brief and case-specific questions.
    Triggers Human-In-The-Loop (HITL) pause if clinician review is needed.
    """
    encounter_id = state.get("encounter_id", "unknown")
    patient_id = state.get("patient_id", "pat_unknown")
    logger.info("executing_doctor_bridge_node", encounter_id=encounter_id)

    complaint = state.get("chief_complaint", "")
    symptoms = state.get("structured_symptoms", [])
    history_ctx = state.get("memory_context", [])
    ocr_reports = state.get("doc_ocr_extracted_text", [])
    meds = state.get("extracted_medications", [])
    timeline_events = state.get("patient_timeline", [])

    brief = {
        "brief_id": f"brief_{encounter_id}",
        "patient_id": patient_id,
        "encounter_id": encounter_id,
        "chief_complaint": complaint,
        "symptoms": symptoms,
        "medical_history_summary": f"Historical entries: {len(history_ctx)} records.",
        "reports_summary": f"Uploaded documents: {len(ocr_reports)} processed.",
        "medications": meds,
        "timeline_highlights": [e.get("description") for e in timeline_events[:3]],
        "current_concerns": ["Symptom progression", "Specialist evaluation needed"],
        "generated_at": datetime.utcnow().isoformat(),
    }

    questions = [
        f"How long have you experienced the current {symptoms[0] if symptoms else 'symptoms'}?",
        "Have you noticed any change in symptom severity after taking your current medications?",
        "Are there any specific diagnostic tests or lab reports you would like reviewed?",
        "What specific warning symptoms should prompt emergency care?"
    ]

    # Triggers Human-In-The-Loop pause state for doctor review
    awaiting_review = True
    is_paused = True

    history = state.get("execution_history", [])
    history.append({
        "step_id": f"step_doctor_bridge_{len(history)}",
        "agent_name": "DoctorBridgeAgent",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "status": "PAUSED_FOR_DOCTOR_REVIEW",
        "state_delta_keys": ["doctor_brief", "doctor_questions", "is_paused", "awaiting_doctor_review"],
        "error_message": None,
    })

    return {
        "doctor_brief": brief,
        "doctor_questions": questions,
        "is_paused": is_paused,
        "awaiting_doctor_review": awaiting_review,
        "execution_history": history,
    }
