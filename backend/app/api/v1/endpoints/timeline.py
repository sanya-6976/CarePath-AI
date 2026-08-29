from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.connections import get_db
from app.services import timeline_service
from app.core.security import get_current_user, verify_patient_ownership

router = APIRouter(prefix="/timeline", tags=["Timeline"])

class TimelineEventData(BaseModel):
    user_id: str
    event_type: str
    event_title: str

@router.get("/{patient_id}")
def get_timeline(patient_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    verify_patient_ownership(current_user, patient_id)
    return timeline_service.get_timeline_events(db, patient_id)

@router.post("/event")
def add_event(data: TimelineEventData, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    verify_patient_ownership(current_user, data.user_id)
    event = timeline_service.add_timeline_event(db, data.model_dump())
    db.commit()
    return event
