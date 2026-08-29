import pytest
from src.agents.router import supervisor_router
from src.agents.state import CarePathState, UrgencyLevel


def test_supervisor_router_emergency_short_circuit():
    """Verify that is_emergency=True causes immediate routing to safety agent."""
    state: CarePathState = {
        "encounter_id": "test_routing_01",
        "patient_id": "pat_01",
        "chief_complaint": "Severe crushing chest pain",
        "symptoms_duration": "10 min",
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
        "emergency_reasoning": "Chest pain",
        "recommended_specialty": None,
        "specialist_rationale": None,
        "patient_care_plan": [],
        "follow_up_schedule": {},
        "next_agent": "supervisor",
        "execution_history": [],
        "error_state": None,
    }

    assert supervisor_router(state) == "safety"


def test_supervisor_router_perception_image_branching():
    """Verify routing to vision agent when unprocessed image attachments exist."""
    state: CarePathState = {
        "encounter_id": "test_routing_02",
        "patient_id": "pat_02",
        "chief_complaint": "Skin rash on leg",
        "symptoms_duration": "3 days",
        "symptoms_severity": 4,
        "attachments": [{"attachment_id": "img_01", "file_type": "IMAGE", "file_url": "/tmp/rash.jpg", "processed": False}],
        "extracted_demographics": {},
        "structured_symptoms": ["skin rash"],
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

    assert supervisor_router(state) == "vision"
