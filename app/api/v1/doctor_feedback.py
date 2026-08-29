"""Doctor Feedback Interpretation API Endpoints."""

from fastapi import APIRouter, Form, HTTPException, status
from starlette.concurrency import run_in_threadpool

from app.schemas.doctor_feedback import DoctorFeedbackRequest, DoctorFeedbackInterpretationReport
from app.services.doctor_feedback_engine import doctor_feedback_engine
from app.core.logging import logger

router = APIRouter(prefix="/feedback", tags=["Doctor Feedback Interpreter"])


@router.post(
    "/interpret",
    response_model=DoctorFeedbackInterpretationReport,
    summary="Interpret doctor consultation notes, Q&A answers, and structure CarePath Memory candidates",
)
async def interpret_doctor_feedback(request: DoctorFeedbackRequest) -> DoctorFeedbackInterpretationReport:
    """Interpret clinician feedback, classify statement origins, extract follow-ups/referrals, and build memory candidates."""
    try:
        logger.info("Interpreting doctor feedback...")
        report = await run_in_threadpool(doctor_feedback_engine.interpret_feedback, request)
        return report
    except Exception as e:
        logger.error("Doctor feedback interpretation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to interpret doctor feedback: {e}",
        )


@router.post(
    "/interpret-notes",
    response_model=DoctorFeedbackInterpretationReport,
    summary="Interpret raw doctor consultation notes text",
)
async def interpret_doctor_notes_text(
    doctor_notes: str = Form(..., description="Raw doctor consultation notes or clinical assessment text."),
) -> DoctorFeedbackInterpretationReport:
    """Interpret raw doctor notes text into memory-ready clinical objects."""
    try:
        logger.info("Interpreting doctor notes text...")
        request = DoctorFeedbackRequest(doctor_notes=doctor_notes)
        report = await run_in_threadpool(doctor_feedback_engine.interpret_feedback, request)
        return report
    except Exception as e:
        logger.error("Doctor notes interpretation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to interpret doctor notes text: {e}",
        )
