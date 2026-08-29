"""
CarePath AI — Longitudinal Integration Test (Phase 3B)
======================================================
Tests the complete multi-day patient journey through the AUTHENTICATED API.

Flow tested:
  1. Register a fresh test patient
  2. Login → receive real signed JWT
  3. Day  1: POST /medical/update (rash onset)
  4. Day  1: POST /medical/analyze → LangGraph runs with 1 context entry
  5. Day 10: POST /medical/update (GP visit)
  6. Day 25: POST /medical/update (medicine not helping)
  7. Day 35: POST /medical/update (rash spreading — PROGRESSION)
  8. Day 35: POST /medical/analyze → LangGraph runs with 4 context entries
  9. GET /medical/recommendation → versioned analysis with changed_factors
  10. GET /medical/context → all 4 updates returned
  11. Verify UNAUTHORIZED without token (401)
  12. Verify FORBIDDEN for wrong patient (403)
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

TEST_EMAIL = f"longitudinal_test_{uuid.uuid4().hex[:8]}@carepath-test.local"
TEST_PASSWORD = "SecureTestPass#2026!"


def _get_auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestLongitudinalAuthenticatedFlow:
    """Complete multi-day patient journey with full auth."""

    token: str = ""
    patient_id: str = ""

    def test_01_register(self):
        """Register a fresh test patient."""
        resp = client.post("/api/v1/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        })
        assert resp.status_code == 201, f"Register failed: {resp.text}"
        data = resp.json()
        assert "user_id" in data
        TestLongitudinalAuthenticatedFlow.patient_id = data["user_id"]

    def test_02_login_real_jwt(self):
        """Login and receive a cryptographically signed JWT (not a mock string)."""
        resp = client.post("/api/v1/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        })
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        data = resp.json()
        assert "token" in data
        token = data["token"]
        # Real JWT has three base64url segments separated by dots
        assert token.count(".") == 2, "Token does not look like a real JWT (expected 3 segments)"
        assert not token.startswith("mock_"), "Token is still a mock token!"
        TestLongitudinalAuthenticatedFlow.token = token

    def test_03_profile_requires_auth(self):
        """Profile endpoint must reject unauthenticated requests."""
        resp = client.get("/api/v1/auth/profile")
        assert resp.status_code == 401

    def test_04_profile_authenticated(self):
        """Authenticated profile returns the correct user."""
        token = TestLongitudinalAuthenticatedFlow.token
        resp = client.get("/api/v1/auth/profile", headers=_get_auth_headers(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == TestLongitudinalAuthenticatedFlow.patient_id

    def test_05_update_requires_auth(self):
        """Medical update must reject unauthenticated requests."""
        patient_id = TestLongitudinalAuthenticatedFlow.patient_id
        resp = client.post("/api/v1/medical/update", json={
            "patient_id": patient_id,
            "update_type": "symptom",
            "content": "Red rash has appeared on my neck.",
        })
        assert resp.status_code == 401

    def test_06_day1_update(self):
        """Day 1: Submit initial symptom update (authenticated)."""
        token = TestLongitudinalAuthenticatedFlow.token
        patient_id = TestLongitudinalAuthenticatedFlow.patient_id
        resp = client.post("/api/v1/medical/update",
            json={"patient_id": patient_id, "update_type": "symptom",
                  "content": "Red rash has appeared on my neck."},
            headers=_get_auth_headers(token),
        )
        assert resp.status_code == 200, f"Day 1 update failed: {resp.text}"
        assert resp.json()["status"] == "success"

    def test_07_day1_analyze(self):
        """Day 1: Analyze — LangGraph runs with 1 historical context entry."""
        token = TestLongitudinalAuthenticatedFlow.token
        patient_id = TestLongitudinalAuthenticatedFlow.patient_id
        resp = client.post("/api/v1/medical/analyze",
            json={"patient_id": patient_id},
            headers=_get_auth_headers(token),
        )
        assert resp.status_code == 200, f"Day 1 analyze failed: {resp.text}"
        data = resp.json()
        assert data["status"] == "Analysis completed"
        assert data["historical_context_entries"] == 1
        assert data["agents_used"] is True
        assert data["previous_analysis_id"] is None  # no prior analysis

    def test_08_day10_update(self):
        """Day 10: Submit GP visit update."""
        token = TestLongitudinalAuthenticatedFlow.token
        patient_id = TestLongitudinalAuthenticatedFlow.patient_id
        resp = client.post("/api/v1/medical/update",
            json={"patient_id": patient_id, "update_type": "consultation",
                  "content": "Visited a general physician who prescribed a topical cream."},
            headers=_get_auth_headers(token),
        )
        assert resp.status_code == 200

    def test_09_day25_update(self):
        """Day 25: Treatment not helping."""
        token = TestLongitudinalAuthenticatedFlow.token
        patient_id = TestLongitudinalAuthenticatedFlow.patient_id
        resp = client.post("/api/v1/medical/update",
            json={"patient_id": patient_id, "update_type": "symptom",
                  "content": "The medicine has not helped. The rash persists."},
            headers=_get_auth_headers(token),
        )
        assert resp.status_code == 200

    def test_10_day35_progression_update(self):
        """Day 35: Rash spreading — clear progression signal."""
        token = TestLongitudinalAuthenticatedFlow.token
        patient_id = TestLongitudinalAuthenticatedFlow.patient_id
        resp = client.post("/api/v1/medical/update",
            json={"patient_id": patient_id, "update_type": "symptom",
                  "content": "The rash is getting worse and has spread toward my face."},
            headers=_get_auth_headers(token),
        )
        assert resp.status_code == 200

    def test_11_day35_analyze_with_full_history(self):
        """Day 35: Analyze with 4 entries in historical context — tests longitudinal reasoning."""
        token = TestLongitudinalAuthenticatedFlow.token
        patient_id = TestLongitudinalAuthenticatedFlow.patient_id
        resp = client.post("/api/v1/medical/analyze",
            json={"patient_id": patient_id},
            headers=_get_auth_headers(token),
        )
        assert resp.status_code == 200, f"Day 35 analyze failed: {resp.text}"
        data = resp.json()
        assert data["status"] == "Analysis completed"
        assert data["historical_context_entries"] == 4, (
            f"Expected 4 history entries, got {data['historical_context_entries']}"
        )
        assert data["previous_analysis_id"] is not None, "Second analysis must link to first"
        assert data["agents_used"] is True

        # Verify changed_factors are populated for progression
        changed = data.get("changed_factors") or []
        assert len(changed) > 0, "Progression should produce changed_factors"

    def test_12_recommendation_returns_versioned_analysis(self):
        """Recommendation endpoint returns latest analysis with versioning."""
        token = TestLongitudinalAuthenticatedFlow.token
        patient_id = TestLongitudinalAuthenticatedFlow.patient_id
        resp = client.get(f"/api/v1/medical/recommendation/{patient_id}",
            headers=_get_auth_headers(token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "analysis_id" in data
        assert data["previous_analysis_id"] is not None
        # changed_factors should be non-empty after progression
        cf = data.get("changed_factors")
        assert cf is not None and len(cf) > 0

    def test_13_context_returns_all_updates(self):
        """Context endpoint returns all 4 historical updates."""
        token = TestLongitudinalAuthenticatedFlow.token
        patient_id = TestLongitudinalAuthenticatedFlow.patient_id
        resp = client.get(f"/api/v1/medical/context/{patient_id}",
            headers=_get_auth_headers(token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_entries"] == 4

    def test_14_cross_patient_forbidden(self):
        """A user cannot access another patient's data — must get HTTP 403."""
        token = TestLongitudinalAuthenticatedFlow.token
        other_patient_id = str(uuid.uuid4())
        # Attempt to update a random patient's data
        resp = client.post("/api/v1/medical/update",
            json={"patient_id": other_patient_id, "update_type": "symptom",
                  "content": "Unauthorized access attempt."},
            headers=_get_auth_headers(token),
        )
        assert resp.status_code == 403, (
            f"Expected 403 Forbidden for cross-patient access, got {resp.status_code}"
        )

    def test_15_expired_token_rejected(self):
        """Fabricated / invalid token must be rejected with HTTP 401."""
        resp = client.post("/api/v1/medical/update",
            json={"patient_id": str(uuid.uuid4()), "update_type": "symptom",
                  "content": "test"},
            headers={"Authorization": "Bearer definitely.not.valid"},
        )
        assert resp.status_code == 401
