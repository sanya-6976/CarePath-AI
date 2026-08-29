from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.connections import get_db
from app.services import followup_service
from app.core.security import get_current_user, verify_patient_ownership, verify_resource_ownership
from database.models import FollowUp
from database.crud.utils import safe_uuid

router = APIRouter(prefix="/followup", tags=["FollowUp"])

class FollowUpData(BaseModel):
    user_id: str
    plan_id: Optional[str] = None
    followup_type: Optional[str] = "GENERAL"
    scheduled_date: Optional[str] = None
    description: Optional[str] = None
    purpose: Optional[str] = None
    status: Optional[str] = "SCHEDULED"

class CompleteFollowupData(BaseModel):
    notes: Optional[str] = None

@router.post("", status_code=201)
def create_followup(data: FollowUpData, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    verify_patient_ownership(current_user, data.user_id)
    return followup_service.create_followup(db, data.model_dump())

@router.get("/{patient_id}")
def get_followups(
    patient_id: str,
    status: Optional[str] = Query(None, description="Filter by status e.g. SCHEDULED, COMPLETED, CANCELLED"),
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    verify_patient_ownership(current_user, patient_id)
    return followup_service.get_followups(db, patient_id, status=status)

@router.put("/{followup_id}/complete")
def complete_followup(
    followup_id: str,
    body: Optional[CompleteFollowupData] = None,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    record = db.query(FollowUp).filter(FollowUp.followup_id == safe_uuid(followup_id)).first()
    if not record: raise HTTPException(status_code=404, detail="Follow-up record not found")
    verify_resource_ownership(current_user, record.user_id)
    notes = body.notes if body else None
    fup = followup_service.complete_followup(db, followup_id, notes=notes)
    if not fup:
        raise HTTPException(status_code=404, detail="Follow-up record not found")
    return fup
