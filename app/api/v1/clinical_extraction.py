"""Clinical Information Extraction API Endpoints."""

from fastapi import APIRouter, Form, HTTPException, status
from starlette.concurrency import run_in_threadpool

from app.schemas.clinical_extraction import ClinicalExtractionRequest, ClinicalExtractionReport
from app.services.clinical_extraction_engine import clinical_extraction_engine
from app.core.logging import logger

router = APIRouter(prefix="/extract", tags=["Clinical Information Extractor"])


@router.post(
    "/clinical-info",
    response_model=ClinicalExtractionReport,
    summary="Extract structured clinical information, facts, negation status, temporal events, and conflicts from multi-modal inputs",
)
async def extract_clinical_info(request: ClinicalExtractionRequest) -> ClinicalExtractionReport:
    """Extract normalized medical entities, lab findings, medications, procedures, and conflicts."""
    try:
        logger.info("Extracting clinical information...")
        report = await run_in_threadpool(clinical_extraction_engine.extract_clinical_info, request)
        return report
    except Exception as e:
        logger.error("Clinical information extraction failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract clinical information: {e}",
        )


@router.post(
    "/text",
    response_model=ClinicalExtractionReport,
    summary="Extract structured clinical information directly from raw text",
)
async def extract_clinical_info_from_text(
    clinical_text: str = Form(..., description="Raw clinical text, notes, or patient descriptions."),
) -> ClinicalExtractionReport:
    """Extract clinical entities directly from raw text."""
    try:
        logger.info("Extracting clinical information from text...")
        request = ClinicalExtractionRequest(clinical_text=clinical_text)
        report = await run_in_threadpool(clinical_extraction_engine.extract_clinical_info, request)
        return report
    except Exception as e:
        logger.error("Clinical extraction from text failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract clinical information from text: {e}",
        )
