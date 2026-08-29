from typing import Any, List, Optional
from sqlalchemy.orm import Session
from database.crud import ai_crud
from database.models import CarePlan
import uuid
from datetime import datetime, timezone

from database.crud.utils import safe_uuid

def create_care_plan(session: Session, data: dict) -> CarePlan:
    now = datetime.now(timezone.utc)
    user_id = data.get("user_id")
    analysis_id = data.get("analysis_id")
    
    return ai_crud.create_care_plan(
        session=session,
        plan_id=uuid.uuid4(),
        user_id=safe_uuid(user_id),
        analysis_id=safe_uuid(analysis_id),
        plan_name=data.get("plan_name", "Personalized Care Plan"),
        plan_description=data.get("plan_description", ""),
        status=data.get("status", "ACTIVE"),
        next_steps=data.get("next_steps", ""),
        appointment_prep=data.get("appointment_prep", ""),
        lifestyle_changes=data.get("lifestyle_changes", ""),
        monitoring_points=data.get("monitoring_points", ""),
        estimated_duration=data.get("estimated_duration", ""),
        priority=data.get("priority", "MEDIUM"),
        created_at=now,
        updated_at=now
    )

def get_patient_care_plans(session: Session, patient_id: str, status: Optional[str] = None) -> List[CarePlan]:
    uid = safe_uuid(patient_id)
    if not uid:
        return []
    return ai_crud.get_user_care_plans(session=session, user_id=uid, status=status)

def update_care_plan_status(session: Session, plan_id: str, status: str) -> Optional[CarePlan]:
    pid = safe_uuid(plan_id)
    if not pid:
        return None
    return ai_crud.update_care_plan_status(session=session, plan_id=pid, status=status)
