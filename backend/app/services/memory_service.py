from typing import Dict, Any
from sqlalchemy.orm import Session
from database.crud import user_crud, clinical_crud, ai_crud, system_crud
from database.models import User, PatientProfile
import uuid

from database.crud.utils import safe_uuid

def get_patient_carepath_memory(session: Session, patient_id: str) -> Dict[str, Any]:
    """
    Aggregates the complete CarePath Memory for a patient into a unified, structured history graph.
    
    Structure:
    Patient
     ├── Profile (Demographics, blood group, emergency contact)
     ├── Symptoms (Patient symptoms)
     ├── Consultations (Visits)
     ├── Reports & Documents (MedicalFiles)
     ├── Prescriptions & Medications (Medication)
     ├── Referrals (Recommendations)
     ├── Care Plans (CarePlan)
     ├── Timeline Events (TimelineEvent)
     ├── Follow-ups (FollowUp)
     └── Doctor Feedback (Feedback)
    """
    uid = safe_uuid(patient_id)
    
    user = user_crud.get_user(session, uid) if uid else None
    profile = user_crud.get_patient_profile(session, uid) if uid else None
    
    # 1. Profile metadata
    profile_data = {
        "user_id": str(uid),
        "email": user.email if user else None,
        "first_name": profile.first_name if profile else None,
        "last_name": profile.last_name if profile else None,
        "date_of_birth": profile.date_of_birth.isoformat() if profile and profile.date_of_birth else None,
        "gender": profile.gender if profile else None,
        "blood_group": profile.blood_group if profile else None,
        "emergency_contact": profile.emergency_contact if profile else None,
        "medical_summary": profile.medical_summary if profile else None,
    }

    # 2. Consultations / Visits
    visits = user.visits if user else []
    consultations_data = [
        {
            "visit_id": str(v.visit_id),
            "visit_type": v.visit_type,
            "provider_name": v.provider_name,
            "facility_name": v.facility_name,
            "visit_date": v.visit_date.isoformat() if v.visit_date else None,
            "visit_reason": v.visit_reason,
            "notes": v.notes,
            "outcome": v.outcome,
            "status": v.status
        }
        for v in visits
    ]

    # 3. Symptoms
    symptoms = user.patient_symptoms if user else []
    symptoms_data = [
        {
            "symptom_id": str(s.symptom_id),
            "symptom_name": s.symptom_name,
            "symptom_description": s.symptom_description,
            "onset_date": s.onset_date.isoformat() if s.onset_date else None,
            "severity": s.severity,
            "duration": s.duration,
            "location": s.location
        }
        for s in symptoms
    ]

    # 4. Reports & Medical Files
    medical_files = clinical_crud.get_user_medical_files(session, uid)
    reports_data = [
        {
            "file_id": str(f.file_id),
            "file_name": f.file_name,
            "file_type": f.file_type,
            "storage_path": f.storage_path,
            "upload_date": f.upload_date.isoformat() if f.upload_date else None,
            "ocr_text": f.ocr_text,
            "analysis_status": f.analysis_status
        }
        for f in medical_files
    ]

    # 5. Prescriptions & Medications
    medications = clinical_crud.get_user_medications(session, uid)
    medications_data = [
        {
            "medication_id": str(m.medication_id),
            "medication_name": m.medication_name,
            "dosage": m.dosage,
            "frequency": m.frequency,
            "route": m.route,
            "start_date": m.start_date.isoformat() if m.start_date else None,
            "end_date": m.end_date.isoformat() if m.end_date else None,
            "prescribed_by": m.prescribed_by,
            "purpose": m.purpose,
            "status": m.status
        }
        for m in medications
    ]

    # 6. Referrals & AI Recommendations
    recommendations = ai_crud.get_user_recommendations(session, uid)
    referrals_data = [
        {
            "recommendation_id": str(r.recommendation_id),
            "recommendation_type": r.recommendation_type,
            "specialist_type": r.specialist_type,
            "title": r.title,
            "description": r.description,
            "urgency": r.urgency,
            "status": r.status
        }
        for r in recommendations
    ]

    # 7. Care Plans
    care_plans = ai_crud.get_user_care_plans(session, uid)
    care_plans_data = [
        {
            "plan_id": str(cp.plan_id),
            "plan_name": cp.plan_name,
            "plan_description": cp.plan_description,
            "next_steps": cp.next_steps,
            "priority": cp.priority,
            "status": cp.status,
            "completed_at": cp.completed_at.isoformat() if cp.completed_at else None
        }
        for cp in care_plans
    ]

    # 8. Timeline Events
    timeline_events = system_crud.get_user_timeline_events(session, uid, limit=100)
    timeline_data = [
        {
            "event_id": str(te.event_id),
            "event_type": te.event_type,
            "event_title": te.event_title,
            "event_description": te.event_description,
            "severity": te.severity,
            "event_date": te.event_date.isoformat() if te.event_date else None
        }
        for te in timeline_events
    ]

    # 9. Follow-ups
    follow_ups = ai_crud.get_user_followups(session, uid)
    followups_data = [
        {
            "followup_id": str(fo.followup_id),
            "followup_type": fo.followup_type,
            "scheduled_date": fo.scheduled_date.isoformat() if fo.scheduled_date else None,
            "description": fo.description,
            "status": fo.status,
            "notes": fo.notes
        }
        for fo in follow_ups
    ]

    # 10. Doctor Feedback
    feedback_entries = system_crud.get_user_feedback(session, uid)
    feedback_data = [
        {
            "feedback_id": str(fb.feedback_id),
            "feedback_type": fb.feedback_type,
            "title": fb.title,
            "message": fb.message,
            "rating": fb.rating,
            "response": fb.response,
            "status": fb.status
        }
        for fb in feedback_entries
    ]

    return {
        "patient_profile": profile_data,
        "consultations": consultations_data,
        "symptoms": symptoms_data,
        "reports": reports_data,
        "prescriptions_and_medications": medications_data,
        "referrals": referrals_data,
        "care_plans": care_plans_data,
        "timeline_events": timeline_data,
        "follow_ups": followups_data,
        "doctor_feedback": feedback_data
    }
