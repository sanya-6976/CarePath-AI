from datetime import datetime
from typing import Dict, Any, List
from src.agents.state import CarePathState
from src.repositories.sprint2_repo import memory_repository
from src.core.logging import logger


async def memory_node(state: CarePathState) -> Dict[str, Any]:
    """
    LangGraph Node — CarePath Memory Agent.
    Retrieves relevant historical patient context before Supervisor reasoning.
    Does NOT blindly load full history.
    """
    encounter_id = state.get("encounter_id", "unknown")
    patient_id = state.get("patient_id", "pat_unknown")
    logger.info("executing_memory_node", encounter_id=encounter_id, patient_id=patient_id)

    complaint = state.get("chief_complaint", "")
    keywords = [w.strip().lower() for w in complaint.split() if len(w) > 4]

    relevant_records = await memory_repository.retrieve_context(patient_id, keywords)

    history = state.get("execution_history", [])
    history.append({
        "step_id": f"step_memory_{len(history)}",
        "agent_name": "MemoryAgent",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "status": "SUCCESS",
        "state_delta_keys": ["memory_context"],
        "error_message": None,
    })

    return {
        "memory_context": relevant_records,
        "execution_history": history,
    }
