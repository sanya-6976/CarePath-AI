"""Differential Diagnosis and CarePath Synthesizer Schemas."""
from typing import List, Optional
from pydantic import BaseModel, Field


class DifferentialDiagnosis(BaseModel):
    condition: str
    probability: float
    reasoning: str
    icd10_code: Optional[str] = None


class CarePathStep(BaseModel):
    step_number: int
    timeframe: str = Field(description="e.g. Day 1-3, Week 2, Follow-up 1 month")
    action_type: str = Field(description="MEDICATION, DIAGNOSTIC_TEST, MONITORING, LIFESTYLE, SPECIALIST_REFERRAL")
    description: str
    urgency: str = Field(description="ROUTINE, URGENT, EMERGENCY")


class RiskAssessment(BaseModel):
    risk_level: str = Field(description="LOW, MODERATE, HIGH, CRITICAL")
    risk_score: float = Field(ge=0.0, le=100.0)
    risk_factors: List[str] = Field(default_factory=list)


class PatientCarePathSynthesis(BaseModel):
    patient_summary: str
    risk_assessment: RiskAssessment
    differential_diagnoses: List[DifferentialDiagnosis] = Field(default_factory=list)
    recommended_care_path: List[CarePathStep] = Field(default_factory=list)
    drug_interaction_alerts: List[str] = Field(default_factory=list)
    evidence_guidelines_used: List[str] = Field(default_factory=list)
    disclaimer: str = "FOR CLINICAL DECISION SUPPORT ONLY. ALL DIAGNOSES AND CARE PATHS MUST BE VERIFIED BY A LICENSED HEALTHCARE PROVIDER."
    processing_time_seconds: float
