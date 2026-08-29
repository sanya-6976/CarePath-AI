"""Treatment Response Analysis API Endpoints."""

from fastapi import APIRouter, HTTPException, status
from starlette.concurrency import run_in_threadpool

from app.schemas.treatment_response import TreatmentResponseRequest, TreatmentResponseReport
from app.services.treatment_response_engine import treatment_response_engine
from app.core.logging import logger

router = APIRouter(prefix="/treatment-response", tags=["Treatment Response Analyzer"])


@router.post(
    "/analyze",
    response_model=TreatmentResponseReport,
    summary="Analyze documented treatment events against clinical outcomes",
)
async def analyze_treatment_response(request: TreatmentResponseRequest) -> TreatmentResponseReport:
    """Evaluate documented treatment events, symptom changes, and lab metric changes against clinical evidence."""
    try:
        logger.info("Analyzing treatment response...")
        report = await run_in_threadpool(treatment_response_engine.analyze_treatment_response, request)
        return report
    except Exception as e:
        logger.error("Treatment response analysis failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze treatment response: {e}",
        )
