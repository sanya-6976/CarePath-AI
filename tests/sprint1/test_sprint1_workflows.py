import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


# ── 1. Smart Document Analyzer Tests ──────────────────────────────────────────

def test_document_upload_valid():
    """Test valid PDF document upload."""
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("lab_report.pdf", b"%PDF-1.4 dummy content", "application/pdf")}
    )
    assert response.status_code == 201
    data = response.json()
    assert "document_id" in data
    assert data["status"] == "uploaded"


def test_document_upload_invalid_extension():
    """Test rejection of unsupported file extension."""
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("malware.exe", b"binary content", "application/octet-stream")}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "INVALID_REQUEST"


def test_document_analysis_and_status():
    """Test document analysis execution and status retrieval."""
    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("blood_test.png", b"fake image bytes", "image/png")}
    )
    doc_id = upload_res.json()["document_id"]

    analyze_res = client.post(f"/api/v1/documents/{doc_id}/analyze")
    assert analyze_res.status_code == 200
    assert analyze_res.json()["status"] == "completed"

    get_res = client.get(f"/api/v1/documents/{doc_id}")
    assert get_res.status_code == 200
    assert get_res.json()["document_id"] == doc_id
    assert "extracted_information" in get_res.json()


# ── 2. Medication Companion Tests ─────────────────────────────────────────────

def test_medication_extraction_workflow():
    """Test extraction of structured medications from prescription text."""
    payload = {"prescription_text": "Amoxicillin 500mg TID for 7 days. Take after meals."}
    response = client.post("/api/v1/medications/extract", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "medications" in data
    assert len(data["medications"]) > 0
    assert data["medications"][0]["medication_name"] == "Amoxicillin"


def test_medication_confirmation_and_action_logging():
    """Test medication patient confirmation, scheduling, taken and skipped logging."""
    extract_res = client.post(
        "/api/v1/medications/extract",
        json={"prescription_text": "Ibuprofen 400mg every 8 hours"}
    )
    med_id = extract_res.json()["medications"][0]["medication_id"]

    # Confirm
    conf_res = client.post(f"/api/v1/medications/{med_id}/confirm")
    assert conf_res.status_code == 200
    assert conf_res.json()["medication"]["confirmed"] is True

    # Schedule
    sched_payload = {"reminder_times": ["08:00", "16:00", "00:00"], "start_date": "2026-08-15"}
    sched_res = client.post(f"/api/v1/medications/{med_id}/schedule", json=sched_payload)
    assert sched_res.status_code == 200

    # Taken
    taken_res = client.post(f"/api/v1/medications/{med_id}/taken")
    assert taken_res.status_code == 200

    # Skipped
    skip_res = client.post(f"/api/v1/medications/{med_id}/skipped", json={"reason": "Stomach upset"})
    assert skip_res.status_code == 200


# ── 3. Evidence / RAG Search Tests ────────────────────────────────────────────

def test_evidence_search_success():
    """Test clinical evidence retrieval from RAG service."""
    payload = {
        "query": "Acute appendicitis right lower quadrant triage",
        "patient_context": {"age": 28, "gender": "male"}
    }
    response = client.post("/api/v1/evidence/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert len(data["sources"]) > 0
    assert "title" in data["sources"][0]
