"""Differential Diagnosis & CarePath API Endpoint."""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Optional
from starlette.concurrency import run_in_threadpool
from app.schemas.diagnosis import PatientCarePathSynthesis
from app.services.carepath_engine import carepath_engine
from app.core.logging import logger

router = APIRouter(prefix="/diagnosis", tags=["CarePath Synthesizer"])


@router.post("/synthesize", response_model=PatientCarePathSynthesis, summary="Synthesize multi-modal patient data into differential diagnosis and CarePath recommendations")
async def synthesize_patient_carepath(
    clinical_notes: Optional[str] = Form(None),
    document_file: Optional[UploadFile] = File(None),
    image_file: Optional[UploadFile] = File(None),
):
    """Synthesize clinical text, document OCR, and diagnostic images into a structured CarePath report."""
    try:
        logger.info("Executing multi-modal CarePath synthesis...")
        doc_bytes = await document_file.read() if document_file else None
        img_bytes = await image_file.read() if image_file else None

        result = await run_in_threadpool(
            carepath_engine.synthesize_patient_case,
            clinical_notes=clinical_notes,
            document_bytes=doc_bytes,
            document_filename=document_file.filename if document_file else "doc.png",
            image_bytes=img_bytes,
            image_filename=image_file.filename if image_file else "xray.png"
        )
        return result

    except Exception as e:
        logger.error(f"CarePath synthesis error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to synthesize patient CarePath.")
