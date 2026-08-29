"""Comprehensive Final AI Audit Test Suite (Sprints 1–4 Verification)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.clinical_extraction import ClinicalExtractionRequest
from app.schemas.patient_summary import PatientSummaryRequest
from app.schemas.case_questions import CaseQuestionRequest
from app.schemas.doctor_feedback import DoctorFeedbackRequest, DoctorStatementType
from app.schemas.treatment_response import TreatmentResponseRequest
from app.schemas.follow_up_intelligence import FollowUpIntelligenceRequest
from app.schemas.personalized_care_plan import PersonalizedCarePlanRequest, CarePlanCategory

from app.services.clinical_extraction_engine import clinical_extraction_engine
from app.services.patient_summary_engine import patient_summary_engine
from app.services.case_question_engine import case_question_engine
from app.services.doctor_feedback_engine import doctor_feedback_engine
from app.services.treatment_response_engine import treatment_response_engine
from app.services.follow_up_intelligence_engine import follow_up_intelligence_engine
from app.services.personalized_care_plan_engine import personalized_care_plan_engine

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Complete Multi-Module Pipeline End-to-End Audit
# ---------------------------------------------------------------------------

def test_full_pipeline_multi_module_integration():
    raw_clinical_note = (
        "Patient presents with fever 101F, severe productive cough, and shortness of breath for 3 days. "
        "Diagnosed with Acute Bronchitis. Prescribed Amoxicillin 500mg TID. Patient allergic to Sulfa."
    )

    # Step 1: Clinical Extraction
    ext_report = clinical_extraction_engine.extract_clinical_info(ClinicalExtractionRequest(clinical_text=raw_clinical_note))
    assert len(ext_report.symptoms) >= 2
    assert len(ext_report.medications) >= 1

    # Step 2: Patient Summary
    sum_report = patient_summary_engine.generate_summary(PatientSummaryRequest(clinical_notes=raw_clinical_note))
    assert sum_report.overview.summary_context != ""
    assert len(sum_report.current_medications) >= 1

    # Step 3: Case-Specific Question Generation
    q_report = case_question_engine.generate_questions(
        CaseQuestionRequest(
            symptoms=["Productive cough", "Shortness of breath"],
            medications=["Amoxicillin 500mg"],
            diagnoses=["Acute Bronchitis"],
        )
    )
    assert len(q_report.questions) >= 1

    # Step 4: Doctor Feedback Interpretation
    doctor_notes = "Assessment: Acute Bronchitis.\nDiscontinue Amoxicillin and start Ciprofloxacin 500mg.\nReview in 10 days."
    fb_report = doctor_feedback_engine.interpret_feedback(
        DoctorFeedbackRequest(doctor_notes=doctor_notes, existing_summary=sum_report)
    )
    assert len(fb_report.medications) >= 1
    assert fb_report.medications[0].statement_type == DoctorStatementType.DOCTOR_STATED
    assert len(fb_report.follow_up_instructions) >= 1

    # Step 5: Treatment Response Analysis
    trt_report = treatment_response_engine.analyze_treatment_response(
        TreatmentResponseRequest(
            treatment_events=[{"treatment_name": "Amoxicillin", "start_date": "Day 1"}],
            symptoms=[{"symptom_name": "Cough", "baseline_status": "Severe", "post_treatment_status": "Persisted"}],
        )
    )
    assert len(trt_report.analyzed_treatments) >= 1

    # Step 6: Follow-Up Intelligence
    fu_report = follow_up_intelligence_engine.analyze_follow_up(
        FollowUpIntelligenceRequest(
            doctor_feedback=doctor_notes,
            treatment_responses=[trt.model_dump() for trt in trt_report.analyzed_treatments],
        )
    )
    assert len(fu_report.follow_up_items) >= 1

    # Step 7: Personalized Care-Plan Generation
    cp_report = personalized_care_plan_engine.generate_care_plan(
        PersonalizedCarePlanRequest(
            patient_summary=sum_report.model_dump(),
            doctor_feedback={"doctor_notes": doctor_notes},
            treatment_responses=[trt.model_dump() for trt in trt_report.analyzed_treatments],
            follow_up_intelligence=fu_report.model_dump(),
        )
    )
    assert isinstance(cp_report.care_plan_items, list)
    assert len(cp_report.care_plan_items) >= 2


# ---------------------------------------------------------------------------
# 2. Fact vs Evidence vs Statement Type Separation Audit
# ---------------------------------------------------------------------------

def test_fact_evidence_statement_type_separation_audit():
    req = DoctorFeedbackRequest(
        doctor_notes="Assessment: Essential Hypertension.\nPatient reports mild headache.\nPrescribe Lisinopril 10mg.",
    )

    report = doctor_feedback_engine.interpret_feedback(req)

    doctor_stmts = [i for i in report.interpreted_items if i.statement_type == DoctorStatementType.DOCTOR_STATED]
    patient_stmts = [i for i in report.interpreted_items if i.statement_type == DoctorStatementType.PATIENT_REPORTED]

    assert len(doctor_stmts) >= 1
    assert len(patient_stmts) >= 1


# ---------------------------------------------------------------------------
# 3. Medical Safety & Prescribing Boundary Audit
# ---------------------------------------------------------------------------

def test_medical_safety_disclaimer_audit():
    # Verify all 4 major continuity engines contain non-prescriptive disclaimers
    sum_rep = patient_summary_engine.generate_summary(PatientSummaryRequest(clinical_notes="Notes"))
    fb_rep = doctor_feedback_engine.interpret_feedback(DoctorFeedbackRequest(doctor_notes="Notes"))
    trt_rep = treatment_response_engine.analyze_treatment_response(TreatmentResponseRequest())
    cp_rep = personalized_care_plan_engine.generate_care_plan(PersonalizedCarePlanRequest())

    assert "FOR CLINICIAN AND PATIENT NAVIGATION SUPPORT ONLY" in sum_rep.disclaimer
    assert "THIS SUBSYSTEM DOES NOT GENERATE AI PRESCRIPTIONS" in fb_rep.disclaimer
    assert "THIS SUBSYSTEM DESCRIBES DOCUMENTED OBSERVED OUTCOMES" in trt_rep.disclaimer
    assert "THIS CARE PLAN DOES NOT PRESCRIBE, CHANGE, OR STOP MEDICATIONS" in cp_rep.disclaimer
