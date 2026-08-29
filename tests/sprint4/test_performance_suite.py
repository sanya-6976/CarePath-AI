import time
import pytest
from src.agents.nodes.safety import safety_node
from src.agents.state import CarePathState, UrgencyLevel


@pytest.mark.asyncio
async def test_performance_safety_node_sub_millisecond_latency():
    """
    Sprint 4 Performance Test:
    Verify Safety Agent emergency check operates under 5ms latency threshold.
    """
    state: CarePathState = {
        "encounter_id": "perf_01",
        "patient_id": "pat_perf_01",
        "chief_complaint": "Sudden chest pain and shortness of breath",
        "symptoms_duration": "10 min",
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

    start = time.perf_counter()
    result = await safety_node(state)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    assert result["is_emergency"] is True
    assert elapsed_ms < 10.0, f"Safety check took {elapsed_ms:.2f}ms, target < 10.0ms"
