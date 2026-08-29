from datetime import datetime
from typing import Dict, Any, List
from src.agents.state import CarePathState
from src.core.logging import logger


async def vision_node(state: CarePathState) -> Dict[str, Any]:
    logger.info("executing_vision_node", encounter_id=state.get("encounter_id"))
    attachments = state.get("attachments", [])
    vision_results = list(state.get("vision_analysis_results", []))

    updated_attachments = []
    for att in attachments:
        if att.get("file_type") == "IMAGE" and not att.get("processed"):
            vision_results.append({
                "attachment_id": att.get("attachment_id"),
                "findings": ["Erythematous lesion"],
                "confidence": 0.88
            })
            att["processed"] = True
        updated_attachments.append(att)

    execution_history = state.get("execution_history", [])
    execution_history.append({
        "step_id": f"step_vision_{len(execution_history)}",
        "agent_name": "VisionAgent",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "status": "SUCCESS",
        "state_delta_keys": ["vision_analysis_results", "attachments"],
        "error_message": None,
    })

    return {
        "vision_analysis_results": vision_results,
        "attachments": updated_attachments,
        "execution_history": execution_history,
    }
