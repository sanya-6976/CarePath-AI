from src.agents.router import supervisor_router
from src.agents.state import CarePathState, UrgencyLevel


def test_supervisor_router_emergency_short_circuit():
    """Verify that an emergency state immediately routes to Safety Agent."""
    state: CarePathState = {
        "encounter_id": "test_123",
        "patient_id": "pat_123",
        "chief_complaint": "Severe crushing chest pain",
        "symptoms_duration": "10 minutes",
        "symptoms_severity": 10,
        "attachments": [],
        "extracted_demographics": {},
        "structured_symptoms": [],
        "vision_analysis_results": [],
        "doc_ocr_extracted_text": [],
        "patient_timeline": [],
        "rag_evidence_docs": [],
        "clinical_hypotheses": [],
        "confidence_score": 0.0,
        "needs_more_info": False,
        "missing_info_prompt": None,
        "urgency_level": UrgencyLevel.EMERGENCY,
        "is_emergency": True,
        "emergency_reasoning": "Chest pain detected",
        "recommended_specialty": None,
        "specialist_rationale": None,
        "patient_care_plan": [],
        "follow_up_schedule": {},
        "next_agent": "supervisor",
        "execution_history": [],
        "error_state": None,
    }

    next_agent = supervisor_router(state)
    assert next_agent == "safety"
