"""Follow-Up Intelligence API Endpoints."""

from fastapi import APIRouter, HTTPException, status
from starlette.concurrency import run_in_threadpool

from app.schemas.follow_up_intelligence import FollowUpIntelligenceRequest, FollowUpIntelligenceReport
from app.services.follow_up_intelligence_engine import follow_up_intelligence_engine
from app.core.logging import logger

router = APIRouter(prefix="/follow-up", tags=["Follow-Up Intelligence"])


@router.post(
    "/analyze",
    response_model=FollowUpIntelligenceReport,
    summary="Analyze care-continuity follow-up requirements",
)
async def analyze_follow_up_needs(request: FollowUpIntelligenceRequest) -> FollowUpIntelligenceReport:
    """Analyze clinician instructions, unresolved symptoms, and treatment responses to identify follow-up needs."""
    try:
        logger.info("Analyzing follow-up intelligence...")
        report = await run_in_threadpool(follow_up_intelligence_engine.analyze_follow_up, request)
        return report
    except Exception as e:
        logger.error("Follow-up intelligence analysis failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze follow-up intelligence: {e}",
        )
