from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.connections import get_db
from app.services import patient_service
import uuid

from database.crud.utils import safe_uuid
from app.core.security import get_current_user, verify_patient_ownership, require_admin

router = APIRouter(prefix="/patients", tags=["Patients"])

class PatientData(BaseModel):
    user_id: str
    first_name: str
    last_name: str

@router.post("")
def create_patient(data: PatientData, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    verify_patient_ownership(current_user, data.user_id)
    try:
        profile = patient_service.create_patient(db, data.user_id, data.model_dump())
        db.commit()
        return profile
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("")
def get_all_patients(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_admin(current_user)
    profiles = patient_service.get_all_patients(db)
    result = []
    for profile in profiles:
        first_name = profile.first_name or ""
        last_name = profile.last_name or ""
        full_name = f"{first_name} {last_name}".strip() or "Patient"
        result.append({
            "id": str(profile.user_id),
            "user_id": str(profile.user_id),
            "name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "age": 30,
            "gender": profile.gender or "Male",
            "blood_type": profile.blood_group or "O+",
            "allergies": [],
            "medical_history": profile.medical_summary or "",
            "current_symptoms": ""
        })
    return result

@router.get("/{patient_id}")
def get_patient(patient_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    verify_patient_ownership(current_user, patient_id)
    uid = safe_uuid(patient_id)
    profile = patient_service.get_patient(db, uid or patient_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found.")

    first_name = profile.first_name or ""
    last_name = profile.last_name or ""
    full_name = f"{first_name} {last_name}".strip() or "Patient"

    return {
        "id": str(profile.user_id),
        "user_id": str(profile.user_id),
        "name": full_name,
        "first_name": first_name,
        "last_name": last_name,
        "age": 30,
        "gender": profile.gender or "Male",
        "blood_type": profile.blood_group or "O+",
        "allergies": [],
        "medical_history": profile.medical_summary or "",
        "current_symptoms": ""
    }

@router.put("/{patient_id}")
def update_patient(patient_id: str, data: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    verify_patient_ownership(current_user, patient_id)
    profile = patient_service.update_patient(db, patient_id, data)
    if profile:
        db.commit()
    
    first_name = profile.first_name if profile and profile.first_name else ""
    last_name = profile.last_name if profile and profile.last_name else ""
    full_name = f"{first_name} {last_name}".strip() or data.get("name", "Patient")

    return {
        "id": patient_id,
        "user_id": patient_id,
        "name": full_name,
        "first_name": first_name,
        "last_name": last_name,
        "age": data.get("age", 30),
        "gender": profile.gender if profile and profile.gender else data.get("gender", "Male"),
        "blood_type": profile.blood_group if profile and profile.blood_group else data.get("blood_type", "O+"),
        "allergies": data.get("allergies", []),
        "medical_history": profile.medical_summary if profile and profile.medical_summary else data.get("medical_history", ""),
        "current_symptoms": data.get("current_symptoms", "")
    }

@router.delete("/{patient_id}")
def delete_patient(patient_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    verify_patient_ownership(current_user, patient_id)
    uid = safe_uuid(patient_id)
    success = patient_service.delete_patient(db, uid or patient_id)
    db.commit()
    return {"success": success}
