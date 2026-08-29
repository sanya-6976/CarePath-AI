from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connections import get_db
from database.models import MedicalFile
from database.crud.utils import safe_uuid
from typing import List, Any, Optional

router = APIRouter(prefix="/records", tags=["Records"])

@router.get("")
@router.get("/")
def get_medical_records(patient_id: Optional[str] = None, db: Session = Depends(get_db)):
    if patient_id:
        uid = safe_uuid(patient_id)
        if uid:
            files = db.query(MedicalFile).filter(MedicalFile.user_id == uid).order_by(MedicalFile.upload_date.desc()).all()
        else:
            files = db.query(MedicalFile).order_by(MedicalFile.upload_date.desc()).all()
    else:
        files = db.query(MedicalFile).order_by(MedicalFile.upload_date.desc()).all()

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
def delete_medical_record(record_id: str, db: Session = Depends(get_db)):
    rid = safe_uuid(record_id)
    if rid:
        f = db.query(MedicalFile).filter(MedicalFile.file_id == rid).first()
        if f:
            db.delete(f)
            db.commit()
            return {"status": "deleted", "id": record_id}
    return {"status": "deleted", "id": record_id}
