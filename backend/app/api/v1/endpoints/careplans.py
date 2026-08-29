from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.connections import get_db
from app.services import careplan_service
from app.core.security import get_current_user, verify_patient_ownership, verify_resource_ownership
from database.models import CarePlan
from database.crud.utils import safe_uuid

router = APIRouter(prefix="/careplans", tags=["Care Plans"])

class CarePlanCreate(BaseModel):
    user_id: str
    analysis_id: Optional[str] = None
    plan_name: str
    plan_description: Optional[str] = None
    next_steps: Optional[str] = None
    appointment_prep: Optional[str] = None
    lifestyle_changes: Optional[str] = None
    monitoring_points: Optional[str] = None
    estimated_duration: Optional[str] = None
    priority: Optional[str] = "MEDIUM"
    status: Optional[str] = "ACTIVE"

class CarePlanStatusUpdate(BaseModel):
    status: str

@router.post("/", status_code=201)
def create_care_plan(data: CarePlanCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    verify_patient_ownership(current_user, data.user_id)
    plan = careplan_service.create_care_plan(db, data.model_dump())
    return plan

@router.get("/{patient_id}")
def get_patient_care_plans(
    patient_id: str,
    status: Optional[str] = Query(None, description="Filter by status e.g. ACTIVE, COMPLETED, ARCHIVED"),
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    verify_patient_ownership(current_user, patient_id)
    return careplan_service.get_patient_care_plans(db, patient_id, status=status)

@router.put("/{plan_id}/status")
def update_care_plan_status(
    plan_id: str,
    body: CarePlanStatusUpdate,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    plan = db.query(CarePlan).filter(CarePlan.plan_id == safe_uuid(plan_id)).first()
    if not plan: raise HTTPException(status_code=404, detail="Care plan record not found")
    verify_resource_ownership(current_user, plan.user_id)
    updated = careplan_service.update_care_plan_status(db, plan_id, body.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Care plan record not found")
    return updated
