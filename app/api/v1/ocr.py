"""OCR API Endpoints."""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from starlette.concurrency import run_in_threadpool
from app.schemas.ocr import OCRResult
from app.services.ocr_engine import ocr_engine
from app.core.exceptions import OCRExtractionError
from app.core.logging import logger

router = APIRouter(prefix="/ocr", tags=["OCR Ingestion"])


@router.post("/extract", response_model=OCRResult, summary="Extract clinical data from medical image or PDF document")
async def extract_ocr(
    file: UploadFile = File(...),
):
    """Upload a medical prescription, lab report, or clinical note to extract structured data."""
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

        logger.info(f"Processing OCR request for file: {file.filename} ({len(content)} bytes)")
        # Offload heavy CPU OCR processing to threadpool
        result = await run_in_threadpool(
            ocr_engine.extract_text,
            content,
            filename=file.filename or "uploaded_doc.png"
        )
        return result

    except OCRExtractionError as e:
        logger.error(f"OCR Extraction error: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during OCR processing: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process document OCR.")
