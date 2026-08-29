from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.connections import get_db
from app.services import medication_service
from app.core.security import get_current_user, verify_patient_ownership, verify_resource_ownership
from database.models import Medication
from database.crud.utils import safe_uuid

router = APIRouter(prefix="/medications", tags=["Medications"])

class MedicationCreate(BaseModel):
    user_id: str
    medication_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    route: Optional[str] = "oral"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    purpose: Optional[str] = None
    side_effects: Optional[str] = None
    instructions: Optional[str] = None
    prescribed_by: Optional[str] = None
    status: Optional[str] = "ACTIVE"

class MedicationStatusUpdate(BaseModel):
    status: str

@router.post("/", status_code=201)
def create_medication(data: MedicationCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    verify_patient_ownership(current_user, data.user_id)
    medication = medication_service.add_medication(db, data.model_dump())
    return medication

@router.get("/{patient_id}")
def get_patient_medications(
    patient_id: str,
    status: Optional[str] = Query(None, description="Filter by status e.g. ACTIVE, COMPLETED, DISCONTINUED"),
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    verify_patient_ownership(current_user, patient_id)
    return medication_service.get_patient_medications(db, patient_id, status=status)

@router.put("/{medication_id}/status")
def update_medication_status(
    medication_id: str,
    body: MedicationStatusUpdate,
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    medication = db.query(Medication).filter(Medication.medication_id == safe_uuid(medication_id)).first()
    if not medication:
        raise HTTPException(status_code=404, detail="Medication record not found")
    verify_resource_ownership(current_user, medication.user_id)
    updated = medication_service.update_medication_status(db, medication_id, body.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Medication record not found")
    return updated

@router.get("/{patient_id}/adherence")
def get_medication_adherence(patient_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    verify_patient_ownership(current_user, patient_id)
    return medication_service.get_medication_adherence(db, patient_id)
