import os
import sys
import uuid
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connections import SessionLocal
from database import crud
from database.models import (
    User, PatientProfile, Visit, MedicalFile, SymptomSession,
    PatientSymptom, AIAnalysis, Recommendation, CarePlan,
    Medication, FollowUp, Notification, TimelineEvent
)

def populate_aryan_demo():
    session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        base_time = now - timedelta(days=14)

        email = "aryansnair@gmail.com"
        print(f"--- Seeding CarePath AI Demo Data for User: {email} ---")

        # 1. User
        user = crud.get_user_by_email(session, email)
        if not user:
            print(f"Creating user record for {email}...")
            user = crud.create_user(
                session=session,
                user_id=uuid.uuid4(),
                email=email,
                password_hash="$2b$12$eImiTXuWVxfM37uY4JANjO5E/0N1rV.kS7d02n92s011xK8J2...",
                role="patient",
                account_status="active",
                created_at=base_time,
                updated_at=now
            )
        u_id = user.user_id
        print(f"User ID: {u_id}")

        # 2. Patient Profile
        print("1. Updating Patient Profile (Aryan Nair)...")
        profile = crud.get_patient_profile(session, u_id)
        if profile:
            profile.first_name = "Aryan"
            profile.last_name = "Nair"
            profile.date_of_birth = datetime(1994, 8, 12, tzinfo=timezone.utc).date()
            profile.gender = "Male"
            profile.height = 178.0
            profile.weight = 74.0
            profile.blood_group = "O+"
            profile.emergency_contact = "+1 (555) 234-5678"
            profile.medical_summary = (
                "32-year-old male with mild exertional bronchospasm and seasonal environmental allergies. "
                "Managed with Albuterol rescue inhaler and daily Fluticasone. Compliant with clinical care plan."
            )
            profile.updated_at = now
            session.commit()
        else:
            crud.create_patient_profile(
                session=session,
                user_id=u_id,
                first_name="Aryan",
                last_name="Nair",
                date_of_birth=datetime(1994, 8, 12, tzinfo=timezone.utc).date(),
                gender="Male",
                height=178.0,
                weight=74.0,
                blood_group="O+",
                emergency_contact="+1 (555) 234-5678",
                medical_summary=(
                    "32-year-old male with mild exertional bronchospasm and seasonal environmental allergies. "
                    "Managed with Albuterol rescue inhaler and daily Fluticasone. Compliant with clinical care plan."
                ),
                created_at=base_time,
                updated_at=now
            )

        # 3. Clinical Visits
        print("2. Populating Clinical Visits...")
        visit1 = crud.create_visit(
            session=session,
            visit_id=uuid.uuid4(),
            user_id=u_id,
            visit_type="consultation",
            provider_name="Dr. Robert Chen, MD",
            facility_name="CarePath Primary Health Center",
            visit_date=base_time + timedelta(days=2),
            duration=30,
            visit_reason="Evaluation of nocturnal dry cough and mild dyspnea upon exercise.",
            notes="Chest auscultation reveals mild end-expiratory wheeze. Ordered Pulmonary Function Test and Chest Radiogram.",
            outcome="Prescribed short-acting bronchodilator. Referred to Pulmonology.",
            status="completed",
            created_at=base_time + timedelta(days=2),
            updated_at=base_time + timedelta(days=2)
        )

        visit2 = crud.create_visit(
            session=session,
            visit_id=uuid.uuid4(),
            user_id=u_id,
            visit_type="appointment",
            provider_name="Dr. Sarah Jenkins, MD (Pulmonology)",
            facility_name="Metro Pulmonary & Allergy Institute",
            visit_date=now - timedelta(days=3),
            duration=45,
            visit_reason="Pulmonology Consultation & Spirometry Review",
            notes="FEV1/FVC ratio: 78%. Reversible airway obstruction demonstrated post-bronchodilator (+14% FEV1 improvement).",
            outcome="Initiated maintenance inhaled corticosteroid (Fluticasone) and peak flow self-monitoring.",
            next_appointment=now + timedelta(days=14),
            status="completed",
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(days=3)
        )

        # 4. Medical Files
        print("3. Populating Medical Files & Diagnostics...")
        crud.create_medical_file(
            session=session,
            file_id=uuid.uuid4(),
            user_id=u_id,
            visit_id=visit1.visit_id,
            file_name="Chest_XRay_PA_Lateral_Report.pdf",
            storage_path=f"medical_files/{u_id}/Chest_XRay_Report.pdf",
            file_type="application/pdf",
            mime_type="application/pdf",
            file_size=1850000,
            upload_date=base_time + timedelta(days=3),
            analysis_status="completed",
            created_at=base_time + timedelta(days=3),
            updated_at=base_time + timedelta(days=3)
        )
        crud.create_medical_file(
            session=session,
            file_id=uuid.uuid4(),
            user_id=u_id,
            visit_id=visit2.visit_id,
            file_name="Spirometry_Pulmonary_Function_Test.pdf",
            storage_path=f"medical_files/{u_id}/Spirometry_PFT.pdf",
            file_type="application/pdf",
            mime_type="application/pdf",
            file_size=2400000,
            upload_date=now - timedelta(days=2),
            analysis_status="completed",
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(days=2)
        )
        crud.create_medical_file(
            session=session,
            file_id=uuid.uuid4(),
            user_id=u_id,
            visit_id=visit2.visit_id,
            file_name="Allergy_IgE_Blood_Panel.pdf",
            storage_path=f"medical_files/{u_id}/Allergy_Panel.pdf",
            file_type="application/pdf",
            mime_type="application/pdf",
            file_size=1100000,
            upload_date=now - timedelta(days=1),
            analysis_status="completed",
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(days=1)
        )

        # 5. Symptom Sessions & Symptoms
        print("4. Populating Symptom Tracking Data...")
        sess1 = crud.create_session(
            session=session,
            session_id=uuid.uuid4(),
            user_id=u_id,
            session_date=base_time + timedelta(days=1),
            session_type="initial",
            status="completed",
            created_at=base_time + timedelta(days=1),
            updated_at=base_time + timedelta(days=1)
        )
        sess2 = crud.create_session(
            session=session,
            session_id=uuid.uuid4(),
            user_id=u_id,
            session_date=now - timedelta(days=2),
            session_type="reassessment",
            status="completed",
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(days=2)
        )

        symptoms = [
            (sess1.session_id, "Exertional Dyspnea", "Shortness of breath after climbing stairs or jogging", "moderate", "10 days", "Chest/Airway"),
            (sess1.session_id, "Dry Nocturnal Cough", "Tickling cough worse at night", "mild", "1 week", "Throat/Chest"),
            (sess2.session_id, "Chest Tightness", "Mild sensation of constriction in chest area", "mild", "3 days", "Chest"),
            (sess2.session_id, "Wheezing", "High-pitched whistle sound on forced expiration", "mild", "2 days", "Airway")
        ]
        for sid, name, desc, sev, dur, loc in symptoms:
            crud.create_symptom(
                session=session,
                symptom_id=uuid.uuid4(),
                session_id=sid,
                user_id=u_id,
                symptom_name=name,
                symptom_description=desc,
                onset_date=base_time.date(),
                severity=sev,
                duration=dur,
                location=loc,
                created_at=now,
                updated_at=now
            )

        # 6. AI Analysis
        print("5. Populating Multi-Agent AI Analyses...")
        analysis1 = crud.create_analysis(
            session=session,
            analysis_id=uuid.uuid4(),
            user_id=u_id,
            session_id=sess1.session_id,
            analysis_type="differential_diagnosis",
            findings="Spirometry report indicates reversible lower airway obstruction (+14% post-BD FEV1). Visual chest radiogram clear of focal consolidations.",
            differential_list="1. Cough-Variant Asthma (92% probability), 2. Environmental Allergy Induced Bronchospasm (85%), 3. Post-Viral Hyperreactivity (40%)",
            confidence_score=0.94,
            risk_level="low",
            summary="Clinical history, spirometry curve, and symptom presentation strongly align with mild persistent asthma triggered by environmental allergens.",
            evidence_sources="Spirometry PFT, Chest Radiogram, Allergy IgE Panel, CarePath 11-Agent Reasoning Pipeline",
            ai_model_version="CarePath 2.0 Multi-Agent Graph",
            execution_time=115,
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(days=2)
        )

        # 7. Recommendations
        print("6. Populating Clinical Recommendations...")
        crud.create_recommendation(
            session=session,
            recommendation_id=uuid.uuid4(),
            analysis_id=analysis1.analysis_id,
            user_id=u_id,
            recommendation_type="lifestyle",
            specialist_type="Pulmonologist",
            title="Pulmonology Consultation & Allergy Management",
            description="Consult Dr. Sarah Jenkins for maintenance asthma controller optimization and environmental allergen immunotherapy.",
            confidence=0.95,
            urgency="routine",
            status="completed",
            rationale="Post-bronchodilator reversibility confirmed on PFT.",
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(days=2)
        )
        crud.create_recommendation(
            session=session,
            recommendation_id=uuid.uuid4(),
            analysis_id=analysis1.analysis_id,
            user_id=u_id,
            recommendation_type="lifestyle",
            title="Daily Peak Flow Monitoring & Hydration",
            description="Record morning and evening Peak Expiratory Flow Rate (PEFR). Maintain hydration >2.5L daily to keep mucous thin.",
            confidence=0.92,
            urgency="routine",
            status="pending",
            rationale="Early detection of airway narrowing before symptoms manifest.",
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(days=1)
        )

        # 8. Care Plan
        print("7. Populating Longitudinal Care Plan...")
        plan1 = crud.create_care_plan(
            session=session,
            plan_id=uuid.uuid4(),
            user_id=u_id,
            analysis_id=analysis1.analysis_id,
            plan_name="14-Day Airway & Asthma Action Plan",
            plan_description="Structured management plan focusing on daily anti-inflammatory controller adherence, peak-flow tracking, and allergen avoidance.",
            status="active",
            next_steps="Review peak-flow log at 2-week pulmonology follow-up.",
            appointment_prep="Bring symptom diary and PEFR log to clinic.",
            lifestyle_changes="HEPA air filter in bedroom, avoid dust exposure, warm up thoroughly before exercise.",
            monitoring_points="Daily FEV1/PEFR, nocturnal cough frequency, rescue inhaler usage count.",
            estimated_duration="14 days",
            priority="medium",
            created_at=now - timedelta(days=2),
            updated_at=now
        )

        # 9. Medications
        print("8. Populating Medications...")
        meds = [
            ("Albuterol Sulfate HFA Inhaler", "90 mcg/actuation", "2 puffs every 4-6 hours as needed", "As Needed", "Inhalation", "Acute relief of bronchospasm", "Mild tremor, transient elevated heart rate", "Rinse mouth after use.", "Dr. Robert Chen", "active"),
            ("Fluticasone Furoate Inhaler", "100 mcg", "1 puff daily in the morning", "Daily", "Inhalation", "Preventative anti-inflammatory airway control", "Hoarseness, dry throat", "Use consistently every morning.", "Dr. Sarah Jenkins", "active"),
            ("Montelukast Sodium", "10 mg", "1 tablet daily at bedtime", "Daily", "Oral", "Leukotriene receptor antagonist for allergic asthma", "Mild headache", "Take in the evening.", "Dr. Sarah Jenkins", "active")
        ]
        for name, dos, freq, dur, rte, pur, side, inst, dr, st in meds:
            crud.clinical_crud.create_medication(
                session=session,
                medication_id=uuid.uuid4(),
                user_id=u_id,
                medication_name=name,
                dosage=dos,
                frequency=freq,
                duration=dur,
                route=rte,
                start_date=(now - timedelta(days=10)).date(),
                end_date=(now + timedelta(days=80)).date(),
                purpose=pur,
                side_effects=side,
                instructions=inst,
                prescribed_by=dr,
                status=st,
                created_at=now - timedelta(days=10),
                updated_at=now
            )

        # 10. Follow-ups & Appointments
        print("9. Populating Scheduled Follow-ups...")
        crud.create_followup(
            session=session,
            followup_id=uuid.uuid4(),
            user_id=u_id,
            plan_id=plan1.plan_id,
            followup_type="checkpoint",
            scheduled_date=now + timedelta(days=11),
            description="14-Day Pulmonology Follow-Up with Dr. Sarah Jenkins",
            purpose="Evaluate Fluticasone controller efficacy & PEFR logs.",
            status="pending",
            notes="Bring PEFR diary to clinic.",
            created_at=now - timedelta(days=1),
            updated_at=now
        )
        crud.create_followup(
            session=session,
            followup_id=uuid.uuid4(),
            user_id=u_id,
            plan_id=plan1.plan_id,
            followup_type="review",
            scheduled_date=now + timedelta(days=3),
            description="Symptom & PEFR Check-in",
            purpose="Log morning peak expiratory flow rate and nocturnal symptom score.",
            status="pending",
            created_at=now,
            updated_at=now
        )

        # 11. Timeline Events
        print("10. Populating Chronological Timeline Events...")
        timeline_events = [
            ("visit", base_time + timedelta(days=2), "Primary Consultation with Dr. Robert Chen", "Evaluated for nocturnal cough and exertional dyspnea."),
            ("symptom", base_time + timedelta(days=3), "Chest Radiogram Report Uploaded", "Chest X-Ray PA & Lateral clear of acute pulmonary consolidation."),
            ("visit", now - timedelta(days=3), "Pulmonology Consultation with Dr. Sarah Jenkins", "Spirometry evaluation confirmed post-bronchodilator reversibility."),
            ("analysis", now - timedelta(days=2), "CarePath AI Multi-Agent Analysis Completed", "Differential diagnosis: Mild Persistent Bronchial Asthma (92% confidence)."),
            ("analysis", now - timedelta(days=2), "14-Day Airway Action Plan Created", "Initiated daily Fluticasone controller and PEFR tracking."),
            ("symptom", now - timedelta(days=2), "Fluticasone & Albuterol Prescriptions Added", "Active medication routine established with pharmacy refill sync.")
        ]
        for etype, edate, etitle, edesc in timeline_events:
            crud.create_timeline_event(
                session=session,
                event_id=uuid.uuid4(),
                user_id=u_id,
                event_type=etype,
                event_date=edate,
                event_title=etitle,
                event_description=edesc,
                severity="mild",
                related_record_id=analysis1.analysis_id,
                related_record_type="AI_ANALYSIS",
                visible_to_patient=True,
                created_at=edate
            )

        print("\nSUCCESS: All CarePath AI demo data populated successfully for Aryan Nair (aryansnair@gmail.com)!")

    except Exception as e:
        session.rollback()
        print(f"ERROR populating demo data: {e}")
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    populate_aryan_demo()
