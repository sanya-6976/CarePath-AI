import pytest
from src.agents.nodes.safety import safety_node
from src.agents.nodes.intake import intake_node
from src.agents.state import UrgencyLevel, CarePathState


def _base_state(**overrides) -> CarePathState:
    """Factory for minimal CarePathState fixture."""
    state: CarePathState = {
        "encounter_id": "enc_test",
        "patient_id": "pat_test",
        "chief_complaint": "Mild headache",
        "symptoms_duration": "2 hours",
        "symptoms_severity": 4,
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
    state.update(overrides)
    return state


# ── Safety Agent ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_safety_node_detects_emergency():
    """Safety node must flag chest pain as EMERGENCY."""
    state = _base_state(
        chief_complaint="Severe crushing chest pain radiating to left arm",
        symptoms_severity=10,
    )
    delta = await safety_node(state)
    assert delta["is_emergency"] is True
    assert delta["urgency_level"] == UrgencyLevel.EMERGENCY
    assert delta["emergency_reasoning"] is not None


@pytest.mark.asyncio
async def test_safety_node_passes_routine():
    """Safety node must NOT flag mild headache as emergency."""
    state = _base_state(
        chief_complaint="Mild headache since this morning",
        symptoms_severity=3,
    )
    delta = await safety_node(state)
    assert delta["is_emergency"] is False


@pytest.mark.asyncio
async def test_safety_node_stroke_detection():
    """Safety node must detect stroke keywords."""
    state = _base_state(
        chief_complaint="Sudden weakness and face drooping on left side",
        symptoms_severity=9,
    )
    delta = await safety_node(state)
    assert delta["is_emergency"] is True


# ── Intake Agent ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_intake_node_extracts_symptoms():
    """Intake node must produce a non-empty structured_symptoms list."""
    state = _base_state(
        chief_complaint="Severe right lower quadrant abdominal pain for 12 hours with fever",
        symptoms_duration="12 hours",
        symptoms_severity=8,
    )
    delta = await intake_node(state)
    assert isinstance(delta["structured_symptoms"], list)
    assert len(delta["structured_symptoms"]) > 0


@pytest.mark.asyncio
async def test_intake_node_appends_execution_history():
    """Intake node must append an execution history entry."""
    state = _base_state(chief_complaint="Knee pain for 2 weeks")
    delta = await intake_node(state)
    history = delta["execution_history"]
    assert len(history) == 1
    assert history[0]["agent_name"] == "IntakeAgent"
    assert history[0]["status"] == "SUCCESS"
