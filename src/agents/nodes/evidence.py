from datetime import datetime
from typing import Dict, Any, List
from src.agents.state import CarePathState, UrgencyLevel
from src.core.logging import logger


async def evidence_node(state: CarePathState) -> Dict[str, Any]:
    """LangGraph Node — Evidence & RAG Agent."""
    encounter_id = state.get("encounter_id", "unknown")
    logger.info("executing_evidence_node", encounter_id=encounter_id)

    complaint = state.get("chief_complaint", "").lower()
    evidence: List[Dict[str, Any]] = []

    if any(kw in complaint for kw in ["abdominal", "stomach", "right lower", "rlq"]):
        evidence = [
            {
                "evidence_id": "guideline_nice_appendicitis_001",
                "source_title": "NICE CG189: Acute Appendicitis",
                "guideline_reference": "NICE CG189 §1.2",
                "content_snippet": (
                    "RLQ tenderness with fever and leukocytosis requires urgent General Surgery."
                ),
                "relevance_score": 0.95,
                "recommended_specialty": "General Surgery",
                "urgency_hint": UrgencyLevel.URGENT,
            },
            {
                "evidence_id": "guideline_acg_gastro_004",
                "source_title": "ACG Guidelines: Acute Abdominal Pain",
                "guideline_reference": "ACG 2024",
                "content_snippet": "Persistent RIF pain with rebound tenderness indicates surgical pathology.",
                "relevance_score": 0.88,
                "recommended_specialty": "Gastroenterology",
                "urgency_hint": UrgencyLevel.URGENT,
            },
        ]
    else:
        evidence = [
            {
                "evidence_id": "guideline_who_primary_010",
                "source_title": "WHO Triage Protocols",
                "guideline_reference": "WHO §4",
                "content_snippet": "Structured clinical history and specialist referral recommended.",
                "relevance_score": 0.75,
                "recommended_specialty": "General Internal Medicine",
                "urgency_hint": UrgencyLevel.ROUTINE,
            }
        ]

    execution_history = state.get("execution_history", [])
    execution_history.append({
        "step_id": f"step_evidence_{len(execution_history)}",
        "agent_name": "EvidenceAgent",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "status": "SUCCESS",
        "state_delta_keys": ["rag_evidence_docs"],
        "error_message": None,
    })

    return {
        "rag_evidence_docs": evidence,
        "execution_history": execution_history,
    }
