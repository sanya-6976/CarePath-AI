from typing import Any, List, Optional
from sqlalchemy.orm import Session
from database.crud import ai_crud
from database.models import FollowUp
import uuid
from datetime import datetime, timezone

from database.crud.utils import safe_uuid

def create_followup(session: Session, data: dict) -> FollowUp:
    now = datetime.now(timezone.utc)
    user_id = data.get("user_id")
    plan_id = data.get("plan_id")
    
    return ai_crud.create_followup(
        session=session,
        followup_id=uuid.uuid4(),
        user_id=safe_uuid(user_id),
        plan_id=safe_uuid(plan_id),
        followup_type=data.get("followup_type", "GENERAL"),
        scheduled_date=data.get("scheduled_date"),
        description=data.get("description", ""),
        purpose=data.get("purpose", ""),
        status=data.get("status", "SCHEDULED"),
        created_at=now,
        updated_at=now
    )

def get_followups(session: Session, patient_id: str, status: Optional[str] = None) -> List[FollowUp]:
    uid = safe_uuid(patient_id)
    if not uid:
        return []
    return ai_crud.get_user_followups(session=session, user_id=uid, status=status)

def complete_followup(session: Session, followup_id: str, notes: Optional[str] = None) -> Optional[FollowUp]:
    fid = safe_uuid(followup_id)
    if not fid:
        return None
    followup = ai_crud.update_followup_status(session, fid, status="COMPLETED", completed_date=datetime.now(timezone.utc))
    if followup and notes:
        from database.crud.utils import update_record
        return update_record(session, FollowUp, fid, notes=notes)
    return followup
