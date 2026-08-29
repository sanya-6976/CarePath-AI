"""Strict Pydantic Schemas for Clinical Information Extraction."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ocr import OCRResult, PrescriptionItem, LabMetricItem
from app.schemas.patient_summary import PatientSummaryReport


class ClinicalSourceType(str, Enum):
    """Origin source category for extracted clinical facts."""

    OCR = "OCR"
    PRESCRIPTION = "PRESCRIPTION"
    MEDICAL_REPORT = "MEDICAL_REPORT"
    CLINICAL_NOTE = "CLINICAL_NOTE"
    PATIENT_INPUT = "PATIENT_INPUT"
    DOCTOR_INPUT = "DOCTOR_INPUT"


class FactType(str, Enum):
    """Categorization distinguishing explicit facts from inferences or uncertainties."""

    EXPLICIT_FACT = "EXPLICIT_FACT"
    INFERRED_INFORMATION = "INFERRED_INFORMATION"
    UNCERTAIN_INFORMATION = "UNCERTAIN_INFORMATION"
    CONFLICTING_INFORMATION = "CONFLICTING_INFORMATION"


class ExtractedTemporalEvent(BaseModel):
    """Explicit temporal expression and context associated with a clinical entity or event."""

    model_config = ConfigDict(extra="forbid")

    event_name: str = Field(min_length=1)
    temporal_expression: str = Field(min_length=1, description="Raw expression e.g. 'for 3 days', 'started yesterday', 'in 2024'")
    normalized_duration: Optional[str] = Field(default=None, description="ISO-8601 duration or normalized representation e.g. 'P3D'")
    relationship: str = Field(default="DURATION", description="ONSET, DURATION, HISTORICAL_DATE, FREQUENCY")


class ExtractedMedicationFact(BaseModel):
    """Structured medication fact extracted with explicit source attribution and dosage info."""

    model_config = ConfigDict(extra="forbid")

    drug_name: str = Field(min_length=1)
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    route: Optional[str] = None
    negated: bool = False
    status: str = Field(default="REPORTED", description="REPORTED, ACTIVE, DISCONTINUED, VERIFIED")
    source_type: ClinicalSourceType = Field(default=ClinicalSourceType.CLINICAL_NOTE)
    source_snippet: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class ExtractedLabFact(BaseModel):
    """Structured laboratory test finding extracted with source traceability."""

    model_config = ConfigDict(extra="forbid")

    test_name: str = Field(min_length=1)
    value: str = Field(min_length=1)
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    status: Optional[str] = Field(default=None, description="NORMAL, ABNORMAL, HIGH, LOW, CRITICAL")
    source_type: ClinicalSourceType = Field(default=ClinicalSourceType.MEDICAL_REPORT)
    source_snippet: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class ExtractedProcedureFact(BaseModel):
    """Medical procedure or diagnostic test finding extracted from patient data."""

    model_config = ConfigDict(extra="forbid")

    procedure_name: str = Field(min_length=1)
    procedure_date: Optional[str] = None
    status: Optional[str] = Field(default="COMPLETED")
    source_type: ClinicalSourceType = Field(default=ClinicalSourceType.CLINICAL_NOTE)
    source_snippet: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class ExtractedClinicalEntity(BaseModel):
    """A generic extracted clinical entity with negation, body site, temporal context, and source traceability."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    normalized_text: Optional[str] = None
    category: str = Field(description="SYMPTOM, DIAGNOSIS, ALLERGY, HISTORY, FAMILY_HISTORY, ANATOMY, PROCEDURE, LAB_METRIC, MEDICATION")
    fact_type: FactType = Field(default=FactType.EXPLICIT_FACT)
    negated: bool = Field(default=False)
    body_site: Optional[str] = Field(default=None, description="Associated anatomical location e.g. 'left lower lung'")
    temporal_context: Optional[ExtractedTemporalEvent] = None
    source_type: ClinicalSourceType = Field(default=ClinicalSourceType.CLINICAL_NOTE)
    source_snippet: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class ClinicalConflictRecord(BaseModel):
    """Explicit cross-source conflict representation."""

    model_config = ConfigDict(extra="forbid")

    conflicting_topic: str = Field(min_length=1)
    source_statement_a: str = Field(min_length=1)
    source_statement_b: str = Field(min_length=1)
    source_a_type: ClinicalSourceType
    source_b_type: ClinicalSourceType
    uncertainty_description: str = Field(min_length=1)


class ClinicalExtractionRequest(BaseModel):
    """Input payload to request comprehensive clinical information extraction."""

    model_config = ConfigDict(extra="forbid")

    clinical_text: Optional[str] = None
    ocr_results: List[OCRResult] = Field(default_factory=list)
    prescriptions: List[PrescriptionItem] = Field(default_factory=list)
    lab_metrics: List[LabMetricItem] = Field(default_factory=list)
    existing_summary: Optional[PatientSummaryReport] = None
    default_source_type: ClinicalSourceType = Field(default=ClinicalSourceType.CLINICAL_NOTE)
    document_filename: Optional[str] = None


class ClinicalExtractionReport(BaseModel):
    """Master validated output report containing extracted clinical entities, facts, and relationships."""

    model_config = ConfigDict(extra="forbid")

    entities: List[ExtractedClinicalEntity] = Field(default_factory=list)
    symptoms: List[ExtractedClinicalEntity] = Field(default_factory=list)
    diagnoses: List[ExtractedClinicalEntity] = Field(default_factory=list)
    medications: List[ExtractedMedicationFact] = Field(default_factory=list)
    laboratory_findings: List[ExtractedLabFact] = Field(default_factory=list)
    procedures: List[ExtractedProcedureFact] = Field(default_factory=list)
    allergies: List[ExtractedClinicalEntity] = Field(default_factory=list)
    history_items: List[ExtractedClinicalEntity] = Field(default_factory=list)
    temporal_events: List[ExtractedTemporalEvent] = Field(default_factory=list)
    conflicts: List[ClinicalConflictRecord] = Field(default_factory=list)
    uncertain_information: List[str] = Field(default_factory=list)
    source_references: List[str] = Field(default_factory=list)
    overall_confidence: float = Field(ge=0.0, le=1.0)
    processing_time_seconds: float = Field(ge=0.0)
