import os
import sys
import uuid
import random
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connections import SessionLocal
from database import crud
from database.models import *

def populate():
    session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        base_time = now - timedelta(days=30) # Start timeline 30 days ago

        print("Locating existing user: abhay@gmail.com")
        user = crud.get_user_by_email(session, "abhay@gmail.com")
        if not user:
            print("User abhay@gmail.com not found. Creating it...")
            user = crud.create_user(
                session=session,
                user_id=uuid.uuid4(),
                email="abhay@gmail.com",
                password_hash="fake_hash",
                role="patient",
                account_status="active",
                created_at=base_time,
                updated_at=base_time
            )
        u_id = user.user_id
        print(f"Using User ID: {u_id}")

        # 1. Patient Profile
        print("Populating Patient Profile...")
        profile = crud.get_patient_profile(session, u_id)
        if profile:
            crud.utils.update_record(session, PatientProfile, u_id,
                first_name="Abhay", last_name="Sharma",
                date_of_birth=datetime(1990, 5, 14, tzinfo=timezone.utc),
                gender="Male", height=175.0, weight=70.0, blood_group="O+",
                medical_summary="Generally healthy, mild seasonal allergies.",
                updated_at=now
            )
        else:
            crud.create_patient_profile(
                session=session,
                user_id=u_id,
                first_name="Abhay", last_name="Sharma",
                date_of_birth=datetime(1990, 5, 14, tzinfo=timezone.utc),
                gender="Male", height=175.0, weight=70.0, blood_group="O+",
                medical_summary="Generally healthy, mild seasonal allergies.",
                created_at=base_time, updated_at=base_time
            )

        # 2. Visits
        print("Populating Visits...")
        visit1 = crud.create_visit(session=session, visit_id=uuid.uuid4(), user_id=u_id, visit_type="consultation", provider_name="Dr. Smith", facility_name="City Clinic", visit_date=base_time + timedelta(days=1), duration=30, visit_reason="General Consultation", status="completed", created_at=base_time, updated_at=base_time)
        visit2 = crud.create_visit(session=session, visit_id=uuid.uuid4(), user_id=u_id, visit_type="appointment", provider_name="Dr. Smith", facility_name="City Clinic", visit_date=now - timedelta(days=2), duration=20, visit_reason="Routine Follow-up", status="completed", created_at=now, updated_at=now)

        # 3. Medical Files
        print("Populating Medical Files...")
        crud.create_medical_file(session=session, file_id=uuid.uuid4(), user_id=u_id, visit_id=visit1.visit_id, file_name="blood_report.pdf", storage_path=f"medical_files/{u_id}/blood_report.pdf", file_type="application/pdf", mime_type="application/pdf", file_size=150000, upload_date=base_time + timedelta(days=2), analysis_status="completed", created_at=base_time, updated_at=base_time)
        crud.create_medical_file(session=session, file_id=uuid.uuid4(), user_id=u_id, visit_id=visit1.visit_id, file_name="chest_xray.png", storage_path=f"medical_files/{u_id}/chest_xray.png", file_type="image/png", mime_type="image/png", file_size=2048000, upload_date=base_time + timedelta(days=2), analysis_status="completed", created_at=base_time, updated_at=base_time)
        crud.create_medical_file(session=session, file_id=uuid.uuid4(), user_id=u_id, visit_id=visit2.visit_id, file_name="prescription.pdf", storage_path=f"medical_files/{u_id}/prescription.pdf", file_type="application/pdf", mime_type="application/pdf", file_size=50000, upload_date=now - timedelta(days=1), analysis_status="pending", created_at=now, updated_at=now)

        # 4. Symptom Sessions
        print("Populating Symptom Sessions...")
        sess1 = crud.create_session(session=session, session_id=uuid.uuid4(), user_id=u_id, session_date=base_time, session_type="initial", status="completed", created_at=base_time, updated_at=base_time)
        sess2 = crud.create_session(session=session, session_id=uuid.uuid4(), user_id=u_id, session_date=now - timedelta(days=3), session_type="reassessment", status="completed", created_at=now, updated_at=now)

        # 5. Patient Symptoms
        print("Populating Symptoms...")
        symptoms_data = [
            (sess1.session_id, "Fatigue", "Feeling tired all the time", "moderate", "2 weeks", "whole body"),
            (sess1.session_id, "Headache", "Throbbing pain in forehead", "mild", "3 days", "head"),
            (sess1.session_id, "Mild Fever", "Temp 99.5F", "mild", "1 day", "body"),
            (sess2.session_id, "Joint Pain", "Aching knees", "moderate", "1 week", "knees"),
            (sess2.session_id, "Cough", "Dry cough", "mild", "2 days", "throat"),
            (sess2.session_id, "Muscle Pain", "Sore back", "mild", "3 days", "back")
        ]
        symptom_ids = []
        for sid, name, desc, sev, dur, loc in symptoms_data:
            s = crud.create_symptom(session=session, symptom_id=uuid.uuid4(), session_id=sid, user_id=u_id, symptom_name=name, symptom_description=desc, onset_date=base_time, severity=sev, duration=dur, location=loc, created_at=now, updated_at=now)
            symptom_ids.append(s.symptom_id)

        # 6. AI Analysis
        print("Populating AI Analysis...")
        analysis1 = crud.create_analysis(session=session, analysis_id=uuid.uuid4(), user_id=u_id, session_id=sess1.session_id, analysis_type="differential_diagnosis", findings="Patient shows signs of viral infection.", differential_list="1. Viral Fever, 2. Common Cold", confidence_score=0.85, risk_level="low", summary="Mild viral infection expected to clear in a few days.", created_at=base_time, updated_at=base_time)
        analysis2 = crud.create_analysis(session=session, analysis_id=uuid.uuid4(), user_id=u_id, session_id=sess2.session_id, analysis_type="risk_assessment", findings="Joint and muscle pain without high fever.", differential_list="1. Physical strain, 2. Mild arthritis", confidence_score=0.75, risk_level="low", summary="Strain from physical activity.", created_at=now, updated_at=now)

        # 7. Recommendations
        print("Populating Recommendations...")
        crud.create_recommendation(session=session, recommendation_id=uuid.uuid4(), analysis_id=analysis1.analysis_id, user_id=u_id, recommendation_type="lifestyle", title="Rest", description="Get plenty of rest for 3 days.", confidence=0.9, urgency="routine", rationale="Rest allows immune system to recover.", status="pending", created_at=base_time, updated_at=base_time)
        crud.create_recommendation(session=session, recommendation_id=uuid.uuid4(), analysis_id=analysis1.analysis_id, user_id=u_id, recommendation_type="lifestyle", title="Hydration", description="Drink 3 liters of water.", confidence=0.95, urgency="routine", rationale="Hydration clears toxins.", status="completed", created_at=base_time, updated_at=base_time)

        # 8. Care Plans
        print("Populating Care Plans...")
        plan1 = crud.create_care_plan(session=session, plan_id=uuid.uuid4(), user_id=u_id, analysis_id=analysis1.analysis_id, plan_name="Recovery Plan", plan_description="Short term recovery plan for viral infection.", status="active", next_steps="Follow up in 2 weeks if symptoms persist.", appointment_prep="Bring latest blood reports.", lifestyle_changes="Increase fluid intake.", monitoring_points="Monitor body temperature.", estimated_duration="2 weeks", priority="low", created_at=base_time, updated_at=base_time)

        # 9. Follow Ups
        print("Populating Follow-ups...")
        crud.create_followup(session=session, followup_id=uuid.uuid4(), user_id=u_id, plan_id=plan1.plan_id, followup_type="checkpoint", scheduled_date=now - timedelta(days=1), description="Check fever", purpose="Monitor temp", status="completed", completed_date=now, created_at=base_time, updated_at=base_time)
        crud.create_followup(session=session, followup_id=uuid.uuid4(), user_id=u_id, plan_id=plan1.plan_id, followup_type="review", scheduled_date=now + timedelta(days=7), description="Final review", purpose="Assess recovery", status="pending", created_at=now, updated_at=now)

        # 10. Notifications
        print("Populating Notifications...")
        notifs = [
            ("reminder", "Follow-up Reminder", "You have a follow up scheduled tomorrow.", "medium", plan1.plan_id, "CarePlan"),
            ("update", "Analysis Completed", "Your recent symptom analysis is ready.", "low", analysis2.analysis_id, "AIAnalysis"),
            ("recommendation", "New Recommendation", "We have a new lifestyle recommendation.", "low", None, "Recommendation"),
            ("update", "Report Uploaded", "Your chest X-ray was uploaded.", "low", visit1.visit_id, "Visit"),
            ("reminder", "Medication Reminder", "Time to take Vitamin D.", "medium", None, "Medication")
        ]
        for t, title, msg, p, r_id, r_type in notifs:
            crud.create_notification(session=session, notification_id=uuid.uuid4(), user_id=u_id, notification_type=t, title=title, message=msg, priority=p, related_record_id=r_id, related_record_type=r_type, is_read=False, delivery_channel="in_app", sent_at=now, created_at=now)

        # 11. Medications
        print("Populating Medications...")
        crud.clinical_crud.create_medication(session=session, medication_id=uuid.uuid4(), user_id=u_id, medication_name="Paracetamol", dosage="500mg", frequency="SOS", duration="3 days", route="Oral", start_date=base_time.date(), purpose="Fever", status="completed", created_at=base_time, updated_at=base_time)
        crud.clinical_crud.create_medication(session=session, medication_id=uuid.uuid4(), user_id=u_id, medication_name="Vitamin D", dosage="60000 IU", frequency="Weekly", duration="4 weeks", route="Oral", start_date=now.date(), purpose="Deficiency", status="active", created_at=now, updated_at=now)
        crud.clinical_crud.create_medication(session=session, medication_id=uuid.uuid4(), user_id=u_id, medication_name="Cetirizine", dosage="10mg", frequency="Daily at night", duration="5 days", route="Oral", start_date=now.date(), purpose="Allergies", status="active", created_at=now, updated_at=now)

        # 12. Family Members
        print("Populating Family...")
        # Create a sibling (since it requires a user ID, we'll make a fake one just for the relationship)
        sibling = crud.get_user_by_email(session, "sibling@carepath.ai")
        if not sibling:
            sibling = crud.create_user(session=session, user_id=uuid.uuid4(), email="sibling@carepath.ai", password_hash="hash", role="patient", account_status="active", created_at=now, updated_at=now)
        sibling_id = sibling.user_id
        crud.create_family_member(session=session, family_id=uuid.uuid4(), primary_user_id=u_id, member_user_id=sibling_id, relationship_type="sibling", access_level="view", status="active", created_at=now, updated_at=now)

        # 13. Feedback
        print("Populating Feedback...")
        crud.create_feedback(session=session, feedback_id=uuid.uuid4(), user_id=u_id, feedback_type="general", rating=5, title="Great App", message="Very helpful for tracking my symptoms.", status="resolved", created_at=now, updated_at=now)

        # 14. Audit History
        print("Populating Audit History...")
        crud.utils.create_record(session, AuditHistory, audit_id=uuid.uuid4(), user_id=u_id, action_type="login", record_type="User", record_id=u_id, ip_address="192.168.1.1", status="success", created_at=now)
        crud.utils.create_record(session, AuditHistory, audit_id=uuid.uuid4(), user_id=u_id, action_type="update", record_type="PatientProfile", record_id=u_id, ip_address="192.168.1.1", status="success", created_at=now)
        crud.utils.create_record(session, AuditHistory, audit_id=uuid.uuid4(), user_id=u_id, action_type="create", record_type="MedicalFile", record_id=visit1.visit_id, ip_address="192.168.1.1", status="success", created_at=now)

        # 15. Prompt Templates
        print("Populating Prompt Templates...")
        existing_prompts = session.query(PromptTemplate).count()
        if existing_prompts == 0:
            crud.utils.create_record(session, PromptTemplate, template_id=uuid.uuid4(), agent_name="Clinical Reasoning", template_version="1.0", template_name="Symptom Check v1", template_content="Analyze symptoms and provide list.", is_active=True, created_at=now, updated_at=now)
            crud.utils.create_record(session, PromptTemplate, template_id=uuid.uuid4(), agent_name="Document Analysis", template_version="1.0", template_name="OCR Parse", template_content="Extract text from document.", is_active=True, created_at=now, updated_at=now)
            
        template = session.query(PromptTemplate).first()
        t_id = template.template_id if template else None

        # 16. Agent Runs
        print("Populating Agent Runs...")
        crud.create_agent_run(session=session, run_id=uuid.uuid4(), user_id=u_id, agent_name="Clinical Reasoning", agent_version="1.0", template_id=t_id, input_data='{"symptoms": "fatigue"}', output_data='{"result": "viral"}', execution_time=1200, token_count=150, cost=0.01, status="success", model_used="gpt-4", created_at=now)
        crud.create_agent_run(session=session, run_id=uuid.uuid4(), user_id=u_id, agent_name="Document Analysis", agent_version="1.0", template_id=t_id, input_data='{"file": "xray.png"}', error_message="Timeout", execution_time=5000, token_count=0, status="failure", model_used="gpt-4-vision", created_at=now)

        # 17. Timeline Events
        print("Populating Timeline Events...")
        crud.create_timeline_event(session=session, event_id=uuid.uuid4(), user_id=u_id, event_type="visit", event_date=visit1.visit_date, event_title="General Consultation", event_description="Visit with Dr. Smith", related_record_id=visit1.visit_id, related_record_type="Visit", visible_to_patient=True, created_at=base_time)
        crud.create_timeline_event(session=session, event_id=uuid.uuid4(), user_id=u_id, event_type="symptom", event_date=sess1.session_date, event_title="Reported Symptoms", event_description="Fatigue, Headache", related_record_id=sess1.session_id, related_record_type="SymptomSession", visible_to_patient=True, created_at=base_time)
        crud.create_timeline_event(session=session, event_id=uuid.uuid4(), user_id=u_id, event_type="analysis", event_date=analysis1.created_at, event_title="AI Analysis", event_description="Viral infection detected", related_record_id=analysis1.analysis_id, related_record_type="AIAnalysis", visible_to_patient=False, created_at=base_time)

        # 18. Evidence Retrieval
        print("Populating Evidence...")
        run = session.query(AgentRun).first()
        run_id = run.run_id if run else None
        crud.create_evidence(session=session, evidence_id=uuid.uuid4(), run_id=run_id, source_type="medical_literature", source_reference="https://pubmed.ncbi.nlm.nih.gov/123456", evidence_text="Fatigue is common in viral infections.", relevance_score=0.92, retrieval_timestamp=now, context_used_in="differential_diagnosis", created_at=now)
        crud.create_evidence(session=session, evidence_id=uuid.uuid4(), run_id=run_id, source_type="guidelines", source_reference="CDC Guidelines", evidence_text="Rest and hydrate.", relevance_score=0.88, retrieval_timestamp=now, context_used_in="recommendation", created_at=now)

        print("\n[PASS] Successfully populated the development database with demo dataset for abhay@gmail.com!")
    except Exception as e:
        print(f"\n[FAIL] Failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    populate()
