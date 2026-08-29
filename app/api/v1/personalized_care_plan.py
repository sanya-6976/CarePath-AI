"""Personalized Care-Plan Generation API Endpoints."""

from fastapi import APIRouter, HTTPException, status
from starlette.concurrency import run_in_threadpool

from app.schemas.personalized_care_plan import PersonalizedCarePlanRequest, PersonalizedCarePlanReport
from app.services.personalized_care_plan_engine import personalized_care_plan_engine
from app.core.logging import logger

router = APIRouter(prefix="/care-plan", tags=["Personalized Care Plan Generator"])


@router.post(
    "/generate",
    response_model=PersonalizedCarePlanReport,
    summary="Generate evidence-grounded personalized care plan",
)
async def generate_personalized_care_plan(request: PersonalizedCarePlanRequest) -> PersonalizedCarePlanReport:
    """Generate structured continuity care plan grounding doctor orders and patient context."""
    try:
        logger.info("Generating personalized care plan...")
        report = await run_in_threadpool(personalized_care_plan_engine.generate_care_plan, request)
        return report
    except Exception as e:
        logger.error("Care plan generation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate care plan: {e}",
        )
