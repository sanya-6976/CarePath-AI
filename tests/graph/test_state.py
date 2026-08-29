import pytest
from src.agents.state import (
    CarePathState,
    UrgencyLevel,
)


def test_carepath_state_integrity():
    """Verify that CarePathState preserves typed fields and state structure."""
    state: CarePathState = {
        "encounter_id": "enc_state_integrity",
        "patient_id": "pat_99",
        "chief_complaint": "Acute RLQ pain",
        "symptoms_duration": "12 hours",
        "symptoms_severity": 8,
        "attachments": [],
        "extracted_demographics": {"age": 28},
        "structured_symptoms": ["RLQ pain"],
        "vision_analysis_results": [],
        "doc_ocr_extracted_text": [],
        "patient_timeline": [],
        "rag_evidence_docs": [
            {
                "evidence_id": "ev_01",
                "source_title": "NICE CG189",
                "relevance_score": 0.95,
            }
        ],
        "clinical_hypotheses": [
            {
                "hypothesis_id": "hyp_01",
                "condition_name": "Appendicitis",
                "likelihood_score": 0.85,
            }
        ],
        "confidence_score": 0.85,
        "needs_more_info": False,
        "missing_info_prompt": None,
        "urgency_level": UrgencyLevel.URGENT,
        "is_emergency": False,
        "emergency_reasoning": None,
        "recommended_specialty": "General Surgery",
        "specialist_rationale": "High RLQ risk",
        "patient_care_plan": ["Fasting required"],
        "follow_up_schedule": {"hours": 12},
        "next_agent": "supervisor",
        "execution_history": [],
        "error_state": None,
    }

    assert state["encounter_id"] == "enc_state_integrity"
    assert len(state["rag_evidence_docs"]) == 1
    assert state["recommended_specialty"] == "General Surgery"
    assert state["confidence_score"] == 0.85
