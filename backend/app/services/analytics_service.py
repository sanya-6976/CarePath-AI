from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.app.services.memory_service import get_patient_carepath_memory

def get_patient_analytics(session: Session, patient_id: str) -> Dict[str, Any]:
    """
    Computes comprehensive clinical continuity analytics and dashboard statistics:
    - Encounters & Consultations breakdown
    - Care plan completion rates
    - Medication adherence score (%)
    - Follow-up distribution (scheduled vs completed)
    - Symptom severity counts & timeline activity
    """
    memory = get_patient_carepath_memory(session, patient_id)

    # 1. Consultations stats
    consultations = memory.get("consultations", [])
    total_consultations = len(consultations)

    # 2. Care Plan stats
    care_plans = memory.get("care_plans", [])
    total_care_plans = len(care_plans)
    active_care_plans = sum(1 for cp in care_plans if cp.get("status") == "ACTIVE")
    completed_care_plans = sum(1 for cp in care_plans if cp.get("status") == "COMPLETED")
    care_plan_completion_rate = 100.0 if total_care_plans == 0 else round((completed_care_plans / total_care_plans) * 100, 1)

    # 3. Medication Adherence
    medications = memory.get("prescriptions_and_medications", [])
    total_meds = len(medications)
    active_meds = sum(1 for m in medications if m.get("status") == "ACTIVE")
    completed_meds = sum(1 for m in medications if m.get("status") == "COMPLETED")
    med_adherence_rate = 100.0 if total_meds == 0 else round(((active_meds + completed_meds) / total_meds) * 100, 1)

    # 4. Follow-up distribution
    follow_ups = memory.get("follow_ups", [])
    total_followups = len(follow_ups)
    scheduled_followups = sum(1 for f in follow_ups if f.get("status") == "SCHEDULED")
    completed_followups = sum(1 for f in follow_ups if f.get("status") == "COMPLETED")

    # 5. Symptom Severity Breakdown
    symptoms = memory.get("symptoms", [])
    severity_counts = {"HIGH": 0, "MODERATE": 0, "LOW": 0, "NORMAL": 0}
    for s in symptoms:
        sev = (s.get("severity") or "NORMAL").upper()
        if sev in severity_counts:
            severity_counts[sev] += 1
        else:
            severity_counts["MODERATE"] += 1

    # 6. Timeline activity
    timeline_events = memory.get("timeline_events", [])
    total_timeline_milestones = len(timeline_events)

    return {
        "patient_id": patient_id,
        "clinical_summary": {
            "total_consultations": total_consultations,
            "total_reports_uploaded": len(memory.get("reports", [])),
            "total_timeline_milestones": total_timeline_milestones
        },
        "care_plans": {
            "total": total_care_plans,
            "active": active_care_plans,
            "completed": completed_care_plans,
            "completion_rate_percentage": care_plan_completion_rate
        },
        "medications": {
            "total": total_meds,
            "active": active_meds,
            "completed": completed_meds,
            "adherence_rate_percentage": med_adherence_rate
        },
        "follow_ups": {
            "total": total_followups,
            "scheduled": scheduled_followups,
            "completed": completed_followups
        },
        "symptoms": {
            "total_recorded": len(symptoms),
            "severity_distribution": severity_counts
        }
    }
