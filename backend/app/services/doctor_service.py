from typing import Any, List, Optional
from sqlalchemy.orm import Session
from database.crud import clinical_crud, ai_crud, system_crud
from database.models import Visit, Feedback, Recommendation
import uuid
from datetime import datetime, timezone

from database.crud.utils import safe_uuid

def create_consultation(session: Session, data: dict) -> Visit:
    now = datetime.now(timezone.utc)
    user_id = data.get("user_id")
    
    return clinical_crud.create_visit(
        session=session,
        visit_id=uuid.uuid4(),
        user_id=safe_uuid(user_id),
        visit_type=data.get("visit_type", "CONSULTATION"),
        provider_name=data.get("provider_name", "Attending Physician"),
        facility_name=data.get("facility_name", "CarePath Clinical Center"),
        visit_date=data.get("visit_date") or now,
        duration=data.get("duration", 30),
        visit_reason=data.get("visit_reason", ""),
        notes=data.get("notes", ""),
        outcome=data.get("outcome", ""),
        status=data.get("status", "COMPLETED"),
        created_at=now,
        updated_at=now
    )

def get_patient_consultations(session: Session, patient_id: str) -> List[Visit]:
    uid = safe_uuid(patient_id)
    if not uid:
        return []
    from sqlalchemy import select
    return list(session.scalars(select(Visit).where(Visit.user_id == uid).order_by(Visit.visit_date.desc())).all())

def add_doctor_feedback(session: Session, data: dict) -> Feedback:
    now = datetime.now(timezone.utc)
    user_id = data.get("user_id")
    related_record_id = data.get("related_record_id")
    
    return system_crud.create_feedback(
        session=session,
        feedback_id=uuid.uuid4(),
        user_id=safe_uuid(user_id),
        feedback_type=data.get("feedback_type", "DOCTOR_REVIEW"),
        rating=data.get("rating", 5),
        title=data.get("title", "Clinical Review Note"),
        message=data.get("message", ""),
        related_record_id=safe_uuid(related_record_id),
        related_record_type=data.get("related_record_type", "CARE_PLAN"),
        status=data.get("status", "APPROVED"),
        response=data.get("response", ""),
        created_at=now,
        updated_at=now
    )

def get_doctor_recommendations(session: Session, patient_id: str) -> List[Recommendation]:
    uid = safe_uuid(patient_id)
    if not uid:
        return []
    return ai_crud.get_user_recommendations(session, uid)
