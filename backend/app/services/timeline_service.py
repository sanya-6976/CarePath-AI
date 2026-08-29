from typing import Any, List, Optional
from sqlalchemy.orm import Session
from database.crud import system_crud
from database.models import TimelineEvent
import uuid
from datetime import datetime, timezone

from database.crud.utils import safe_uuid

def get_timeline_events(session: Session, patient_id: str, event_type: Optional[str] = None, limit: int = 50) -> List[TimelineEvent]:
    uid = safe_uuid(patient_id)
    if not uid:
        return []
    return system_crud.get_user_timeline_events(session=session, user_id=uid, event_type=event_type, limit=limit)

def add_timeline_event(session: Session, data: dict) -> TimelineEvent:
    now = datetime.now(timezone.utc)
    user_id = data.get("user_id")
    event_date = data.get("event_date")
    uid = safe_uuid(user_id)
    rel_id = safe_uuid(data.get("related_record_id"))
    
    return system_crud.create_timeline_event(
        session=session,
        event_id=uuid.uuid4(),
        user_id=uid,
        event_type=data.get("event_type", "GENERAL"),
        event_date=event_date or now,
        event_title=data.get("event_title", ""),
        event_description=data.get("event_description", ""),
        severity=data.get("severity", "MEDIUM"),
        related_record_id=rel_id,
        related_record_type=data.get("related_record_type"),
        visible_to_patient=data.get("visible_to_patient", True),
        created_at=now
    )

def auto_log_timeline_event(
    session: Session,
    user_id: Any,
    event_type: str,
    event_title: str,
    event_description: str = "",
    severity: str = "MEDIUM",
    related_record_id: Optional[Any] = None,
    related_record_type: Optional[str] = None
) -> TimelineEvent:
    """Helper to auto-persist a timeline event from background domain services."""
    return add_timeline_event(
        session=session,
        data={
            "user_id": str(user_id),
            "event_type": event_type,
            "event_title": event_title,
            "event_description": event_description,
            "severity": severity,
            "related_record_id": str(related_record_id) if related_record_id else None,
            "related_record_type": related_record_type
        }
    )

