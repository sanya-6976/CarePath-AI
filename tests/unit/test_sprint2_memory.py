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
from database.crud import create_user, create_patient_profile, create_symptom, create_medical_file
from backend.app.services import (
    memory_service, doctor_service, medication_service, careplan_service, followup_service, timeline_service
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
        email="sprint2_patient@carepath.ai",
        password_hash="hashed_pw",
        role="patient",
        account_status="active",
        created_at=datetime.now(timezone.utc)
    )
    profile = create_patient_profile(
        session=db_session,
        user_id=u_id,
        first_name="Jane",
        last_name="Doe",
        gender="Female",
        blood_group="O+",
        medical_summary="Chronic asthma, hypertension",
        created_at=datetime.now(timezone.utc)
    )
    return user

class TestSprint2CarePathMemoryAndDoctor:

    def test_carepath_memory_aggregation(self, db_session, test_patient):
        p_id = str(test_patient.user_id)

        # Populate patient data across domain entities
        # 1. Symptom
        create_symptom(
            db_session,
            symptom_id=uuid.uuid4(),
            user_id=test_patient.user_id,
            symptom_name="Shortness of breath",
            severity="MODERATE",
            created_at=datetime.now(timezone.utc)
        )

        # 2. Consultation
        doctor_service.create_consultation(
            db_session,
            {
                "user_id": p_id,
                "provider_name": "Dr. Sarah Jenkins",
                "visit_reason": "Routine Cardiology Follow-up",
                "notes": "ECG normal, continuation of beta-blockers advised."
            }
        )

        # 3. Medical File / Report
        create_medical_file(
            db_session,
            file_id=uuid.uuid4(),
            user_id=test_patient.user_id,
            file_name="echocardiogram.pdf",
            storage_path="docs/echo.pdf",
            file_type="lab_report",
            upload_date=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )

        # 4. Medication
        medication_service.add_medication(
            db_session,
            {
                "user_id": p_id,
                "medication_name": "Metoprolol",
                "dosage": "50mg daily",
                "status": "ACTIVE"
            }
        )

        # 5. Care Plan
        plan = careplan_service.create_care_plan(
            db_session,
            {
                "user_id": p_id,
                "plan_name": "Cardiovascular Health Protocol",
                "priority": "HIGH"
            }
        )

        # 6. Doctor Feedback
        doctor_service.add_doctor_feedback(
            db_session,
            {
                "user_id": p_id,
                "title": "Care Plan Approval",
                "message": "Protocol reviewed and approved by Cardiology Lead.",
                "related_record_id": str(plan.plan_id),
                "related_record_type": "CARE_PLAN",
                "status": "APPROVED"
            }
        )

        # 7. Timeline Event
        timeline_service.add_timeline_event(
            db_session,
            {
                "user_id": p_id,
                "event_type": "CONSULTATION",
                "event_title": "Completed Cardiology Follow-up"
            }
        )

        # Execute CarePath Memory Aggregation
        memory = memory_service.get_patient_carepath_memory(db_session, p_id)

        # Assert full tree integrity
        assert memory["patient_profile"]["first_name"] == "Jane"
        assert memory["patient_profile"]["blood_group"] == "O+"
        assert len(memory["symptoms"]) == 1
        assert memory["symptoms"][0]["symptom_name"] == "Shortness of breath"
        assert len(memory["consultations"]) == 1
        assert memory["consultations"][0]["provider_name"] == "Dr. Sarah Jenkins"
        assert len(memory["reports"]) == 1
        assert memory["reports"][0]["file_name"] == "echocardiogram.pdf"
        assert len(memory["prescriptions_and_medications"]) == 1
        assert memory["prescriptions_and_medications"][0]["medication_name"] == "Metoprolol"
        assert len(memory["care_plans"]) == 1
        assert memory["care_plans"][0]["plan_name"] == "Cardiovascular Health Protocol"
        assert len(memory["doctor_feedback"]) == 1
        assert memory["doctor_feedback"][0]["title"] == "Care Plan Approval"
        assert len(memory["timeline_events"]) >= 1

    def test_doctor_bridge_consultations_and_reviews(self, db_session, test_patient):
        p_id = str(test_patient.user_id)

        # Doctor Consultation
        consultation = doctor_service.create_consultation(
            db_session,
            {
                "user_id": p_id,
                "provider_name": "Dr. Marcus Vance",
                "visit_reason": "Pre-op evaluation",
                "status": "COMPLETED"
            }
        )
        assert consultation.provider_name == "Dr. Marcus Vance"

        consultations = doctor_service.get_patient_consultations(db_session, p_id)
        assert len(consultations) == 1
        assert consultations[0].visit_reason == "Pre-op evaluation"
