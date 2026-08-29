from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connections import get_db

try:
    from app.services import analytics_service
except ImportError:
    from backend.app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics & Dashboard"])

@router.get("/{patient_id}")
def get_patient_analytics(patient_id: str, db: Session = Depends(get_db)):
    """
    Computes clinical continuity metrics, medication adherence %,
    care plan completion rates, and symptom severity distributions for a patient.
    """
    try:
        return analytics_service.get_patient_analytics(db, patient_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to calculate analytics: {str(e)}")
