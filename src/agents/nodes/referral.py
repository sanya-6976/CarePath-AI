from datetime import datetime
from typing import Dict, Any, List
from src.agents.state import CarePathState, UrgencyLevel
from src.core.logging import logger


async def referral_node(state: CarePathState) -> Dict[str, Any]:
    """
    LangGraph Node — Explainable Specialist Referral Navigation Agent.
    Produces structured navigation guidance with mandatory disclaimer:
    'Navigation guidance, not a diagnosis.'
    """
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_referral_node", encounter_id=encounter_id)

    complaint = state.get("chief_complaint", "").lower()
    hypotheses = state.get("clinical_hypotheses", [])
    evidence_docs = state.get("rag_evidence_docs", [])

    if any(kw in complaint for kw in ["chest pain", "shortness of breath", "heart"]):
        specialty = "Cardiology"
        urgency = UrgencyLevel.EMERGENCY if state.get("is_emergency") else UrgencyLevel.URGENT
        reasoning = [
            "Reported symptoms involving cardiac/chest discomfort.",
            "Requires immediate diagnostic evaluation (ECG, Troponin)."
        ]
    elif any(kw in complaint for kw in ["abdominal", "stomach", "rlq"]):
        specialty = "General Surgery"
        urgency = UrgencyLevel.URGENT
        reasoning = [
            "Localized right lower quadrant pain narrative.",
            "Evidence guidelines indicate acute abdominal pain triage."
        ]
    else:
        specialty = "General Internal Medicine"
        urgency = UrgencyLevel.ROUTINE
        reasoning = [
            "General symptom presentation requiring comprehensive physical examination.",
            "Specialist navigation based on primary care clinical evaluation."
        ]

    referral_details = {
        "referral_id": f"ref_{encounter_id}",
        "specialist": specialty,
        "reasoning": reasoning,
        "supporting_evidence": [
            {"title": d.get("source_title", "Clinical Guideline"), "relevance": d.get("relevance_score", 0.9)}
            for d in evidence_docs
        ],
        "confidence": state.get("confidence_score", 0.85),
        "urgency": str(urgency.value if hasattr(urgency, 'value') else urgency),
        "disclaimer": "Navigation guidance, not a diagnosis."
    }

    history = state.get("execution_history", [])
    history.append({
        "step_id": f"step_referral_{len(history)}",
        "agent_name": "ReferralAgent",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "status": "SUCCESS",
        "state_delta_keys": ["recommended_specialty", "specialist_rationale", "referral_details"],
        "error_message": None,
    })

    return {
        "recommended_specialty": specialty,
        "specialist_rationale": " | ".join(reasoning),
        "referral_details": referral_details,
        "execution_history": history,
    }
