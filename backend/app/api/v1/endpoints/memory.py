from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connections import get_db
from app.services import memory_service
from app.core.security import get_current_user, verify_patient_ownership

router = APIRouter(prefix="/memory", tags=["CarePath Memory"])

@router.get("/{patient_id}")
def get_carepath_memory(patient_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Retrieves the complete, aggregated CarePath Memory tree for a patient.
    Consolidates profile, consultations, symptoms, reports, medications,
    referrals, care plans, timeline events, follow-ups, and doctor feedback.
    """
    verify_patient_ownership(current_user, patient_id)
    try:
        memory = memory_service.get_patient_carepath_memory(db, patient_id)
        return memory
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch CarePath Memory: {str(e)}")
