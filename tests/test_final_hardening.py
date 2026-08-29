"""Low-dependency regression checks for final hardening wiring.

HTTP integration tests require the configured FastAPI runtime and database.
These checks deliberately verify the non-negotiable safety wiring without
claiming to exercise external services.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_clinical_graph_failure_does_not_persist_a_fallback_analysis():
    source = (ROOT / "backend/app/api/v1/endpoints/medical.py").read_text(encoding="utf-8")
    assert "await carepath_graph.ainvoke(initial_state)" in source
    assert "AI analysis is temporarily unavailable" in source
    assert "final_state = initial_state" not in source


def test_companion_new_clinical_needs_route_to_existing_medical_workflow():
    source = (ROOT / "backend/app/api/v1/endpoints/companion.py").read_text(encoding="utf-8")
    assert "classify_companion_intent" in source
    assert "trigger_analysis(AnalyzeRequest" in source
    assert "URGENT_SAFETY_CONCERN" in source


def test_secret_configuration_has_no_insecure_default():
    source = (ROOT / "backend/app/core/security.py").read_text(encoding="utf-8")
    assert "JWT_SECRET_KEY" in source
    assert "super_secret_temporary" not in source
