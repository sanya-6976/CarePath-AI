"""Shared AI Domain Models Package.

These domain objects are the canonical representations used internally
across all CarePath AI modules (Vision, OCR, NLP, RAG, ClinicalIntelligence).
They are distinct from the FastAPI response schemas in ``app/schemas/`` which
represent the external API contract.
"""
from app.models.common import (
    PatientContext,
    ConfidenceScore,
    Evidence,
    MedicalEntityRecord,
    AIFinding,
    ClinicalInsight,
    EntityCategory,
    SeverityLevel,
    FindingType,
    InsightType,
)

__all__ = [
    "PatientContext",
    "ConfidenceScore",
    "Evidence",
    "MedicalEntityRecord",
    "AIFinding",
    "ClinicalInsight",
    "EntityCategory",
    "SeverityLevel",
    "FindingType",
    "InsightType",
]
