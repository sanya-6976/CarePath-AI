import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


# ── 1. Doctor Bridge & HITL Tests ─────────────────────────────────────────────

def test_doctor_bridge_brief_and_questions():
    """Test Doctor Brief generation and case-specific questions."""
    payload = {
        "patient_id": "pat_test_001",
        "chief_complaint": "Persistent RLQ abdominal pain with mild fever for 12 hours",
        "symptoms_duration": "12 hours",
        "symptoms_severity": 7
    }
    brief_res = client.post("/api/v1/doctor-bridge/brief", json=payload)
    assert brief_res.status_code == 201
    brief_data = brief_res.json()
    brief_id = brief_data["brief_id"]
    assert "chief_complaint" in brief_data

    # Generate questions
    q_res = client.post("/api/v1/doctor-bridge/questions", params={"brief_id": brief_id})
    assert q_res.status_code == 200
    assert "questions" in q_res.json()
    assert len(q_res.json()["questions"]) > 0


def test_doctor_review_and_hitl_resume():
    """Test Doctor Review submission and tagging as clinician-provided feedback."""
    brief_res = client.post(
        "/api/v1/doctor-bridge/brief",
        json={"chief_complaint": "Severe stomach discomfort"}
    )
    brief_id = brief_res.json()["brief_id"]

    review_payload = {
        "brief_id": brief_id,
        "clinician_name": "Dr. Sarah Jenkins, MD",
        "notes": "Patient presents with localized tenderness. Prescribed ultrasound.",
        "confirmed_next_step": "Urgent Abdominal Ultrasound",
        "follow_up_instructions": "Return if fever exceeds 38.5C"
    }

    rev_res = client.post("/api/v1/doctor-bridge/review", json=review_payload)
    assert rev_res.status_code == 201
    rev_data = rev_res.json()
    assert rev_data["status"] == "SUCCESS"
    assert rev_data["review"]["is_clinician_feedback"] is True


# ── 2. Patient Timeline Tests ──────────────────────────────────────────────────

def test_patient_timeline_events_and_summary():
    """Test retrieval of patient timeline events and narrative summary."""
    patient_id = "pat_timeline_99"

    # Add custom event
    add_res = client.post(
        "/api/v1/timeline/events",
        params={"patient_id": patient_id},
        json={"event_type": "LAB_TEST", "description": "Blood work CBC completed.", "source": "Lab"}
    )
    assert add_res.status_code == 201

    get_res = client.get(f"/api/v1/timeline/{patient_id}")
    assert get_res.status_code == 200
    assert len(get_res.json()["timeline_events"]) > 0

    sum_res = client.get(f"/api/v1/timeline/{patient_id}/summary")
    assert sum_res.status_code == 200
    assert "summary_narrative" in sum_res.json()


# ── 3. Explainable Referral Tests ──────────────────────────────────────────────

def test_explainable_referral_recommendation_and_disclaimer():
    """Test referral recommendation with mandatory disclaimer."""
    payload = {
        "chief_complaint": "Severe right lower quadrant pain with fever",
        "symptoms_duration": "12 hours",
        "symptoms_severity": 8
    }
    response = client.post("/api/v1/referrals/recommend", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "specialist" in data
    assert "reasoning" in data
    assert data["disclaimer"] == "Navigation guidance, not a diagnosis."


# ── 4. Personalized Care Plan Tests ───────────────────────────────────────────

def test_care_plan_generation_and_clinician_instruction_separation():
    """Test Care Plan generation with explicit separation of AI guidance vs Clinician instructions."""
    payload = {
        "chief_complaint": "Abdominal pain",
        "recommended_specialty": "General Surgery",
        "doctor_notes": "Dr. Miller: Avoid heavy food for 24 hours."
    }
    response = client.post("/api/v1/care-plans/generate", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "ai_organization_guidance" in data
    assert "clinician_provided_instructions" in data
    assert len(data["clinician_provided_instructions"]) > 0
