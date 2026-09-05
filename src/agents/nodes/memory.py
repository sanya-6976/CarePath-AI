"""
CarePath AI — Memory Agent Node
===============================
Retrieves relevant persistent patient history across encounters, structuring historical context
without dumping full unstructured database blobs.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
from src.agents.state import CarePathState
from src.core.logging import logger


async def memory_node(state: CarePathState) -> Dict[str, Any]:
    """
    LangGraph Node — Memory Agent.
    Aggregates historical encounter context for the current patient.
    """
    encounter_id = state.get("encounter_id", "unknown")
    patient_id = state.get("patient_id", "unknown")
    logger.info("executing_memory_node", encounter_id=encounter_id, patient_id=patient_id)

    historical_context = list(state.get("historical_context", []))

    memory_summary = {
        "total_past_encounters": len(historical_context),
        "previous_analysis": state.get("previous_analysis"),
        "key_historical_updates": [h.get("content") for h in historical_context[-5:]] if historical_context else []
    }

    execution_history = list(state.get("execution_history", []))
    execution_history.append({
        "step_id": f"step_memory_{len(execution_history)}",
        "agent_name": "MemoryAgent",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "status": "SUCCESS",
        "state_delta_keys": ["memory_context", "historical_context"],
        "error_message": None,
    })

    return {
        "memory_context": memory_summary,
        "execution_history": execution_history,
    }
