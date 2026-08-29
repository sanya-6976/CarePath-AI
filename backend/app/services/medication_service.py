from typing import Any, List, Optional, Dict
from sqlalchemy.orm import Session
from database.crud import clinical_crud
from database.models import Medication
try:
    from backend.app.services.timeline_service import auto_log_timeline_event
except ModuleNotFoundError:
    from app.services.timeline_service import auto_log_timeline_event
import uuid
from datetime import datetime, timezone

from database.crud.utils import safe_uuid

def add_medication(session: Session, data: dict) -> Medication:
    now = datetime.now(timezone.utc)
    user_id = data.get("user_id")
    med_id = uuid.uuid4()
    uid = safe_uuid(user_id)
    med_name = data.get("medication_name", "")
    
    med = clinical_crud.create_medication(
        session=session,
        medication_id=med_id,
        user_id=uid,
        medication_name=med_name,
        dosage=data.get("dosage", ""),
        frequency=data.get("frequency", ""),
        duration=data.get("duration", ""),
        route=data.get("route", "oral"),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        purpose=data.get("purpose", ""),
        side_effects=data.get("side_effects", ""),
        instructions=data.get("instructions", ""),
        prescribed_by=data.get("prescribed_by", ""),
        status=data.get("status", "ACTIVE"),
        created_at=now,
        updated_at=now
    )

    # Timeline auto-trigger
    try:
        auto_log_timeline_event(
            session=session,
            user_id=uid,
            event_type="MEDICATION",
            event_title=f"Prescribed Medication: {med_name}",
            event_description=f"Dosage: {data.get('dosage', 'N/A')}, Frequency: {data.get('frequency', 'N/A')}",
            severity="MEDIUM",
            related_record_id=med_id,
            related_record_type="MEDICATION"
        )
    except Exception:
        pass

    return med

def get_patient_medications(session: Session, patient_id: str, status: Optional[str] = None) -> List[Medication]:
    uid = safe_uuid(patient_id)
    if not uid:
        return []
    return clinical_crud.get_user_medications(session=session, user_id=uid, status=status)

def update_medication_status(session: Session, medication_id: str, status: str) -> Optional[Medication]:
    mid = safe_uuid(medication_id)
    if not mid:
        return None
    med = clinical_crud.update_medication_status(session=session, medication_id=mid, status=status)
    if med and status.upper() in ["COMPLETED", "DISCONTINUED"]:
        try:
            auto_log_timeline_event(
                session=session,
                user_id=med.user_id,
                event_type="MEDICATION",
                event_title=f"Medication {status.title()}: {med.medication_name}",
                severity="LOW",
                related_record_id=med.medication_id,
                related_record_type="MEDICATION"
            )
        except Exception:
            pass
    return med

def get_medication_adherence(session: Session, patient_id: str) -> Dict[str, Any]:
    """Calculates overall medication adherence metrics for a patient."""
    meds = get_patient_medications(session, patient_id)
    total_meds = len(meds)
    active_count = sum(1 for m in meds if m.status.upper() == "ACTIVE")
    completed_count = sum(1 for m in meds if m.status.upper() == "COMPLETED")
    discontinued_count = sum(1 for m in meds if m.status.upper() == "DISCONTINUED")

    adherence_percentage = 100.0 if total_meds == 0 else round(((active_count + completed_count) / total_meds) * 100, 1)

    return {
        "patient_id": patient_id,
        "total_medications": total_meds,
        "active_medications": active_count,
        "completed_medications": completed_count,
        "discontinued_medications": discontinued_count,
        "adherence_percentage": adherence_percentage
    }
