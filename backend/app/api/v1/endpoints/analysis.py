from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.connections import get_db
from app.services import analysis_service
from app.core.security import get_current_user, verify_patient_ownership, verify_resource_ownership
from database.models import AIAnalysis
import uuid

router = APIRouter(prefix="/analysis", tags=["Analysis"])

class AnalysisStartRequest(BaseModel):
    patient_id: str

@router.post("/start")
def start_analysis(req: AnalysisStartRequest, db: Session = Depends(get_db)):
    try:
        analysis = analysis_service.start_analysis(db, req.patient_id)
        db.commit()
        return analysis
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{analysis_id}")
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    analysis = analysis_service.get_analysis(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@router.get("/history/{patient_id}")
def get_analysis_history(patient_id: str, db: Session = Depends(get_db)):
    return analysis_service.get_analysis_history(db, patient_id)
