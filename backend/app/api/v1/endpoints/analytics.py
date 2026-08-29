from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connections import get_db
from backend.app.services import analytics_service
from app.core.security import get_current_user, verify_patient_ownership

router = APIRouter(prefix="/analytics", tags=["Analytics & Dashboard"])

@router.get("/{patient_id}")
def get_patient_analytics(patient_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Computes clinical continuity metrics, medication adherence %,
    care plan completion rates, and symptom severity distributions for a patient.
    """
    verify_patient_ownership(current_user, patient_id)
    try:
        return analytics_service.get_patient_analytics(db, patient_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to calculate analytics: {str(e)}")
