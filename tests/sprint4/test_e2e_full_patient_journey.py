import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_end_to_end_synthetic_patient_journey():
    """
    Sprint 4 E2E Test: Full Synthetic Patient Journey across all CarePath features.
    Flow:
    1. Upload document (Lab Report)
    2. Analyze document & auto-post to Timeline & Memory
    3. Extract Medication & Confirm
    4. RAG Evidence Search
    5. Generate Explainable Referral (with navigation disclaimer)
    6. Generate Doctor Bridge Brief & Questions
    7. Submit Doctor Review (HITL Resume & Clinician-tagged feedback)
    8. Generate Care Plan (AI guidance vs Clinician instructions)
    9. Retrieve Patient Timeline
    """
    patient_id = "pat_s4_e2e_99"

    # Step 1: Upload Document
    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("blood_work.pdf", b"%PDF-1.4 sample lab report", "application/pdf")}
    )
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["document_id"]

    # Step 2: Analyze Document
    analyze_res = client.post(f"/api/v1/documents/{doc_id}/analyze")
    assert analyze_res.status_code == 200
    assert analyze_res.json()["status"] == "completed"

    # Step 3: Extract & Confirm Medication
    extract_res = client.post(
        "/api/v1/medications/extract",
        json={"prescription_text": "Metformin 500mg daily after breakfast"}
    )
    assert extract_res.status_code == 201
    meds = extract_res.json()["medications"]
    assert len(meds) > 0
    med_id = meds[0]["medication_id"]

    conf_res = client.post(f"/api/v1/medications/{med_id}/confirm")
    assert conf_res.status_code == 200
    assert conf_res.json()["medication"]["confirmed"] is True

    # Step 4: Evidence RAG Search
    evidence_res = client.post(
        "/api/v1/evidence/search",
        json={"query": "Type 2 diabetes glycemic control guidelines", "patient_context": {"age": 54}}
    )
    assert evidence_res.status_code == 200
    assert len(evidence_res.json()["sources"]) > 0

    # Step 5: Explainable Referral Recommendation
    ref_res = client.post(
        "/api/v1/referrals/recommend",
        json={"chief_complaint": "Elevated fasting blood sugar levels", "patient_id": patient_id}
    )
    assert ref_res.status_code == 201
    ref_data = ref_res.json()
    assert "specialist" in ref_data
    assert ref_data["disclaimer"] == "Navigation guidance, not a diagnosis."

    # Step 6: Doctor Bridge Brief & Questions
    brief_res = client.post(
        "/api/v1/doctor-bridge/brief",
        json={"patient_id": patient_id, "chief_complaint": "Glycemic fluctuation"}
    )
    assert brief_res.status_code == 201
    brief_id = brief_res.json()["brief_id"]

    questions_res = client.post("/api/v1/doctor-bridge/questions", params={"brief_id": brief_id})
    assert questions_res.status_code == 200
    assert len(questions_res.json()["questions"]) > 0

    # Step 7: Doctor Review (HITL Resume & Clinician-tagged feedback)
    review_res = client.post(
        "/api/v1/doctor-bridge/review",
        json={
            "brief_id": brief_id,
            "clinician_name": "Dr. Alan Grant, MD (Endocrinology)",
            "notes": "Patient advised to maintain daily glucose log and repeat HbA1c in 3 months.",
            "confirmed_next_step": "HbA1c Lab Repeat in 90 Days",
            "follow_up_instructions": "Contact office if fasting glucose exceeds 180 mg/dL."
        }
    )
    assert review_res.status_code == 201
    assert review_res.json()["review"]["is_clinician_feedback"] is True

    # Step 8: Personalized Care Plan Generation
    care_plan_res = client.post(
        "/api/v1/care-plans/generate",
        json={
            "patient_id": patient_id,
            "chief_complaint": "Glycemic fluctuation",
            "recommended_specialty": "Endocrinology",
            "doctor_notes": "Dr. Grant: Log daily glucose levels."
        }
    )
    assert care_plan_res.status_code == 201
    cp_data = care_plan_res.json()
    assert "ai_organization_guidance" in cp_data
    assert "clinician_provided_instructions" in cp_data

    # Step 9: Verify Patient Timeline automatically captured events
    timeline_res = client.get(f"/api/v1/timeline/{patient_id}")
    assert timeline_res.status_code == 200
    events = timeline_res.json()["timeline_events"]
    assert len(events) > 0
