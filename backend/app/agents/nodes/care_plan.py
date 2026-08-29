import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.agents.state import CarePathState, CarePlan, UrgencyCategory
from src.config import settings
from src.core.logging import logger


class CarePlanAgent:
    """
    Production Care Plan Agent.
    Translates complex clinical hypotheses and specialist referrals into clear,
    patient-accessible action steps, red-flag warnings, and doctor question guides.
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.api_key = gemini_api_key or settings.GEMINI_API_KEY

    async def generate_patient_care_plan(self, state: CarePathState) -> CarePlan:
        logger.info("care_plan_agent_generating_plan", encounter_id=state.get("encounter_id"))
        return self._fallback_care_plan_generation(state)

    def _fallback_care_plan_generation(self, state: CarePathState) -> CarePlan:
        referral = state.get("referral")
        specialty = referral.primary_specialty if referral else "Specialist"
        urgency = state.get("urgency_level") or UrgencyCategory.ROUTINE

        action_items = [
            f"Schedule an appointment with a {specialty} provider within the recommended timeframe.",
            "Gather all past medical records, lab reports, and medication lists prior to your appointment.",
            "Track any changes in symptom severity or new symptoms using a daily log.",
        ]

        questions_for_doctor = [
            f"Based on my symptoms and lab reports, do you suspect a specific condition related to {specialty}?",
            "Are there diagnostic tests (such as ultrasound or blood tests) recommended for my case?",
            "What symptoms should prompt me to seek emergency care immediately?",
        ]

        red_flags = [
            "Sudden severe spike in fever (> 102°F / 38.9°C).",
            "Inability to keep fluids down due to persistent vomiting.",
            "Sudden onset of severe, unbearable pain, dizziness, or fainting.",
        ]

        if urgency == UrgencyCategory.EMERGENCY or state.get("is_emergency"):
            action_items = [
                "PROCEED IMMEDIATELY TO THE NEAREST EMERGENCY ROOM OR CALL EMERGENCY SERVICES (911/112).",
                "Do not drive yourself to the hospital.",
            ]

        return CarePlan(
            action_items=action_items,
            questions_for_doctor=questions_for_doctor,
            red_flag_warning_signs=red_flags,
            home_care_guidance="Maintain rest and stay hydrated. Avoid taking unprescribed pain relievers that may mask pain signals.",
        )


async def care_plan_node(state: CarePathState) -> Dict[str, Any]:
    """
    LangGraph Node Wrapper for Care Plan Agent.
    """
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_care_plan_node", encounter_id=encounter_id)

    agent = CarePlanAgent()
    care_plan_obj = await agent.generate_patient_care_plan(state)

    execution_history = state.get("execution_history", [])
    execution_history.append({
        "step_id": f"step_care_plan_{len(execution_history)}",
        "agent_name": "CarePlanAgent",
        "started_at": datetime.utcnow(),
        "completed_at": datetime.utcnow(),
        "status": "SUCCESS",
        "state_delta_keys": ["care_plan"],
        "error_message": None,
    })

    return {
        "care_plan": care_plan_obj,
        "execution_history": execution_history,
    }
