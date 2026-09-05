import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import uuid
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.orm import Session
from database.connections import SessionLocal, engine, Base
from database.models import (
    User, PatientProfile, SymptomSession, PatientSymptom, Medication,
    MedicalFile, AIAnalysis, PatientUpdate, TimelineEvent, CarePlan, FollowUp, Recommendation
)

try:
    from app.core.security import get_password_hash
except ImportError:
    from backend.app.core.security import get_password_hash

def seed_user(email: str, plaintext_pw: str, first_name: str, last_name: str):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        print(f"[INFO] User '{email}' already exists with user_id: {existing_user.user_id}. Cleaning old profile records for clean seed...")
        user_id = existing_user.user_id
        
        # Clean existing records for this user
        db.query(TimelineEvent).filter(TimelineEvent.user_id == user_id).delete()
        db.query(PatientUpdate).filter(PatientUpdate.user_id == user_id).delete()
        db.query(FollowUp).filter(FollowUp.user_id == user_id).delete()
        db.query(CarePlan).filter(CarePlan.user_id == user_id).delete()
        db.query(Recommendation).filter(Recommendation.user_id == user_id).delete()
        db.query(AIAnalysis).filter(AIAnalysis.user_id == user_id).delete()
        db.query(MedicalFile).filter(MedicalFile.user_id == user_id).delete()
        db.query(Medication).filter(Medication.user_id == user_id).delete()
        db.query(PatientSymptom).filter(PatientSymptom.user_id == user_id).delete()
        db.query(SymptomSession).filter(SymptomSession.user_id == user_id).delete()
        db.query(PatientProfile).filter(PatientProfile.user_id == user_id).delete()
        db.query(User).filter(User.user_id == user_id).delete()
        db.commit()

    # 1. Create User
    now = datetime.now(timezone.utc)
    user_id = uuid.uuid4()
    hashed_pw = get_password_hash(plaintext_pw)

    user = User(
        user_id=user_id,
        email=email,
        password_hash=hashed_pw,
        role="patient",
        account_status="active",
        created_at=now - timedelta(days=30),
        updated_at=now,
        last_login=now
    )
    db.add(user)
    db.commit()

    print(f"[OK] Created User: {email} (ID: {user_id})")

    # 2. Patient Profile
    profile = PatientProfile(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date(1990, 4, 12),
        gender="Male",
        height=178.0,
        weight=76.0,
        blood_group="A+",
        emergency_contact="+91-9876543210",
        medical_summary=(
            "Patient diagnosed with Moderate Persistent Bronchial Asthma and Seasonal Allergic Rhinitis. "
            "Exhibits exercise-induced dyspnea, intermittent nocturnal coughing, and seasonal nasal congestion. "
            "Currently maintained on Fluticasone/Salmeterol combination inhaler, rescue Albuterol, and Montelukast."
        ),
        created_at=now - timedelta(days=30),
        updated_at=now
    )
    db.add(profile)
    db.commit()
    print(f"[OK] Created PatientProfile for {first_name} {last_name}.")

    # 3. Patient Updates
    updates_data = [
        (now - timedelta(days=30), "symptom", "Initial medical assessment: Diagnosed with Moderate Persistent Asthma following recurrent wheezing and shortness of breath during cold weather."),
        (now - timedelta(days=14), "medication", "Started daily Fluticasone/Salmeterol 250/50 mcg DPI inhaler (1 puff twice daily) and Montelukast 10 mg at bedtime."),
        (now - timedelta(days=3), "symptom", "Reported increased morning chest tightness and persistent dry cough after light outdoor exercise in cold air.")
    ]
    for u_date, u_type, u_content in updates_data:
        up = PatientUpdate(
            update_id=uuid.uuid4(),
            user_id=user_id,
            update_type=u_type,
            content=u_content,
            created_at=u_date
        )
        db.add(up)
    db.commit()
    print("[OK] Seeded 3 PatientUpdate entries.")

    # 4. Symptom Session & Patient Symptoms
    session_id = uuid.uuid4()
    s_session = SymptomSession(
        session_id=session_id,
        user_id=user_id,
        session_date=now - timedelta(days=3),
        session_type="initial",
        status="completed",
        created_at=now - timedelta(days=3),
        updated_at=now
    )
    db.add(s_session)

    symptoms_data = [
        ("Shortness of Breath (Dyspnea)", "Breathing tightness triggered by cold weather and light exercise.", "moderate", "3 days", "Chest/Airways"),
        ("Wheezing & Dry Cough", "High-pitched wheezing sound during exhalation and nocturnal dry cough.", "moderate", "2 weeks", "Bronchial airways"),
        ("Nasal Congestion & Sneezing", "Seasonal allergic rhinitis symptoms with clear nasal discharge.", "mild", "1 month", "Nasal passages")
    ]
    for sym_name, sym_desc, sym_sev, sym_dur, sym_loc in symptoms_data:
        sym = PatientSymptom(
            symptom_id=uuid.uuid4(),
            session_id=session_id,
            user_id=user_id,
            symptom_name=sym_name,
            symptom_description=sym_desc,
            onset_date=(now - timedelta(days=14)).date(),
            severity=sym_sev,
            duration=sym_dur,
            location=sym_loc,
            created_at=now - timedelta(days=3),
            updated_at=now
        )
        db.add(sym)
    db.commit()
    print("[OK] Seeded SymptomSession and 3 PatientSymptoms.")

    # 5. Medical Files
    files_data = [
        (
            "01_spirometry_pft_report.pdf",
            "Lab Report",
            "Spirometry Pulmonary Function Test Report: FEV1 = 2.40 L (71% of predicted value), FEV1/FVC = 0.72. Significant bronchodilator reversibility (+14% increase in FEV1 post-albuterol). Interpretation: Reversible moderate obstructive airway defect consistent with bronchial asthma.",
            now - timedelta(days=28)
        ),
        (
            "02_asthma_prescription.pdf",
            "Prescription",
            "Clinical Prescription Script: 1. Fluticasone/Salmeterol 250/50 mcg DPI inhaler - 1 puff twice daily (morning & night). 2. Albuterol Sulfate 90 mcg Inhaler - 2 puffs as needed for acute shortness of breath. 3. Montelukast 10 mg Oral Tablet - 1 tablet daily at bedtime.",
            now - timedelta(days=14)
        ),
        (
            "03_chest_xray_report.pdf",
            "Medical Report",
            "Chest Radiograph PA View: Lung fields demonstrate hyperinflation consistent with chronic airway disease. No focal lung consolidation, infiltrates, pleural effusion, or pneumothorax observed. Cardiac size within normal limits.",
            now - timedelta(days=7)
        )
    ]

    for f_name, f_type, f_ocr, f_date in files_data:
        f_id = uuid.uuid4()
        mf = MedicalFile(
            file_id=f_id,
            user_id=user_id,
            file_name=f_name,
            storage_path=f"uploads/{user_id}/{f_id}_{f_name}",
            file_type=f_type,
            mime_type="application/pdf",
            file_size=245000,
            upload_date=f_date,
            analysis_status="completed",
            ocr_text=f_ocr,
            created_at=f_date,
            updated_at=now
        )
        db.add(mf)
    db.commit()
    print("[OK] Seeded 3 MedicalFiles.")

    # 6. Active Medications
    meds_data = [
        (
            "Fluticasone / Salmeterol Inhaler",
            "250/50 mcg (1 Puff)",
            "Twice daily (Morning & Evening)",
            "Ongoing",
            "Inhalation",
            (now - timedelta(days=14)).date(),
            "Prevents asthma attacks and reduces airway inflammation over time.",
            "Inhale 1 puff twice daily. Always rinse your mouth with water after use."
        ),
        (
            "Albuterol Sulfate Rescue Inhaler",
            "90 mcg (2 Puffs)",
            "Every 4-6 hours as needed",
            "As Needed",
            "Inhalation",
            (now - timedelta(days=30)).date(),
            "Relieves wheezing, chest tightness, and shortness of breath by opening up your airways.",
            "Inhale 2 puffs using your inhaler whenever sudden breathing symptoms start."
        ),
        (
            "Montelukast Oral Tablet",
            "10 mg (1 Tablet)",
            "Once daily at bedtime",
            "Ongoing",
            "Oral",
            (now - timedelta(days=14)).date(),
            "Helps control allergy triggers and prevents nighttime asthma symptoms and allergic rhinitis.",
            "Swallow 1 tablet every evening at bedtime with a glass of water."
        )
    ]

    for m_name, m_dose, m_freq, m_dur, m_route, m_start, m_purpose, m_inst in meds_data:
        med = Medication(
            medication_id=uuid.uuid4(),
            user_id=user_id,
            medication_name=m_name,
            dosage=m_dose,
            frequency=m_freq,
            duration=m_dur,
            route=m_route,
            start_date=m_start,
            purpose=m_purpose,
            instructions=m_inst,
            prescribed_by="Dr. S. Sharma (Pulmonologist)",
            status="active",
            created_at=now - timedelta(days=14),
            updated_at=now
        )
        db.add(med)
    db.commit()
    print("[OK] Seeded 3 Active Medications.")

    # 7. AI Analysis & Specialist Recommendation
    analysis_id = uuid.uuid4()
    analysis = AIAnalysis(
        analysis_id=analysis_id,
        user_id=user_id,
        session_id=session_id,
        analysis_type="differential_diagnosis",
        findings="FEV1 71% with 14% bronchodilator reversibility confirms Moderate Persistent Bronchial Asthma with exercise-induced wheezing.",
        differential_list="1. Moderate Persistent Bronchial Asthma\n2. Exercise-Induced Bronchospasm\n3. Seasonal Allergic Rhinitis",
        confidence_score=0.92,
        risk_level="medium",
        summary="CarePath recommends Pulmonology evaluation for asthma action plan optimization and inhaler technique review.",
        changed_factors='["Increased morning chest tightness post-exercise", "Rescue inhaler use increased to 3 times weekly"]',
        new_information='["Spirometry PFT report showing 14% FEV1 reversibility uploaded"]',
        created_at=now - timedelta(days=1),
        updated_at=now
    )
    db.add(analysis)
    db.commit()

    rec = Recommendation(
        recommendation_id=uuid.uuid4(),
        analysis_id=analysis_id,
        user_id=user_id,
        recommendation_type="specialist",
        specialist_type="Pulmonology",
        title="Pulmonology Asthma Review Recommended",
        description="Persistent exercise-induced shortness of breath and spirometry FEV1 reversibility warrant specialist care plan tuning.",
        confidence=0.92,
        urgency="routine",
        rationale="PFT spirometry confirms reversible bronchial obstruction (FEV1 71%). Pulmonologist consultation supports optimal asthma control.",
        estimated_timeline="Within 2-3 weeks",
        status="pending",
        created_at=now - timedelta(days=1),
        updated_at=now
    )
    db.add(rec)
    db.commit()
    print("[OK] Seeded AIAnalysis & Pulmonology Recommendation.")

    # 8. Care Plan & Follow Up
    plan_id = uuid.uuid4()
    cp = CarePlan(
        plan_id=plan_id,
        user_id=user_id,
        analysis_id=analysis_id,
        plan_name="Asthma Management & Airway Control Plan",
        plan_description="Comprehensive asthma maintenance plan emphasizing daily inhaler adherence, peak flow tracking, and allergen avoidance.",
        status="active",
        next_steps="1. Schedule Pulmonology consultation.\n2. Monitor daily morning peak expiratory flow (PEF).\n3. Rinse mouth after steroid inhaler use.",
        appointment_prep="Bring your spirometry report and medication log to your pulmonology appointment.",
        lifestyle_changes="Avoid cold air exposure during intense outdoor exercises. Use air purifier in bedroom.",
        monitoring_points="Track peak flow daily. Log rescue inhaler usage if needed > 2 times per week.",
        estimated_duration="3 Months",
        priority="medium",
        created_at=now - timedelta(days=1),
        updated_at=now
    )
    db.add(cp)

    fu = FollowUp(
        followup_id=uuid.uuid4(),
        user_id=user_id,
        plan_id=plan_id,
        followup_type="review",
        scheduled_date=now + timedelta(days=7),
        description="Follow-up Pulmonology Consultation & Asthma Action Plan Review",
        purpose="Evaluate response to combination inhaler therapy and review peak flow monitoring.",
        status="scheduled",
        created_at=now,
        updated_at=now
    )
    db.add(fu)
    db.commit()
    print("[OK] Seeded CarePlan & FollowUp.")

    # 9. Timeline Events
    events_data = [
        (now - timedelta(days=30), "symptom", "Initial Asthma Symptoms Reported", "Reported shortness of breath and wheezing after cold weather exposure.", "mild"),
        (now - timedelta(days=28), "visit", "Pulmonary Function Test (Spirometry) Completed", "Spirometry demonstrated FEV1 of 71% predicted with +14% bronchodilator reversibility.", "mild"),
        (now - timedelta(days=14), "medication", "Prescription Started: Combination Inhaler Regimen", "Started daily Fluticasone/Salmeterol 250/50 mcg and Montelukast 10 mg bedtime tablet.", "mild"),
        (now - timedelta(days=3), "symptom", "Reported Exercise-Induced Morning Chest Tightness", "Logged morning chest tightness following outdoor exercise in cold temperature.", "moderate"),
        (now - timedelta(days=1), "analysis", "CarePath Multi-Agent Analysis Completed", "Synthesized PFT report, symptoms, and prescription records. Recommended Pulmonology review.", "mild")
    ]

    for ev_date, ev_type, ev_title, ev_desc, ev_sev in events_data:
        te = TimelineEvent(
            event_id=uuid.uuid4(),
            user_id=user_id,
            event_type=ev_type,
            event_date=ev_date,
            event_title=ev_title,
            event_description=ev_desc,
            severity=ev_sev,
            visible_to_patient=True,
            created_at=ev_date
        )
        db.add(te)
    db.commit()
    print("[OK] Seeded 5 TimelineEvents.")

    print("\n=======================================================")
    print(f"SUCCESS: User profile successfully created!")
    print(f"Email: {email}")
    print(f"Password: {plaintext_pw}")
    print(f"User ID: {user_id}")
    print("=======================================================\n")

    db.close()

if __name__ == "__main__":
    seed_user("test@gmail.com", "test123", "Test", "User")
    seed_user("arun@gmail.com", "dtu123", "Arun", "Kumar")
