from datetime import datetime
from typing import Dict, Any, List
from src.agents.state import CarePathState, UrgencyLevel
from src.core.logging import logger


async def care_plan_node(state: CarePathState) -> Dict[str, Any]:
    """
    LangGraph Node — Personalized Patient Care Plan Generator.
    Strictly distinguishes AI-generated guidance from clinician-provided instructions.
    """
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_care_plan_node", encounter_id=encounter_id)

    specialty = state.get("recommended_specialty") or "Specialist"
    urgency = state.get("urgency_level") or UrgencyLevel.ROUTINE
    is_emergency = state.get("is_emergency", False)
    doctor_feedback = state.get("doctor_feedback", {})

    ai_guidance = [
        f"Schedule a consultation with a {specialty} provider.",
        "Gather all past medical records, lab reports, and medication lists.",
        "Track symptom severity changes in your daily log."
    ]

    if is_emergency or urgency == UrgencyLevel.EMERGENCY:
        ai_guidance.insert(0, "CALL EMERGENCY SERVICES (911/112) IMMEDIATELY.")

    clinician_instructions = []
    if doctor_feedback:
        clinician_instructions = [
            f"Clinician Note: {doctor_feedback.get('notes', 'Reviewed by physician.')}",
            f"Confirmed Next Step: {doctor_feedback.get('confirmed_next_step', 'Follow up as advised.')}"
        ]

    care_plan_details = {
        "care_plan_id": f"plan_{encounter_id}",
        "encounter_id": encounter_id,
        "ai_organization_guidance": ai_guidance,
        "clinician_provided_instructions": clinician_instructions,
        "questions_to_ask_doctor": [
            f"What specific tests do you recommend for my case?",
            "What warning signs should prompt emergency care?"
        ],
        "monitoring_points": [
            "Track daily body temperature and pain score.",
            "Log any new or worsening symptoms."
        ],
        "generated_at": datetime.utcnow().isoformat()
    }

    history = state.get("execution_history", [])
    history.append({
        "step_id": f"step_care_plan_{len(history)}",
        "agent_name": "CarePlanAgent",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "status": "SUCCESS",
        "state_delta_keys": ["patient_care_plan", "care_plan_details"],
        "error_message": None,
    })

    return {
        "patient_care_plan": ai_guidance + clinician_instructions,
        "care_plan_details": care_plan_details,
        "execution_history": history,
    }
