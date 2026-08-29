"""Strict Pydantic Schemas for Patient Summary Generation."""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ocr import OCRResult, PrescriptionItem, LabMetricItem
from app.schemas.nlp import BioNERResult
from app.schemas.rag import RAGQueryResponse, DocumentChunk
from app.models.common import ClinicalTimelineEvent


class PatientOverview(BaseModel):
    """Patient demographic and clinical background context overview."""

    model_config = ConfigDict(extra="forbid")

    patient_id: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=150)
    gender: Optional[str] = None
    chief_complaint: Optional[str] = None
    summary_context: str = Field(
        min_length=1,
        description="High-level narrative overview of current patient presentation.",
    )


class MedicationSummaryItem(BaseModel):
    """Medication information exactly as extracted and verified from documents/notes."""

    model_config = ConfigDict(extra="forbid")

    drug_name: str = Field(min_length=1)
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    status: str = Field(default="REPORTED", description="REPORTED, ACTIVE, VERIFIED, DISCONTINUED")
    source: str = Field(default="clinical_notes", description="Origin of medication fact")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class LabFindingSummaryItem(BaseModel):
    """Laboratory test finding extracted from patient data."""

    model_config = ConfigDict(extra="forbid")

    test_name: str = Field(min_length=1)
    value: str = Field(min_length=1)
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    status: Optional[str] = Field(default=None, description="NORMAL, ABNORMAL, HIGH, LOW, CRITICAL")
    source: str = Field(default="lab_report", description="Origin of lab metric")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class TimelineEventSummaryItem(BaseModel):
    """Previous relevant clinical timeline event."""

    model_config = ConfigDict(extra="forbid")

    event_date: Optional[str] = None
    category: str = Field(default="GENERAL")
    title: str = Field(min_length=1)
    details: str = Field(default="")


class ExternalEvidenceItem(BaseModel):
    """RAG-retrieved external guideline evidence, cleanly separated from patient facts."""

    model_config = ConfigDict(extra="forbid")

    source_title: str = Field(min_length=1)
    excerpt: str = Field(min_length=1)
    relevance_score: float = Field(ge=0.0, le=1.0)
    citation: str = Field(min_length=1)
    guideline_id: Optional[str] = None


class FactVsInference(BaseModel):
    """Strict separation between facts, clinical observations, external evidence, and gaps."""

    model_config = ConfigDict(extra="forbid")

    directly_extracted_facts: List[str] = Field(
        default_factory=list,
        description="Directly extracted patient facts (verbatim symptoms, labs, meds, history).",
    )
    clinical_observations: List[str] = Field(
        default_factory=list,
        description="Clinically relevant observations derived solely from supplied patient data.",
    )
    external_guideline_evidence: List[str] = Field(
        default_factory=list,
        description="External guideline information retrieved via RAG (not patient facts).",
    )
    uncertainties_and_gaps: List[str] = Field(
        default_factory=list,
        description="Missing data, low confidence extractions, or unresolved uncertainties.",
    )


class SummaryConfidence(BaseModel):
    """Meaningful confidence indicator and uncertainty breakdown."""

    model_config = ConfigDict(extra="forbid")

    overall_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall summary confidence score based on data completeness and extraction quality.",
    )
    high_confidence_facts: List[str] = Field(default_factory=list)
    uncertain_extractions: List[str] = Field(default_factory=list)
    conflicting_information: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)


class PatientSummaryRequest(BaseModel):
    """Input payload to request a structured patient summary."""

    model_config = ConfigDict(extra="forbid")

    patient_id: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=150)
    gender: Optional[str] = None
    clinical_notes: Optional[str] = None
    document_ocr_results: List[OCRResult] = Field(default_factory=list)
    prescriptions: List[PrescriptionItem] = Field(default_factory=list)
    lab_metrics: List[LabMetricItem] = Field(default_factory=list)
    symptoms: List[str] = Field(default_factory=list)
    diagnoses: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    timeline_events: List[ClinicalTimelineEvent] = Field(default_factory=list)
    rag_evidence: Optional[RAGQueryResponse] = None
    include_rag: bool = True


class PatientSummaryReport(BaseModel):
    """Validated structured patient summary report."""

    model_config = ConfigDict(extra="forbid")

    overview: PatientOverview
    current_symptoms: List[str] = Field(default_factory=list)
    relevant_diagnoses: List[str] = Field(default_factory=list)
    current_medications: List[MedicationSummaryItem] = Field(default_factory=list)
    laboratory_findings: List[LabFindingSummaryItem] = Field(default_factory=list)
    previous_events: List[TimelineEventSummaryItem] = Field(default_factory=list)
    treatment_history: List[str] = Field(default_factory=list)
    recent_changes: List[str] = Field(default_factory=list)
    unresolved_issues: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    fact_vs_inference: FactVsInference
    evidence_references: List[ExternalEvidenceItem] = Field(default_factory=list)
    confidence_indicators: SummaryConfidence
    insufficient_information: bool = False
    data_sufficiency_notes: str = Field(default="Patient information is sufficient for navigation support.")
    disclaimer: str = Field(
        default=(
            "FOR CLINICIAN AND PATIENT NAVIGATION SUPPORT ONLY. "
            "THIS SUMMARY DOES NOT DIAGNOSE, PRESCRIBE, OR ALTER MEDICATIONS. "
            "ALL CLINICAL FINDINGS MUST BE INDEPENDENTLY VERIFIED BY A LICENSED HEALTHCARE PROVIDER."
        )
    )
    processing_time_seconds: float = Field(ge=0.0)
