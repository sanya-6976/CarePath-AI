"""API Router Aggregator."""
import sys
import os

# Unify app package paths between root app/ and backend/app/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
backend_app_dir = os.path.join(project_root, "backend", "app")
root_app_dir = os.path.join(project_root, "app")

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    import app as top_app
    if hasattr(top_app, "__path__") and backend_app_dir not in top_app.__path__:
        top_app.__path__.append(backend_app_dir)

    for subpkg in ["core", "services", "schemas", "models", "api", "api.v1", "api.v1.endpoints"]:
        pkg_name = f"app.{subpkg}"
        backend_sub = os.path.join(backend_app_dir, *subpkg.split("."))
        root_sub = os.path.join(root_app_dir, *subpkg.split("."))
        try:
            mod = __import__(pkg_name, fromlist=["__path__"])
            if hasattr(mod, "__path__"):
                if root_sub not in mod.__path__ and os.path.exists(root_sub):
                    mod.__path__.append(root_sub)
                if backend_sub not in mod.__path__ and os.path.exists(backend_sub):
                    mod.__path__.append(backend_sub)
        except Exception:
            pass
except Exception:
    pass

from fastapi import APIRouter
from app.api.v1.ocr import router as ocr_router
from app.api.v1.vision import router as vision_router
from app.api.v1.nlp import router as nlp_router
from app.api.v1.rag import router as rag_router
from app.api.v1.diagnosis import router as diagnosis_router
from app.api.v1.patient_summary import router as summary_router
from app.api.v1.case_questions import router as questions_router
from app.api.v1.clinical_extraction import router as extraction_router
from app.api.v1.doctor_feedback import router as feedback_router
from app.api.v1.treatment_response import router as treatment_response_router
from app.api.v1.follow_up_intelligence import router as follow_up_router
from app.api.v1.personalized_care_plan import router as care_plan_router


api_router = APIRouter()

api_router.include_router(ocr_router)
api_router.include_router(vision_router)
api_router.include_router(nlp_router)
api_router.include_router(rag_router)
api_router.include_router(diagnosis_router)
api_router.include_router(summary_router)
api_router.include_router(questions_router)
api_router.include_router(extraction_router)
api_router.include_router(feedback_router)
api_router.include_router(treatment_response_router)
api_router.include_router(follow_up_router)
api_router.include_router(care_plan_router)

# Mount backend database & auth routers
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.patients import router as patients_router
from app.api.v1.endpoints.analysis import router as analysis_router
from app.api.v1.endpoints.timeline import router as timeline_router
from app.api.v1.endpoints.followup import router as followup_router
from app.api.v1.endpoints.notifications import router as notifications_router
from app.api.v1.endpoints.upload import router as upload_router
from app.api.v1.endpoints.medications import router as medications_router
from app.api.v1.endpoints.careplans import router as careplans_router
from app.api.v1.endpoints.memory import router as memory_router
from app.api.v1.endpoints.doctor import router as doctor_router
from app.api.v1.endpoints.analytics import router as analytics_router
from app.api.v1.endpoints.records import router as records_router
from app.api.v1.endpoints.agents import router as agents_router

for r in [
    auth_router, patients_router, analysis_router, timeline_router,
    followup_router, notifications_router, upload_router, medications_router,
    careplans_router, memory_router, doctor_router, analytics_router,
    records_router, agents_router
]:
    api_router.include_router(r)




@api_router.get("/status", tags=["Health"])
async def get_status():
    return {
        "status": "healthy",
        "service": "CarePath AI API v1",
        "version": "0.1.0"
    }
