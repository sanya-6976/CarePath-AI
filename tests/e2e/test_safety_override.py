import pytest
from src.agents.graph import carepath_graph
from src.agents.state import CarePathState, UrgencyLevel


@pytest.mark.asyncio
async def test_end_to_end_safety_override_journey():
    """
    End-to-End Test: Scenario B — Emergency Safety Override.
    Verifies that emergency red-flag symptoms short-circuit normal execution.
    """
    initial_state: CarePathState = {
        "encounter_id": "e2e_safety_002",
        "patient_id": "pat_e2e_002",
        "chief_complaint": "Severe crushing chest pain radiating to left arm with shortness of breath",
        "symptoms_duration": "15 minutes",
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
        "urgency_level": UrgencyLevel.ROUTINE,
        "is_emergency": False,
        "emergency_reasoning": None,
        "recommended_specialty": None,
        "specialist_rationale": None,
        "patient_care_plan": [],
        "follow_up_schedule": {},
        "next_agent": "supervisor",
        "execution_history": [],
        "error_state": None,
    }

    final_state = await carepath_graph.ainvoke(initial_state)

    # Verifications
    assert final_state["is_emergency"] is True
    assert final_state["urgency_level"] == UrgencyLevel.EMERGENCY
    assert final_state["emergency_reasoning"] is not None
    assert len(final_state["patient_care_plan"]) > 0
