import pytest
from src.agents.graph import carepath_graph
from src.agents.state import CarePathState, UrgencyLevel


@pytest.mark.asyncio
async def test_e2e_safety_emergency_override():
    """
    Sprint 4 Safety E2E Test:
    Verifies that emergency complaints (e.g. crushing chest pain) immediately trigger Safety Agent
    short-circuiting and stopping referral/care-plan workflows without unsafe execution.
    """
    emergency_state: CarePathState = {
        "encounter_id": "enc_s4_safety_01",
        "patient_id": "pat_s4_emerg",
        "request_type": "encounter",
        "chief_complaint": "Sudden crushing chest pain radiating to left arm with shortness of breath",
        "symptoms_duration": "5 minutes",
        "symptoms_severity": 10,
        "attachments": [],
        "memory_context": [],
        "extracted_demographics": {},
        "structured_symptoms": [],
        "vision_analysis_results": [],
        "doc_ocr_extracted_text": [],
        "extracted_medications": [],
        "patient_timeline": [],
        "rag_evidence_docs": [],
        "clinical_hypotheses": [],
        "confidence_score": 0.0,
        "needs_more_info": False,
        "missing_info_prompt": None,
        "doctor_brief": None,
        "doctor_questions": [],
        "doctor_feedback": None,
        "is_paused": False,
        "awaiting_doctor_review": False,
        "urgency_level": UrgencyLevel.ROUTINE,
        "is_emergency": False,
        "emergency_reasoning": None,
        "recommended_specialty": None,
        "specialist_rationale": None,
        "referral_details": None,
        "patient_care_plan": [],
        "care_plan_details": None,
        "follow_up_schedule": {},
        "next_agent": "supervisor",
        "execution_history": [],
        "error_state": None,
    }

    final_state = await carepath_graph.ainvoke(emergency_state)

    # Assertions: Emergency state MUST be flagged immediately
    assert final_state["is_emergency"] is True
    assert final_state["urgency_level"] == UrgencyLevel.EMERGENCY
    assert final_state["emergency_reasoning"] is not None
    assert "red-flag" in final_state["emergency_reasoning"].lower()
    assert len(final_state["patient_care_plan"]) > 0
    assert "911" in final_state["patient_care_plan"][0]

    # Verify execution history contains SafetyAgent execution
    history_agents = [step["agent_name"] for step in final_state["execution_history"]]
    assert "SafetyAgent" in history_agents
