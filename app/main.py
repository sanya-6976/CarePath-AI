import sys
import os

# Unify app package paths between root app/ and backend/app/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
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


from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import MedicalAIException, http_status_for
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Multi-Modal Medical Intelligence Platform API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Enable CORS for Streamlit UI & external consumers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


# Register backend endpoints (Auth, Patients, Timeline, Records, Agents, etc.)
try:
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
        app.include_router(r, prefix=settings.API_V1_STR)
except Exception as exc:
    logger.warning("Notice: Backend endpoints loading skipped or partial: %s", exc)





# ---------------------------------------------------------------------------
# Global Exception Handler — converts MedicalAIException → structured JSON
# ---------------------------------------------------------------------------

@app.exception_handler(MedicalAIException)
async def medical_ai_exception_handler(request: Request, exc: MedicalAIException) -> JSONResponse:
    """Return a structured error response for all CarePath AI typed exceptions.

    The response body contains:
    - ``error_code``: machine-readable snake_case error category.
    - ``detail``: human-readable error description.

    HTTP status is determined by :func:`~app.core.exceptions.http_status_for`.
    """
    status_code = http_status_for(exc)
    logger.warning(
        "MedicalAIException: code=%s status=%d path=%s msg=%s",
        exc.error_code,
        status_code,
        request.url.path,
        exc.message,
    )
    return JSONResponse(
        status_code=status_code,
        content={
            "error_code": exc.error_code,
            "detail": exc.message,
        },
    )


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting CarePath AI application server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

