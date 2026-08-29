"""Tests for Shared AI Domain Models (app/models/common.py).

Validates:
- Field constraints enforced at construction time (Pydantic validators).
- Enum values are valid and reject unknown strings.
- Frozen / immutable config prevents post-construction mutation.
- Optional fields default correctly.
"""
import pytest
from pydantic import ValidationError

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


# ---------------------------------------------------------------------------
# PatientContext
# ---------------------------------------------------------------------------

class TestPatientContext:

    def test_all_fields_optional(self):
        ctx = PatientContext()
        assert ctx.patient_id is None
        assert ctx.age is None
        assert ctx.gender is None
        assert ctx.chief_complaint is None
        assert ctx.relevant_history is None

    def test_valid_full_construction(self):
        ctx = PatientContext(
            patient_id="PT-001",
            age=45,
            gender="Female",
            chief_complaint="Cough and fever for 3 days.",
            relevant_history="No known allergies.",
        )
        assert ctx.age == 45
        assert ctx.patient_id == "PT-001"

    def test_age_lower_bound(self):
        ctx = PatientContext(age=0)
        assert ctx.age == 0

    def test_age_upper_bound(self):
        ctx = PatientContext(age=150)
        assert ctx.age == 150

    def test_age_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            PatientContext(age=151)

    def test_age_negative_raises(self):
        with pytest.raises(ValidationError):
            PatientContext(age=-1)

    def test_frozen_prevents_mutation(self):
        ctx = PatientContext(age=30)
        with pytest.raises(Exception):  # ValidationError or TypeError depending on Pydantic version
            ctx.age = 31  # type: ignore[misc]


# ---------------------------------------------------------------------------
# ConfidenceScore
# ---------------------------------------------------------------------------

class TestConfidenceScore:

    def test_valid_score(self):
        cs = ConfidenceScore(value=0.88, method="neural")
        assert cs.value == 0.88
        assert cs.method == "neural"
        assert cs.calibrated is False

    def test_boundary_values(self):
        assert ConfidenceScore(value=0.0).value == 0.0
        assert ConfidenceScore(value=1.0).value == 1.0

    def test_above_one_raises(self):
        with pytest.raises(ValidationError):
            ConfidenceScore(value=1.001)

    def test_below_zero_raises(self):
        with pytest.raises(ValidationError):
            ConfidenceScore(value=-0.001)

    def test_value_rounded_to_4dp(self):
        cs = ConfidenceScore(value=0.123456789)
        assert cs.value == round(0.123456789, 4)

    def test_calibrated_flag(self):
        cs = ConfidenceScore(value=0.75, calibrated=True)
        assert cs.calibrated is True


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------

class TestEvidence:

    def test_valid_construction(self):
        ev = Evidence(
            source="ATS/IDSA Guidelines 2024",
            content="Amoxicillin 1g TID is recommended for CAP.",
            relevance_score=0.92,
            citation="ATS/IDSA Clin Infect Dis. 2024",
        )
        assert ev.source == "ATS/IDSA Guidelines 2024"
        assert ev.relevance_score == 0.92

    def test_optional_citation(self):
        ev = Evidence(
            source="Medical Reference",
            content="Some clinical content.",
            relevance_score=0.5,
        )
        assert ev.citation is None

    def test_empty_source_raises(self):
        with pytest.raises(ValidationError):
            Evidence(source="", content="content", relevance_score=0.5)

    def test_relevance_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            Evidence(source="src", content="text", relevance_score=1.5)


# ---------------------------------------------------------------------------
# MedicalEntityRecord
# ---------------------------------------------------------------------------

class TestMedicalEntityRecord:

    def test_valid_entity(self):
        entity = MedicalEntityRecord(
            text="pneumonia",
            category=EntityCategory.DIAGNOSIS,
            icd10_code="J18.9",
            confidence=ConfidenceScore(value=0.95),
        )
        assert entity.text == "pneumonia"
        assert entity.category == EntityCategory.DIAGNOSIS
        assert entity.negated is False

    def test_negated_entity(self):
        entity = MedicalEntityRecord(
            text="chest pain",
            category=EntityCategory.SYMPTOM,
            negated=True,
            confidence=ConfidenceScore(value=0.90),
        )
        assert entity.negated is True

    def test_snomed_optional(self):
        entity = MedicalEntityRecord(
            text="lung",
            category=EntityCategory.ANATOMY,
            confidence=ConfidenceScore(value=0.80),
        )
        assert entity.snomed_ct is None
        assert entity.icd10_code is None

    def test_invalid_category_raises(self):
        with pytest.raises(ValidationError):
            MedicalEntityRecord(
                text="aspirin",
                category="INVALID_CATEGORY",  # type: ignore[arg-type]
                confidence=ConfidenceScore(value=0.9),
            )


# ---------------------------------------------------------------------------
# AIFinding
# ---------------------------------------------------------------------------

class TestAIFinding:

    def _make_evidence(self) -> Evidence:
        return Evidence(source="Test", content="test content", relevance_score=0.8)

    def test_valid_finding(self):
        finding = AIFinding(
            finding_type=FindingType.IMAGING,
            description="Consolidation in left lower lobe.",
            confidence=ConfidenceScore(value=0.88),
            severity=SeverityLevel.MODERATE,
            supporting_evidence=[self._make_evidence()],
        )
        assert finding.finding_type == FindingType.IMAGING
        assert finding.severity == SeverityLevel.MODERATE
        assert len(finding.supporting_evidence) == 1

    def test_default_severity(self):
        finding = AIFinding(
            finding_type=FindingType.CLINICAL_NLP,
            description="Normal clinical assessment.",
            confidence=ConfidenceScore(value=0.94),
        )
        assert finding.severity == SeverityLevel.NORMAL

    def test_empty_evidence_list(self):
        finding = AIFinding(
            finding_type=FindingType.OCR_EXTRACTED,
            description="Hemoglobin 14.5 g/dL.",
            confidence=ConfidenceScore(value=0.92),
        )
        assert finding.supporting_evidence == []


# ---------------------------------------------------------------------------
# ClinicalInsight
# ---------------------------------------------------------------------------

class TestClinicalInsight:

    def test_valid_insight(self):
        insight = ClinicalInsight(
            insight_type=InsightType.DIFFERENTIAL_DIAGNOSIS,
            summary="Community-acquired pneumonia is the primary diagnosis.",
            recommendations=["Start amoxicillin 1g TID.", "Monitor SpO2."],
            confidence=ConfidenceScore(value=0.82),
        )
        assert insight.insight_type == InsightType.DIFFERENTIAL_DIAGNOSIS
        assert len(insight.recommendations) == 2
        assert "CLINICAL DECISION SUPPORT" in insight.disclaimer

    def test_empty_recommendations_allowed(self):
        insight = ClinicalInsight(
            insight_type=InsightType.RISK_STRATIFICATION,
            summary="Low risk patient.",
            confidence=ConfidenceScore(value=0.96),
        )
        assert insight.recommendations == []

    def test_default_disclaimer_present(self):
        insight = ClinicalInsight(
            insight_type=InsightType.CARE_PATH,
            summary="Follow-up in 1 week.",
            confidence=ConfidenceScore(value=0.75),
        )
        assert len(insight.disclaimer) > 10
