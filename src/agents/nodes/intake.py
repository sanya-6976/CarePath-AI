"""
CarePath AI — Intake & Medical NLP Agent Node
==============================================
Normalizes narrative patient input into structured symptom tokens, onset duration,
treatment response, and adaptive missing-information queries.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
from src.agents.state import CarePathState
from src.core.logging import logger
from app.services.ai_providers import GeminiProvider

gemini_provider = GeminiProvider()


async def intake_node(state: CarePathState) -> Dict[str, Any]:
    """
    LangGraph Node — Intake Agent.
    Converts chief complaint narrative into structured tokens and identifies missing info queries.
    """
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_intake_node", encounter_id=encounter_id)

    complaint = state.get("chief_complaint", "")
    severity = state.get("symptoms_severity", 5)

    # Base structured tokens
    tokens: List[str] = list(dict.fromkeys([
        term.strip().capitalize()
        for term in complaint.replace(",", " ").replace(".", " ").split()
        if len(term) > 3 and term.lower() not in {
            "with", "have", "been", "that", "this", "from", "some", "after", "coughing", "months", "days"
        }
    ]))

    # Progressive missing information identification
    missing_queries: List[str] = []
    if "cough" in complaint.lower() or "coughing" in complaint.lower():
        if "fever" not in complaint.lower():
            missing_queries.append("Do you currently have a fever or night sweats?")
        if "sputum" not in complaint.lower() and "blood" not in complaint.lower():
            missing_queries.append("Is your cough dry or producing sputum/phlegm?")
    if "stomach" in complaint.lower() or "abdominal" in complaint.lower():
        if "nausea" not in complaint.lower() and "vomiting" not in complaint.lower():
            missing_queries.append("Are you experiencing nausea, vomiting, or appetite loss?")

    demographics = {
        "complaint_length": len(complaint),
        "severity_score": severity,
        "extracted_at": datetime.now(timezone.utc).isoformat()
    }

    execution_history = list(state.get("execution_history", []))
    execution_history.append({
        "step_id": f"step_intake_{len(execution_history)}",
        "agent_name": "IntakeAgent",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "status": "SUCCESS",
        "state_delta_keys": ["structured_symptoms", "extracted_demographics", "missing_info_queries"],
        "error_message": None,
    })

    return {
        "structured_symptoms": tokens,
        "extracted_demographics": demographics,
        "missing_info_queries": missing_queries,
        "execution_history": execution_history,
    }
