"""Case-Specific Question Generation API Endpoints."""

from fastapi import APIRouter, HTTPException, status
from starlette.concurrency import run_in_threadpool

from app.schemas.case_questions import CaseQuestionRequest, CaseQuestionsReport
from app.schemas.patient_summary import PatientSummaryReport
from app.services.case_question_engine import case_question_engine
from app.core.logging import logger

router = APIRouter(prefix="/questions", tags=["Case-Specific Questions Generator"])


@router.post(
    "/generate",
    response_model=CaseQuestionsReport,
    summary="Generate targeted, case-specific clinical questions for a doctor from patient data",
)
async def generate_case_questions(request: CaseQuestionRequest) -> CaseQuestionsReport:
    """Generate case-specific questions for doctor review.

    Consumes patient summary, clinical notes, symptoms, diagnoses, medications,
    lab metrics, timeline events, and missing data gaps.
    """
    try:
        logger.info("Generating case-specific questions...")
        report = await run_in_threadpool(case_question_engine.generate_questions, request)
        return report
    except Exception as e:
        logger.error("Case question generation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate case-specific questions: {e}",
        )


@router.post(
    "/generate-from-summary",
    response_model=CaseQuestionsReport,
    summary="Generate case-specific clinical questions directly from a PatientSummaryReport",
)
async def generate_questions_from_summary(summary: PatientSummaryReport) -> CaseQuestionsReport:
    """Generate case-specific questions directly from a structured PatientSummaryReport."""
    try:
        logger.info("Generating case questions from patient summary report...")
        request = CaseQuestionRequest(patient_summary=summary)
        report = await run_in_threadpool(case_question_engine.generate_questions, request)
        return report
    except Exception as e:
        logger.error("Case question generation from summary failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate questions from patient summary: {e}",
        )
