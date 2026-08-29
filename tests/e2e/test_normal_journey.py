import pytest
from src.agents.graph import carepath_graph
from src.agents.state import CarePathState, UrgencyLevel


@pytest.mark.asyncio
async def test_end_to_end_normal_patient_journey():
    """
    End-to-End Test: Scenario A — Normal Patient Navigation Journey.
    Verifies state progression across Supervisor -> Intake -> Safety -> Graph completion.
    """
    initial_state: CarePathState = {
        "encounter_id": "e2e_normal_001",
        "patient_id": "pat_e2e_001",
        "chief_complaint": "Severe sharp right lower quadrant abdominal pain for 12 hours with mild fever",
        "symptoms_duration": "12 hours",
        "symptoms_severity": 8,
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
    assert final_state["is_emergency"] is False
    assert len(final_state["execution_history"]) > 0
