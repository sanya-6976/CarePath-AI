from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.connections import get_db
from app.services import doctor_service
from app.core.security import get_current_user, verify_patient_ownership

router = APIRouter(prefix="/doctor", tags=["Doctor Bridge"])

class ConsultationCreate(BaseModel):
    user_id: str
    visit_type: Optional[str] = "CONSULTATION"
    provider_name: Optional[str] = "Attending Physician"
    facility_name: Optional[str] = "CarePath Medical Center"
    visit_reason: Optional[str] = None
    notes: Optional[str] = None
    outcome: Optional[str] = None
    status: Optional[str] = "COMPLETED"

class DoctorFeedbackCreate(BaseModel):
    user_id: str
    feedback_type: Optional[str] = "DOCTOR_REVIEW"
    rating: Optional[int] = 5
    title: Optional[str] = "Clinical Review"
    message: str
    related_record_id: Optional[str] = None
    related_record_type: Optional[str] = "CARE_PLAN"
    status: Optional[str] = "APPROVED"
    response: Optional[str] = None

@router.post("/consultations", status_code=201)
def create_consultation(data: ConsultationCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    verify_patient_ownership(current_user, data.user_id)
    return doctor_service.create_consultation(db, data.model_dump())

@router.get("/consultations/{patient_id}")
def get_consultations(patient_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    verify_patient_ownership(current_user, patient_id)
    return doctor_service.get_patient_consultations(db, patient_id)

@router.post("/feedback", status_code=201)
def submit_doctor_feedback(data: DoctorFeedbackCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    verify_patient_ownership(current_user, data.user_id)
    return doctor_service.add_doctor_feedback(db, data.model_dump())

@router.get("/recommendations/{patient_id}")
def get_recommendations_for_review(patient_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    verify_patient_ownership(current_user, patient_id)
    return doctor_service.get_doctor_recommendations(db, patient_id)
