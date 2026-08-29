from fastapi import APIRouter
from src.config import settings

router = APIRouter(tags=["Health & Diagnostics"])


@router.get("/health", summary="Liveness Probe")
async def health_check():
    """Returns status 200 OK if service is alive."""
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "service": settings.PROJECT_NAME,
    }
