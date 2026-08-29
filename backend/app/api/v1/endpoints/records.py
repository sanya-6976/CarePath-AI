from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connections import get_db
from database.models import MedicalFile
from database.crud.utils import safe_uuid
from typing import List, Any
from app.core.security import get_current_user, verify_resource_ownership

router = APIRouter(prefix="/records", tags=["Records"])

@router.get("")
@router.get("/")
def get_medical_records(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    files = db.query(MedicalFile).filter(MedicalFile.user_id == current_user.user_id).order_by(MedicalFile.upload_date.desc()).all()

    records = []
    for f in files:
        file_type = (f.file_type or "").lower()
        if "prescrip" in file_type:
            rtype = "prescription"
        elif "scan" in file_type or "image" in file_type or "xray" in file_type or "ct" in file_type:
            rtype = "image"
        elif "lab" in file_type or "blood" in file_type:
            rtype = "report"
        else:
            rtype = "report"

        records.append({
            "id": str(f.file_id),
            "patient_id": str(f.user_id),
            "title": f.file_name,
            "type": rtype,
            "file_url": f.storage_path or "#",
            "file_name": f.file_name,
            "created_at": f.created_at.isoformat() if f.created_at else f.upload_date.isoformat() if f.upload_date else None,
            "summary": (f.ocr_text[:300] + "...") if f.ocr_text and len(f.ocr_text) > 300 else (f.ocr_text or f"Uploaded {f.file_type} document.")
        })

    return records

@router.delete("/{record_id}")
def delete_medical_record(record_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rid = safe_uuid(record_id)
    if rid:
        f = db.query(MedicalFile).filter(MedicalFile.file_id == rid).first()
        if f:
            verify_resource_ownership(current_user, f.user_id)
            db.delete(f)
            db.commit()
            return {"status": "deleted", "id": record_id}
    return {"status": "deleted", "id": record_id}
