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
from database.crud import (
    create_user,
    create_medical_file, get_user_medical_files, get_medical_file_by_id, delete_medical_file,
    create_medication, get_user_medications, get_medication_by_id, update_medication_status,
    create_care_plan, get_user_care_plans, get_care_plan_by_id, update_care_plan_status,
    create_followup, get_user_followups, get_followup_by_id, update_followup_status,
    create_timeline_event, get_user_timeline_events,
    create_agent_run, create_evidence, get_user_evidence, get_evidence_by_run
)
from backend.app.services import medication_service, careplan_service, followup_service, timeline_service

# Use in-memory SQLite database for testing
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
def test_user(db_session):
    u_id = uuid.uuid4()
    user = create_user(
        session=db_session,
        user_id=u_id,
        email="test_sprint1@carepath.ai",
        password_hash="hashed_pw",
        role="patient",
        account_status="active",
        created_at=datetime.now(timezone.utc)
    )
    return user

class TestSprint1CRUD:

    def test_medical_file_crud(self, db_session, test_user):
        # Create medical file
        file_id = uuid.uuid4()
        f = create_medical_file(
            session=db_session,
            file_id=file_id,
            user_id=test_user.user_id,
            file_name="blood_test.pdf",
            storage_path="uploads/blood_test.pdf",
            file_type="lab_report",
            mime_type="application/pdf",
            file_size=1024,
            upload_date=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        assert f.file_name == "blood_test.pdf"

        # Read medical files
        user_files = get_user_medical_files(db_session, test_user.user_id)
        assert len(user_files) == 1

        lab_files = get_user_medical_files(db_session, test_user.user_id, file_type="lab_report")
        assert len(lab_files) == 1

        fetched_file = get_medical_file_by_id(db_session, file_id)
        assert fetched_file is not None
        assert fetched_file.file_name == "blood_test.pdf"

        # Delete medical file
        deleted = delete_medical_file(db_session, file_id)
        assert deleted is True
        assert get_medical_file_by_id(db_session, file_id) is None

    def test_medication_crud_and_service(self, db_session, test_user):
        med = medication_service.add_medication(
            db_session,
            {
                "user_id": str(test_user.user_id),
                "medication_name": "Amoxicillin",
                "dosage": "500mg",
                "frequency": "Three times a day",
                "duration": "7 days",
                "status": "ACTIVE"
            }
        )
        assert med.medication_name == "Amoxicillin"

        meds = medication_service.get_patient_medications(db_session, str(test_user.user_id), status="ACTIVE")
        assert len(meds) == 1

        updated = medication_service.update_medication_status(db_session, str(med.medication_id), status="COMPLETED")
        assert updated.status == "COMPLETED"

    def test_careplan_crud_and_service(self, db_session, test_user):
        plan = careplan_service.create_care_plan(
            db_session,
            {
                "user_id": str(test_user.user_id),
                "plan_name": "Hypertension Management Plan",
                "plan_description": "Reduce sodium intake, monitor blood pressure daily.",
                "priority": "HIGH",
                "status": "ACTIVE"
            }
        )
        assert plan.plan_name == "Hypertension Management Plan"

        plans = careplan_service.get_patient_care_plans(db_session, str(test_user.user_id))
        assert len(plans) == 1

        updated_plan = careplan_service.update_care_plan_status(db_session, str(plan.plan_id), "COMPLETED")
        assert updated_plan.status == "COMPLETED"
        assert updated_plan.completed_at is not None

    def test_followup_crud_and_service(self, db_session, test_user):
        fup = followup_service.create_followup(
            db_session,
            {
                "user_id": str(test_user.user_id),
                "followup_type": "CHECK_IN",
                "description": "Check blood pressure log",
                "purpose": "Evaluate medication effectiveness"
            }
        )
        assert fup.status == "SCHEDULED"

        fups = followup_service.get_followups(db_session, str(test_user.user_id), status="SCHEDULED")
        assert len(fups) == 1

        completed = followup_service.complete_followup(db_session, str(fup.followup_id), notes="Blood pressure stabilized")
        assert completed.status == "COMPLETED"
        assert completed.notes == "Blood pressure stabilized"

    def test_timeline_crud_and_service(self, db_session, test_user):
        evt = timeline_service.add_timeline_event(
            db_session,
            {
                "user_id": str(test_user.user_id),
                "event_type": "DIAGNOSIS",
                "event_title": "Diagnosed with mild hypertension",
                "severity": "MEDIUM"
            }
        )
        assert evt.event_title == "Diagnosed with mild hypertension"

        timeline = timeline_service.get_timeline_events(db_session, str(test_user.user_id))
        assert len(timeline) == 1

    def test_evidence_retrieval_crud(self, db_session, test_user):
        run_id = uuid.uuid4()
        run = create_agent_run(
            session=db_session,
            run_id=run_id,
            user_id=test_user.user_id,
            agent_name="evidence_agent",
            status="SUCCESS",
            created_at=datetime.now(timezone.utc)
        )

        ev_id = uuid.uuid4()
        ev = create_evidence(
            session=db_session,
            evidence_id=ev_id,
            run_id=run.run_id,
            source_type="GUIDELINE",
            source_reference="AHA Hypertension Guidelines 2023",
            evidence_text="Target blood pressure < 130/80 mm Hg",
            relevance_score=0.95,
            retrieval_timestamp=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )

        evidence_list = get_user_evidence(db_session, test_user.user_id)
        assert len(evidence_list) == 1
        assert evidence_list[0].evidence_text == "Target blood pressure < 130/80 mm Hg"

        run_ev = get_evidence_by_run(db_session, run_id)
        assert len(run_ev) == 1
