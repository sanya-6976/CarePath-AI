import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.agents.state import CarePathState, FollowUpSchedule, UrgencyCategory
from src.config import settings
from src.core.logging import logger


class FollowUpAgent:
    """
    Production Follow-up Agent.
    Calculates post-triage monitoring schedules and check-in trigger conditions
    based on referral urgency levels.
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.api_key = gemini_api_key or settings.GEMINI_API_KEY

    async def calculate_follow_up_schedule(self, state: CarePathState) -> FollowUpSchedule:
        logger.info("follow_up_agent_calculating_schedule", encounter_id=state.get("encounter_id"))
        return self._fallback_follow_up_schedule(state)

    def _fallback_follow_up_schedule(self, state: CarePathState) -> FollowUpSchedule:
        urgency = state.get("urgency_level") or UrgencyCategory.ROUTINE

        check_in_hours = 48
        trigger = "Re-assess symptom progression and check if specialist appointment was confirmed."
        instructions = [
            "Check if abdominal pain or fever has escalated.",
            "Verify whether you have completed your scheduled specialist consultation.",
            "Log any new symptoms into the CarePath AI portal.",
        ]

        if urgency == UrgencyCategory.URGENT:
            check_in_hours = 12
            trigger = "Urgent 12-hour check-in: Verify if patient has been evaluated by an Urgent Care / Surgical provider."
            instructions = [
                "Confirm urgent surgical/specialist evaluation status.",
                "Check for persistent or worsening right lower quadrant pain.",
            ]
        elif urgency == UrgencyCategory.EMERGENCY:
            check_in_hours = 2
            trigger = "Immediate emergency follow-up: Verify arrival at Emergency Department."
            instructions = [
                "Verify patient is currently under emergency medical supervision.",
            ]

        return FollowUpSchedule(
            recommended_check_in_hours=check_in_hours,
            check_in_trigger=trigger,
            monitoring_instructions=instructions,
        )


async def follow_up_node(state: CarePathState) -> Dict[str, Any]:
    """
    LangGraph Node Wrapper for Follow-up Agent.
    Final node in standard navigation pipeline.
    """
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_follow_up_node", encounter_id=encounter_id)

    agent = FollowUpAgent()
    schedule_obj = await agent.calculate_follow_up_schedule(state)

    execution_history = state.get("execution_history", [])
    execution_history.append({
        "step_id": f"step_followup_{len(execution_history)}",
        "agent_name": "FollowUpAgent",
        "started_at": datetime.utcnow(),
        "completed_at": datetime.utcnow(),
        "status": "SUCCESS",
        "state_delta_keys": ["follow_up"],
        "error_message": None,
    })

    return {
        "follow_up": schedule_obj,
        "execution_history": execution_history,
    }
