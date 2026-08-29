"""Patient Summary Generation API Endpoints."""

from fastapi import APIRouter, Form, HTTPException, status
from typing import Optional
from starlette.concurrency import run_in_threadpool

from app.schemas.patient_summary import PatientSummaryRequest, PatientSummaryReport
from app.services.patient_summary_engine import patient_summary_engine
from app.core.logging import logger

router = APIRouter(prefix="/summary", tags=["Patient Summary Generator"])


@router.post(
    "/generate",
    response_model=PatientSummaryReport,
    summary="Generate a validated, structured patient summary report from multi-modal inputs",
)
async def generate_patient_summary(request: PatientSummaryRequest) -> PatientSummaryReport:
    """Generate a structured patient summary report.

    Consumes clinical notes, OCR documents, prescriptions, lab metrics,
    symptoms, diagnoses, timeline events, and RAG guidelines.
    """
    try:
        logger.info("Generating patient summary report...")
        report = await run_in_threadpool(patient_summary_engine.generate_summary, request)
        return report
    except Exception as e:
        logger.error("Patient summary generation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate patient summary: {e}",
        )


@router.post(
    "/generate-from-notes",
    response_model=PatientSummaryReport,
    summary="Generate a structured patient summary directly from clinical notes text",
)
async def generate_patient_summary_from_notes(
    clinical_notes: str = Form(..., description="Raw clinical notes or unstructured patient presentation text."),
    include_rag: bool = Form(True, description="Whether to query RAG for external guideline evidence."),
) -> PatientSummaryReport:
    """Generate a structured summary directly from raw clinical text."""
    try:
        logger.info("Generating patient summary from clinical notes...")
        request = PatientSummaryRequest(
            clinical_notes=clinical_notes,
            include_rag=include_rag,
        )
        report = await run_in_threadpool(patient_summary_engine.generate_summary, request)
        return report
    except Exception as e:
        logger.error("Patient summary generation from notes failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate patient summary from notes: {e}",
        )
