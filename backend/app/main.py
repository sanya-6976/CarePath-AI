"""
CarePath AI - Main FastAPI Application Entry Point
=================================================
Configures Middlewares, CORS, Structured Logging, Health Check, and mounts API v1 Routers.
"""

import sys
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# Ensure backend_dir is at sys.path[0] and merge package search paths
backend_app_dir = os.path.abspath(os.path.dirname(__file__))
backend_dir = os.path.abspath(os.path.join(backend_app_dir, ".."))
project_root = os.path.abspath(os.path.join(backend_dir, ".."))
root_app_dir = os.path.abspath(os.path.join(project_root, "app"))

if backend_dir in sys.path:
    sys.path.remove(backend_dir)
sys.path.insert(0, backend_dir)

if project_root not in sys.path:
    sys.path.append(project_root)

# Explicitly import 'app' and unify package search paths
import app
if hasattr(app, "__path__"):
    if backend_app_dir not in app.__path__:
        app.__path__.insert(0, backend_app_dir)
    if root_app_dir not in app.__path__ and os.path.exists(root_app_dir):
        app.__path__.append(root_app_dir)

# Unify sub-packages (api, core, services, schemas, models, database)
for subpkg in ["api", "core", "services", "schemas", "models", "database"]:
    pkg_name = f"app.{subpkg}"
    try:
        mod = __import__(pkg_name, fromlist=["__path__"])
        if hasattr(mod, "__path__"):
            b_sub = os.path.join(backend_app_dir, subpkg)
            r_sub = os.path.join(root_app_dir, subpkg)
            if b_sub not in mod.__path__ and os.path.exists(b_sub):
                mod.__path__.insert(0, b_sub)
            if r_sub not in mod.__path__ and os.path.exists(r_sub):
                mod.__path__.append(r_sub)
    except Exception:
        pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.api.v1.endpoints.agents import router as agents_router
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

try:
    from app.api.v1.endpoints.medical import router as medical_router
except ImportError:
    medical_router = None

try:
    from app.api.v1.endpoints.companion import router as companion_router
except ImportError:
    companion_router = None

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG,
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, "BACKEND_CORS_ORIGINS", getattr(settings, "CORS_ORIGINS", ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"])),
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|.*\.netlify\.app)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(agents_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(patients_router, prefix=settings.API_V1_STR)
app.include_router(analysis_router, prefix=settings.API_V1_STR)
app.include_router(timeline_router, prefix=settings.API_V1_STR)
app.include_router(followup_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router, prefix=settings.API_V1_STR)
app.include_router(upload_router, prefix=settings.API_V1_STR)
app.include_router(medications_router, prefix=settings.API_V1_STR)
app.include_router(careplans_router, prefix=settings.API_V1_STR)
app.include_router(memory_router, prefix=settings.API_V1_STR)
app.include_router(doctor_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(records_router, prefix=settings.API_V1_STR)

if medical_router:
    app.include_router(medical_router, prefix=settings.API_V1_STR)
if companion_router:
    app.include_router(companion_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "app_name": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "status": "online",
        "docs_url": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "CarePath AI Backend & Multi-Agent Engine",
        "version": "2.0.0"
    }
