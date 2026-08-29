from fastapi import APIRouter
from src.api.v1.endpoints import (
    health,
    encounters,
    documents,
    medications,
    evidence,
    doctor_bridge,
    timeline,
    referrals,
    care_plans,
)

api_v1_router = APIRouter()

api_v1_router.include_router(health.router)
api_v1_router.include_router(encounters.router)
api_v1_router.include_router(documents.router)
api_v1_router.include_router(medications.router)
api_v1_router.include_router(evidence.router)
api_v1_router.include_router(doctor_bridge.router)
api_v1_router.include_router(timeline.router)
api_v1_router.include_router(referrals.router)
api_v1_router.include_router(care_plans.router)
