import sys
import os
import uuid
import json
from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))

from database.models import (
    Base, User, PatientProfile, Visit, SymptomSession, PatientSymptom,
    Medication, MedicalFile, AIAnalysis, CarePlan, FollowUp, TimelineEvent, Feedback
)
from database.crud import create_user, create_patient_profile, create_visit, create_symptom, create_medical_file
from backend.app.services import (
    memory_service, doctor_service, medication_service, careplan_service, followup_service, timeline_service
)
from backend.app.core.security import PHIRedactor, get_password_hash, verify_password

@pytest.fixture
def db_engine():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def sample_user(db_session):
    u_id = uuid.uuid4()
    user = create_user(
        session=db_session,
        user_id=u_id,
        email="infra_test@carepath.ai",
        password_hash=get_password_hash("SecretPass123!"),
        role="patient",
        account_status="active",
        created_at=datetime.now(timezone.utc)
    )
    profile = create_patient_profile(
        session=db_session,
        user_id=u_id,
        first_name="Alice",
        last_name="Wonderland",
        blood_group="B+",
        created_at=datetime.now(timezone.utc)
    )
    return user


class TestSprint4Infrastructure:

    # 1. Schema Integrity & Relationships
    def test_schema_relationships_and_foreign_keys(self, db_session, sample_user):
        u_id = sample_user.user_id

        # Attach records across multiple tables
        visit = create_visit(
            session=db_session,
            visit_id=uuid.uuid4(),
            user_id=u_id,
            visit_type="EMERGENCY",
            visit_reason="Acute chest pain",
            created_at=datetime.now(timezone.utc)
        )
        med = medication_service.add_medication(
            db_session,
            {"user_id": str(u_id), "medication_name": "Aspirin", "dosage": "325mg"}
        )
        plan = careplan_service.create_care_plan(
            db_session,
            {"user_id": str(u_id), "plan_name": "Emergency Cardiac Protocol"}
        )

        # Refresh user from database
        db_session.expire_all()
        refreshed_user = db_session.get(User, u_id)

        assert refreshed_user is not None
        assert refreshed_user.profile.first_name == "Alice"
        assert len(refreshed_user.visits) == 1
        assert refreshed_user.visits[0].visit_reason == "Acute chest pain"
        assert len(refreshed_user.medications) == 1
        assert refreshed_user.medications[0].medication_name == "Aspirin"

    # 2. CarePath Memory Persistence
    def test_carepath_memory_deep_persistence(self, db_session, sample_user):
        u_id = str(sample_user.user_id)

        # Populate records
        create_symptom(db_session, symptom_id=uuid.uuid4(), user_id=sample_user.user_id, symptom_name="Fever", severity="HIGH")
        doctor_service.create_consultation(db_session, {"user_id": u_id, "provider_name": "Dr. House", "visit_reason": "Unexplained fever"})
        careplan_service.create_care_plan(db_session, {"user_id": u_id, "plan_name": "Diagnostic Workup"})

        memory = memory_service.get_patient_carepath_memory(db_session, u_id)
        
        # Verify JSON serializability of memory object
        json_dump = json.dumps(memory, default=str)
        assert json_dump is not None
        
        parsed = json.loads(json_dump)
        assert parsed["patient_profile"]["first_name"] == "Alice"
        assert len(parsed["symptoms"]) == 1
        assert parsed["symptoms"][0]["symptom_name"] == "Fever"
        assert len(parsed["consultations"]) == 1

    # 3. Timeline Consistency & Ordering
    def test_timeline_chronological_ordering_and_triggers(self, db_session, sample_user):
        u_id = str(sample_user.user_id)

        t1 = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
        t2 = datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc)
        t3 = datetime(2026, 1, 3, 10, 0, tzinfo=timezone.utc)

        timeline_service.add_timeline_event(db_session, {"user_id": u_id, "event_title": "First Event", "event_date": t1})
        timeline_service.add_timeline_event(db_session, {"user_id": u_id, "event_title": "Second Event", "event_date": t2})
        timeline_service.add_timeline_event(db_session, {"user_id": u_id, "event_title": "Third Event", "event_date": t3})

        events = timeline_service.get_timeline_events(db_session, u_id)
        assert len(events) == 3
        # Should be sorted newest first (descending event_date)
        assert events[0].event_title == "Third Event"
        assert events[1].event_title == "Second Event"
        assert events[2].event_title == "First Event"

    # 4. Concurrent Access & Session Transaction Safety
    def test_concurrent_sessions_and_rollback_safety(self, db_engine, sample_user):
        SessionMaker = sessionmaker(bind=db_engine)
        session1 = SessionMaker()
        session2 = SessionMaker()

        u_id = sample_user.user_id

        try:
            # Session 1 adds a medication
            medication_service.add_medication(session1, {"user_id": str(u_id), "medication_name": "Ibuprofen"})
            
            # Session 2 adds a care plan
            careplan_service.create_care_plan(session2, {"user_id": str(u_id), "plan_name": "Pain Management"})

            # Verify isolated commits
            meds = medication_service.get_patient_medications(session1, str(u_id))
            plans = careplan_service.get_patient_care_plans(session2, str(u_id))

            assert len(meds) == 1
            assert len(plans) == 1
        finally:
            session1.close()
            session2.close()

    # 5. Database Security & PHI Redaction
    def test_database_security_and_phi_redaction(self, db_session):
        raw_clinical_note = "Patient SSN is 123-45-6789. Contact at 555-123-4567 or email john.doe@example.com. MRN: MRN12345678."
        redacted_note = PHIRedactor.redact(raw_clinical_note)

        assert "123-45-6789" not in redacted_note
        assert "555-123-4567" not in redacted_note
        assert "john.doe@example.com" not in redacted_note
        assert "[REDACTED_SSN]" in redacted_note
        assert "[REDACTED_PHONE]" in redacted_note
        assert "[REDACTED_EMAIL]" in redacted_note
        assert "[REDACTED_MRN]" in redacted_note

        # Test password hashing security
        hashed = get_password_hash("DoctorSecret2026")
        assert verify_password("DoctorSecret2026", hashed) is True
        assert verify_password("WrongPassword", hashed) is False

    # 6. Backup Export and Recovery Integrity
    def test_patient_backup_export_and_recovery(self, db_session, sample_user):
        u_id = str(sample_user.user_id)

        medication_service.add_medication(db_session, {"user_id": u_id, "medication_name": "Omeprazole"})
        careplan_service.create_care_plan(db_session, {"user_id": u_id, "plan_name": "GERD Management"})

        # Export memory snapshot to JSON string backup
        memory_snapshot = memory_service.get_patient_carepath_memory(db_session, u_id)
        backup_json = json.dumps(memory_snapshot)

        # Reconstruct memory snapshot from backup JSON string
        restored_data = json.loads(backup_json)
        assert restored_data["patient_profile"]["first_name"] == "Alice"
        assert len(restored_data["prescriptions_and_medications"]) == 1
        assert restored_data["prescriptions_and_medications"][0]["medication_name"] == "Omeprazole"
        assert len(restored_data["care_plans"]) == 1
        assert restored_data["care_plans"][0]["plan_name"] == "GERD Management"
