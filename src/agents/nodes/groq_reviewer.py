"""
CarePath AI — Groq Reviewer LangGraph Node
==========================================
Executes an independent review of the CarePath State and patient context using Groq.
Ensures consistency, checks safety rules, identifies uncalculated contradictions,
and verifies missing document requests without modifying the patient's record.
"""

from src.agents.state import CarePathState
from app.services.ai_providers import GroqReviewerProvider
from src.core.logging import logger

groq_provider = GroqReviewerProvider()


async def groq_reviewer_node(state: CarePathState) -> CarePathState:
    """
    Independent Groq Reviewer node in the 14-agent LangGraph workflow.
    """
    logger.info("executing_groq_reviewer_node", encounter_id=state.get("encounter_id"))

    patient_context = state.get("patient_context") or {
        "chief_complaint": state.get("chief_complaint"),
        "symptoms_duration": state.get("symptoms_duration"),
        "symptoms_severity": state.get("symptoms_severity"),
        "structured_symptoms": state.get("structured_symptoms", []),
        "historical_context": state.get("historical_context", []),
        "retrieved_evidence": state.get("retrieved_evidence", [])
    }

    proposed_navigation = {
        "clinical_hypotheses": state.get("clinical_hypotheses", []),
        "recommended_specialty": state.get("recommended_specialty"),
        "urgency_level": str(state.get("urgency_level", "ROUTINE")),
        "is_emergency": state.get("is_emergency", False),
        "care_plan": state.get("patient_care_plan"),
        "missing_information": state.get("missing_information", [])
    }

    review = await groq_provider.review(patient_context, proposed_navigation)

    state["grok_review"] = review

    if review.get("review_status") != "pass":
        logger.info("groq_reviewer_findings", status=review.get("review_status"), summary=review.get("review_summary"))

    return state
