"""Medical Vision API Endpoints."""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from starlette.concurrency import run_in_threadpool
from app.schemas.vision import VisionAnalysisResult
from app.services.vision_engine import vision_engine
from app.core.exceptions import DICOMProcessingError
from app.core.logging import logger

router = APIRouter(prefix="/vision", tags=["Medical Vision"])


@router.post("/analyze", response_model=VisionAnalysisResult, summary="Analyze X-ray or DICOM image for clinical findings")
async def analyze_medical_image(
    file: UploadFile = File(...)
):
    """Upload a DICOM file (.dcm) or medical image (.png, .jpg) to receive AI diagnostic findings and a Grad-CAM heatmap."""
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded image file is empty.")

        logger.info(f"Analyzing diagnostic medical image: {file.filename} ({len(content)} bytes)")
        # Offload vision model tensor computation & Grad-CAM to threadpool
        result = await run_in_threadpool(
            vision_engine.analyze_image,
            content,
            filename=file.filename or "image.png"
        )
        return result

    except DICOMProcessingError as e:
        logger.error(f"DICOM processing error: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected vision error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to analyze medical image.")
