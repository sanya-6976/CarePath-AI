from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from database.connections import get_db
from app.services import upload_service
from app.core.security import get_current_user

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form("Medical Report"),
    patient_id: str | None = Form(None),
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    try:
        content = await file.read()
        return upload_service.process_and_save_upload(
            session=db,
            file_bytes=content,
            filename=file.filename or "uploaded_document",
            user_id=str(current_user.user_id),
            category=category
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    patient_id: str | None = Form(None),
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    content = await file.read()
    return upload_service.process_and_save_upload(
        session=db,
        file_bytes=content,
        filename=file.filename or "uploaded_image.png",
        user_id=str(current_user.user_id),
        category="Imaging/Scan"
    )

@router.post("/report")
async def upload_report(
    file: UploadFile = File(...),
    patient_id: str | None = Form(None),
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    content = await file.read()
    return upload_service.process_and_save_upload(
        session=db,
        file_bytes=content,
        filename=file.filename or "uploaded_report.pdf",
        user_id=str(current_user.user_id),
        category="Medical Report"
    )

@router.post("/prescription")
async def upload_prescription(
    file: UploadFile = File(...),
    patient_id: str | None = Form(None),
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    content = await file.read()
    return upload_service.process_and_save_upload(
        session=db,
        file_bytes=content,
        filename=file.filename or "uploaded_prescription.pdf",
        user_id=str(current_user.user_id),
        category="Prescription"
    )
