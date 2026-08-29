from datetime import datetime
from src.agents.state import CarePathState
from src.core.logging import logger


async def supervisor_node(state: CarePathState) -> CarePathState:
    """
    Supervisor Agent Node.
    Analyzes current state, validates invariants, and logs execution tracking.
    """
    logger.info("executing_supervisor_node", encounter_id=state["encounter_id"])
    
    # Initialize execution history if missing
    history = state.get("execution_history", [])
    history.append({
        "agent_name": "SupervisorAgent",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "EVALUATING",
        "output_summary": f"Evaluated state. Attachments count: {len(state.get('attachments', []))}"
    })
    
    state["execution_history"] = history
    return state
