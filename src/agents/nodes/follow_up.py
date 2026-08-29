from datetime import datetime
from typing import Dict, Any
from src.agents.state import CarePathState, UrgencyLevel
from src.core.logging import logger


async def follow_up_node(state: CarePathState) -> Dict[str, Any]:
    """LangGraph Node — Follow-up Schedule Agent. Final node."""
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_follow_up_node", encounter_id=encounter_id)

    urgency = state.get("urgency_level") or UrgencyLevel.ROUTINE

    if urgency == UrgencyLevel.EMERGENCY:
        schedule = {
            "recommended_check_in_hours": 2,
            "check_in_trigger": "Verify patient has arrived at Emergency Department.",
            "monitoring_instructions": ["Confirm patient is under emergency supervision."],
        }
    elif urgency == UrgencyLevel.URGENT:
        schedule = {
            "recommended_check_in_hours": 12,
            "check_in_trigger": "Verify urgent specialist evaluation was completed.",
            "monitoring_instructions": [
                "Confirm Urgent Care or Surgical evaluation status.",
                "Check for worsening or new symptoms.",
            ],
        }
    else:
        schedule = {
            "recommended_check_in_hours": 48,
            "check_in_trigger": "Assess symptom progression and specialist appointment status.",
            "monitoring_instructions": [
                "Check if symptoms have changed.",
                "Verify specialist appointment was booked.",
                "Log new symptoms to CarePath AI portal.",
            ],
        }

    execution_history = state.get("execution_history", [])
    execution_history.append({
        "step_id": f"step_followup_{len(execution_history)}",
        "agent_name": "FollowUpAgent",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "status": "SUCCESS",
        "state_delta_keys": ["follow_up_schedule"],
        "error_message": None,
    })

    return {
        "follow_up_schedule": schedule,
        "execution_history": execution_history,
    }
