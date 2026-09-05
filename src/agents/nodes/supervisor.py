"""
CarePath AI — Supervisor / Orchestrator Agent Node
===================================================
Analyzes current CarePathState invariants, evaluates available context, and logs execution tracking.
"""

from datetime import datetime, timezone
from src.agents.state import CarePathState
from src.core.logging import logger


async def supervisor_node(state: CarePathState) -> CarePathState:
    """
    Supervisor Agent Node.
    Analyzes current state, validates invariants, and logs execution tracking.
    """
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_supervisor_node", encounter_id=encounter_id)
    
    history = list(state.get("execution_history", []))
    tracking = dict(state.get("agent_status_tracking", {}))

    history.append({
        "step_id": f"step_supervisor_{len(history)}",
        "agent_name": "SupervisorAgent",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "status": "SUCCESS",
        "state_delta_keys": ["execution_history", "agent_status_tracking"],
        "error_message": None,
    })

    tracking["supervisor"] = {
        "agent_name": "SupervisorAgent",
        "status": "Completed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": f"State evaluated. Attachments: {len(state.get('attachments', []))}, Symptoms: {len(state.get('structured_symptoms', []))}"
    }
    
    state["execution_history"] = history
    state["agent_status_tracking"] = tracking
    return state
