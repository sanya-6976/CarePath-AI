import sys
import os
import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))

from database.models import Base, User
from database.crud import create_user, create_patient_profile, create_symptom
from backend.app.services import (
    medication_service, careplan_service, followup_service, timeline_service, analytics_service
)

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_patient(db_session):
    u_id = uuid.uuid4()
    user = create_user(
        session=db_session,
        user_id=u_id,
        email="sprint3_patient@carepath.ai",
        password_hash="hashed_pw",
        role="patient",
        account_status="active",
        created_at=datetime.now(timezone.utc)
    )
    profile = create_patient_profile(
        session=db_session,
        user_id=u_id,
        first_name="John",
        last_name="Smith",
        gender="Male",
        blood_group="A+",
        created_at=datetime.now(timezone.utc)
    )
    return user

class TestSprint3ContinuityOfCare:

    def test_medication_adherence_calculation(self, db_session, test_patient):
        p_id = str(test_patient.user_id)

        # Add 3 medications (2 active, 1 completed)
        m1 = medication_service.add_medication(
            db_session,
            {"user_id": p_id, "medication_name": "Lisinopril", "status": "ACTIVE"}
        )
        m2 = medication_service.add_medication(
            db_session,
            {"user_id": p_id, "medication_name": "Atorvastatin", "status": "ACTIVE"}
        )
        m3 = medication_service.add_medication(
            db_session,
            {"user_id": p_id, "medication_name": "Amoxicillin", "status": "COMPLETED"}
        )

        adherence = medication_service.get_medication_adherence(db_session, p_id)
        assert adherence["total_medications"] == 3
        assert adherence["active_medications"] == 2
        assert adherence["completed_medications"] == 1
        assert adherence["adherence_percentage"] == 100.0

    def test_timeline_automatic_event_trigger(self, db_session, test_patient):
        p_id = str(test_patient.user_id)

        # Adding a medication triggers timeline auto-log
        medication_service.add_medication(
            db_session,
            {"user_id": p_id, "medication_name": "Metformin", "dosage": "500mg"}
        )

        timeline_events = timeline_service.get_timeline_events(db_session, p_id)
        assert len(timeline_events) == 1
        assert "Metformin" in timeline_events[0].event_title
        assert timeline_events[0].event_type == "MEDICATION"

    def test_analytics_service_aggregation(self, db_session, test_patient):
        p_id = str(test_patient.user_id)

        # 1. Symptom
        create_symptom(
            db_session,
            symptom_id=uuid.uuid4(),
            user_id=test_patient.user_id,
            symptom_name="Chest tightness",
            severity="HIGH",
            created_at=datetime.now(timezone.utc)
        )

        # 2. Care Plan
        careplan_service.create_care_plan(
            db_session,
            {"user_id": p_id, "plan_name": "Angina Management", "status": "ACTIVE"}
        )

        # 3. Follow-up
        followup_service.create_followup(
            db_session,
            {"user_id": p_id, "followup_type": "ECG_CHECK", "status": "SCHEDULED"}
        )

        analytics = analytics_service.get_patient_analytics(db_session, p_id)
        assert analytics["patient_id"] == p_id
        assert analytics["care_plans"]["total"] == 1
        assert analytics["follow_ups"]["scheduled"] == 1
        assert analytics["symptoms"]["severity_distribution"]["HIGH"] == 1
