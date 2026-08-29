from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from database.connections import get_db
from app.services import upload_service

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form("Medical Report"),
    patient_id: str = Form("demo_user"),
    db: Session = Depends(get_db)
):
    try:
        content = await file.read()
        return upload_service.process_and_save_upload(
            session=db,
            file_bytes=content,
            filename=file.filename or "uploaded_document",
            user_id=patient_id or "demo_user",
            category=category
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    patient_id: str = Form("demo_user"),
    db: Session = Depends(get_db)
):
    content = await file.read()
    return upload_service.process_and_save_upload(
        session=db,
        file_bytes=content,
        filename=file.filename or "uploaded_image.png",
        user_id=patient_id or "demo_user",
        category="Imaging/Scan"
    )

@router.post("/report")
async def upload_report(
    file: UploadFile = File(...),
    patient_id: str = Form("demo_user"),
    db: Session = Depends(get_db)
):
    content = await file.read()
    return upload_service.process_and_save_upload(
        session=db,
        file_bytes=content,
        filename=file.filename or "uploaded_report.pdf",
        user_id=patient_id or "demo_user",
        category="Medical Report"
    )

@router.post("/prescription")
async def upload_prescription(
    file: UploadFile = File(...),
    patient_id: str = Form("demo_user"),
    db: Session = Depends(get_db)
):
    content = await file.read()
    return upload_service.process_and_save_upload(
        session=db,
        file_bytes=content,
        filename=file.filename or "uploaded_prescription.pdf",
        user_id=patient_id or "demo_user",
        category="Prescription"
    )
