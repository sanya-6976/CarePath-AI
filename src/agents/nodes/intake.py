from datetime import datetime
from typing import Dict, Any, List
from src.agents.state import CarePathState
from src.core.logging import logger


async def intake_node(state: CarePathState) -> Dict[str, Any]:
    """
    LangGraph Node — Intake & Medical NLP Agent.
    Normalises the chief complaint narrative into structured symptom tokens.
    Returns a state delta (only modified keys).
    """
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_intake_node", encounter_id=encounter_id)

    complaint = state.get("chief_complaint", "")

    # Heuristic tokeniser — AI teammate will wire Gemini NLP here in Sprint 3
    tokens: List[str] = list(dict.fromkeys([
        term.strip().capitalize()
        for term in complaint.replace(",", " ").replace(".", " ").split()
        if len(term) > 3 and term.lower() not in {
            "with", "have", "been", "that", "this", "from", "some", "after",
        }
    ]))

    demographics = {
        "complaint_length":   len(complaint),
        "severity_score":     state.get("symptoms_severity", 5),
    }

    execution_history = state.get("execution_history", [])
    execution_history.append({
        "step_id":          f"step_intake_{len(execution_history)}",
        "agent_name":       "IntakeAgent",
        "started_at":       datetime.now().isoformat(),
        "completed_at":     datetime.now().isoformat(),
        "status":           "SUCCESS",
        "state_delta_keys": ["structured_symptoms", "extracted_demographics"],
        "error_message":    None,
    })

    return {
        "structured_symptoms":    tokens,
        "extracted_demographics": demographics,
        "execution_history":      execution_history,
    }
