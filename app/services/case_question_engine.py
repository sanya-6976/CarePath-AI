"""Production Case-Specific Question Generation Engine.

Generates targeted, clinically relevant questions for a doctor based strictly on
available patient data (summary, symptoms, labs, meds, history, timeline, gaps).
Enforces prompt safety, category validation, priority assignment, factual reasoning,
and deterministic deduplication.
"""

from __future__ import annotations

import re
import time
from typing import List, Optional, Set, Dict

from app.core.config import settings
from app.core.logging import get_logger
from app.core.interfaces import CaseQuestionService, ServiceHealthStatus, ServiceAvailability
from app.core.prompt_safety import sanitize_untrusted_text, detect_prompt_injection
from app.schemas.case_questions import (
    CaseQuestionRequest,
    CaseQuestionsReport,
    CaseSpecificQuestion,
    QuestionCategory,
    QuestionPriority,
)
from app.schemas.patient_summary import PatientSummaryReport
from app.schemas.ocr import PrescriptionItem, LabMetricItem
from app.schemas.nlp import BioNERResult
from app.models.common import ClinicalTimelineEvent
from app.services.nlp_engine import nlp_engine

logger = get_logger(__name__)


def _normalize_question_text(text: str) -> str:
    """Normalize question text for deduplication comparison."""
    return re.sub(r"[^\w\s]", "", text.lower()).strip()


class CaseQuestionEngine(CaseQuestionService):
    """Engine for generating validated case-specific questions for clinical review."""

    _SERVICE_NAME = "CarePath Case-Specific Question Engine"
    _SERVICE_VERSION = "0.1.0"

    def health_check(self) -> ServiceHealthStatus:
        """Return the readiness status of the question engine."""
        nlp_health = nlp_engine.health_check()
        if not nlp_health.is_ok:
            return ServiceHealthStatus(
                availability=ServiceAvailability.DEGRADED,
                backend="case_question_engine",
                message="NLP sub-engine running in degraded mode.",
            )
        return ServiceHealthStatus(
            availability=ServiceAvailability.AVAILABLE,
            backend="case_question_engine",
            message="Case-specific question engine is fully operational.",
        )

    def get_service_info(self) -> dict:
        """Return engine metadata."""
        return {
            "name": self._SERVICE_NAME,
            "version": self._SERVICE_VERSION,
            "status": self.health_check().availability.value,
        }

    def generate_questions(self, request: CaseQuestionRequest) -> CaseQuestionsReport:
        """Generate targeted, case-specific clinical questions."""
        start_time = time.time()

        # 1. Sanitize Untrusted Inputs
        clinical_notes_clean = sanitize_untrusted_text(request.clinical_notes) if request.clinical_notes else ""
        has_injection, injection_types = False, []
        if request.clinical_notes:
            has_injection, injection_types = detect_prompt_injection(request.clinical_notes)
            if has_injection:
                logger.warning("Prompt injection detected in case question request: %s", injection_types)

        # 2. Extract NLP Entities if raw text provided
        nlp_result: Optional[BioNERResult] = None
        if clinical_notes_clean:
            try:
                nlp_result = nlp_engine.extract_entities(clinical_notes_clean)
            except Exception as e:
                logger.error("NLP extraction failed in question engine: %s", e)

        # 3. Consolidate Clinical Data
        symptoms_set: Set[str] = set(request.symptoms)
        diagnoses_set: Set[str] = set(request.diagnoses)
        medications_set: Set[str] = set(request.medications)
        lab_metrics_list: List[LabMetricItem] = list(request.lab_metrics)
        prescriptions_list: List[PrescriptionItem] = list(request.prescriptions)
        timeline_events_list: List[ClinicalTimelineEvent] = list(request.timeline_events)
        missing_info_set: Set[str] = set(request.missing_information)
        conflicting_info_list: List[str] = []

        # From PatientSummaryReport if provided
        if request.patient_summary:
            ps = request.patient_summary
            for s in ps.current_symptoms:
                symptoms_set.add(s)
            for d in ps.relevant_diagnoses:
                diagnoses_set.add(d)
            for m in ps.current_medications:
                medications_set.add(m.drug_name)
                if m.dosage:
                    prescriptions_list.append(PrescriptionItem(drug_name=m.drug_name, dosage=m.dosage, frequency=m.frequency))
            for l in ps.laboratory_findings:
                lab_metrics_list.append(LabMetricItem(test_name=l.test_name, value=l.value, unit=l.unit, status=l.status))
            for te in ps.previous_events:
                timeline_events_list.append(ClinicalTimelineEvent(event_date=te.event_date, category=te.category, title=te.title, details=te.details))
            for mi in ps.missing_information:
                missing_info_set.add(mi)
            for conflict in ps.confidence_indicators.conflicting_information:
                conflicting_info_list.append(conflict)

        # From NLP result
        if nlp_result:
            for s in nlp_result.symptoms:
                symptoms_set.add(s)
            for d in nlp_result.diagnoses:
                diagnoses_set.add(d)
            for m in nlp_result.medications:
                medications_set.add(m)

        for p in prescriptions_list:
            medications_set.add(p.drug_name)

        symptoms_list = sorted(list(symptoms_set))
        diagnoses_list = sorted(list(diagnoses_set))
        medications_list = sorted(list(medications_set))
        missing_info_list = sorted(list(missing_info_set))

        # Check total data availability
        total_data_points = (
            len(symptoms_list) + len(diagnoses_list) + len(medications_list) +
            len(lab_metrics_list) + len(timeline_events_list) + (1 if clinical_notes_clean else 0)
        )

        if total_data_points == 0:
            return CaseQuestionsReport(
                questions=[],
                total_question_count=0,
                source_context_summary="No patient data or clinical records were supplied.",
                data_completeness="INSUFFICIENT",
                insufficient_data=True,
                processing_time_seconds=round(time.time() - start_time, 3),
            )

        # 4. Generate Candidate Case-Specific Questions
        raw_questions: List[CaseSpecificQuestion] = []

        # (A) Symptom Clarifications
        severe_keywords = {"chest pain", "shortness of breath", "dyspnea", "fever", "hemoptysis", "syncope", "seizure", "severe"}
        for symptom in symptoms_list:
            sym_lower = symptom.lower()
            is_severe = any(k in sym_lower for k in severe_keywords)
            priority = QuestionPriority.HIGH if is_severe else QuestionPriority.MEDIUM

            question_text = f"When did the {symptom} first start, and has it changed in severity or frequency?"
            reason_text = f"The patient record documents active symptom '{symptom}' without detailed onset or progression history."
            supporting_info = [f"Symptom: {symptom}"]
            conf_score = 0.95 if is_severe else 0.88
            if has_injection:
                conf_score -= 0.10

            raw_questions.append(
                CaseSpecificQuestion(
                    question=question_text,
                    category=QuestionCategory.SYMPTOM_CLARIFICATION,
                    priority=priority,
                    reason=reason_text,
                    supporting_information=supporting_info,
                    confidence=round(conf_score, 2),
                )
            )

            if is_severe:
                raw_questions.append(
                    CaseSpecificQuestion(
                        question=f"Are there any specific aggravating or relieving factors for the {symptom}?",
                        category=QuestionCategory.SYMPTOM_CLARIFICATION,
                        priority=QuestionPriority.HIGH,
                        reason=f"High-priority symptom '{symptom}' requires clarification of triggering or alleviating factors.",
                        supporting_information=[f"Acute Symptom: {symptom}"],
                        confidence=0.92,
                    )
                )

        # (B) Medication & Treatment Response
        for med in medications_list:
            # Check dosage
            pres_match = next((p for p in prescriptions_list if p.drug_name.lower() == med.lower()), None)
            dosage_str = pres_match.dosage if pres_match and pres_match.dosage else None

            if dosage_str:
                raw_questions.append(
                    CaseSpecificQuestion(
                        question=f"Is the patient taking {med} {dosage_str} regularly as prescribed, and have any side effects been reported?",
                        category=QuestionCategory.TREATMENT_RESPONSE,
                        priority=QuestionPriority.HIGH if symptoms_list else QuestionPriority.MEDIUM,
                        reason=f"Patient is documented on {med} ({dosage_str}); evaluating adherence and clinical response is critical.",
                        supporting_information=[f"Medication: {med} {dosage_str}"],
                        confidence=0.90,
                    )
                )
            else:
                raw_questions.append(
                    CaseSpecificQuestion(
                        question=f"What is the exact dosage, frequency, and duration for medication {med}?",
                        category=QuestionCategory.MEDICATION,
                        priority=QuestionPriority.HIGH,
                        reason=f"Medication '{med}' is listed in the patient record without explicit dosage instructions.",
                        supporting_information=[f"Medication: {med}"],
                        confidence=0.93,
                    )
                )

            if symptoms_list:
                raw_questions.append(
                    CaseSpecificQuestion(
                        question=f"Has the symptom of {symptoms_list[0]} improved or worsened since starting or taking {med}?",
                        category=QuestionCategory.TREATMENT_RESPONSE,
                        priority=QuestionPriority.HIGH,
                        reason=f"Patient is taking '{med}' while presenting with '{symptoms_list[0]}'.",
                        supporting_information=[f"Medication: {med}", f"Symptom: {symptoms_list[0]}"],
                        confidence=0.89,
                    )
                )

        # (C) Lab Finding Clarification
        for lab in lab_metrics_list:
            is_abnormal = lab.status and lab.status.upper() in ("ABNORMAL", "HIGH", "LOW", "CRITICAL")
            priority = QuestionPriority.HIGH if is_abnormal else QuestionPriority.MEDIUM

            question_text = f"What is the clinical correlation for the {lab.test_name} result of {lab.value}{' ' + lab.unit if lab.unit else ''}?"
            reason_text = f"Laboratory finding '{lab.test_name}' is recorded as {lab.value}{' ' + lab.unit if lab.unit else ''} ({lab.status or 'value reported'})."
            supporting_info = [f"Lab Result: {lab.test_name} = {lab.value}{' ' + lab.unit if lab.unit else ''}"]

            raw_questions.append(
                CaseSpecificQuestion(
                    question=question_text,
                    category=QuestionCategory.LAB_FINDING,
                    priority=priority,
                    reason=reason_text,
                    supporting_information=supporting_info,
                    confidence=0.94 if is_abnormal else 0.85,
                )
            )

        # (D) Diagnosis & Timeline Clarifications
        for diagnosis in diagnoses_list:
            raw_questions.append(
                CaseSpecificQuestion(
                    question=f"When was {diagnosis} officially diagnosed, and is it currently managed by a specialist?",
                    category=QuestionCategory.DIAGNOSIS_CLARIFICATION,
                    priority=QuestionPriority.MEDIUM,
                    reason=f"Documented diagnosis '{diagnosis}' requires confirmation of onset and current clinical management status.",
                    supporting_information=[f"Diagnosis: {diagnosis}"],
                    confidence=0.87,
                )
            )

        for te in timeline_events_list:
            raw_questions.append(
                CaseSpecificQuestion(
                    question=f"What clinical progress or changes have occurred since the event '{te.title}' recorded on {te.event_date or 'recent visit'}?",
                    category=QuestionCategory.TIMELINE,
                    priority=QuestionPriority.MEDIUM,
                    reason=f"Historical timeline event '{te.title}' ({te.event_date or 'undated'}) needs follow-up assessment.",
                    supporting_information=[f"Timeline Event: {te.title} ({te.event_date or 'undated'})"],
                    confidence=0.86,
                )
            )

        # (E) Missing Information Gaps
        for gap in missing_info_list:
            raw_questions.append(
                CaseSpecificQuestion(
                    question=f"Can you clarify the missing clinical information regarding: {gap}?",
                    category=QuestionCategory.MISSING_INFORMATION,
                    priority=QuestionPriority.HIGH if "medication" in gap.lower() or "allergy" in gap.lower() else QuestionPriority.MEDIUM,
                    reason=f"The patient record explicitly identifies missing information gap: '{gap}'.",
                    supporting_information=[f"Missing Info Gap: {gap}"],
                    confidence=0.91,
                )
            )

        # (F) Conflicting Information Resolution
        for conflict in conflicting_info_list:
            raw_questions.append(
                CaseSpecificQuestion(
                    question=f"Please resolve the conflicting record entry: {conflict}",
                    category=QuestionCategory.MEDICATION if "dosage" in conflict.lower() or "medication" in conflict.lower() else QuestionCategory.DIAGNOSIS_CLARIFICATION,
                    priority=QuestionPriority.HIGH,
                    reason=f"Discrepancy detected in patient record: {conflict}",
                    supporting_information=[f"Conflict: {conflict}"],
                    confidence=0.96,
                )
            )

        # (G) General Follow-Up (only if data is minimal)
        if len(raw_questions) == 0 and total_data_points > 0:
            raw_questions.append(
                CaseSpecificQuestion(
                    question="What primary symptoms or health concerns prompted this visit?",
                    category=QuestionCategory.FOLLOW_UP,
                    priority=QuestionPriority.MEDIUM,
                    reason="Initial presentation data is brief and requires baseline clarification.",
                    supporting_information=["General Presentation"],
                    confidence=0.80,
                )
            )

        # 5. Quality Control: Deduplication, Specificity Filtering, Priority Sorting
        seen_normalized: Set[str] = set()
        unique_questions: List[CaseSpecificQuestion] = []

        # Generic question phrases to reject unless grounded in specific data
        forbidden_generic_phrases = [
            "how are you feeling",
            "any other symptoms",
            "tell me how you feel",
            "what brings you in today without details",
        ]

        for q in raw_questions:
            norm_q = _normalize_question_text(q.question)
            # Filter generic unanchored questions
            if any(g in norm_q for g in forbidden_generic_phrases):
                continue
            if norm_q in seen_normalized:
                continue
            seen_normalized.add(norm_q)
            unique_questions.append(q)

        # Priority Sort: HIGH -> MEDIUM -> LOW, then by confidence descending
        priority_map = {QuestionPriority.HIGH: 0, QuestionPriority.MEDIUM: 1, QuestionPriority.LOW: 2}
        unique_questions.sort(key=lambda q: (priority_map[q.priority], -q.confidence))

        # Truncate to max_questions
        final_questions = unique_questions[: request.max_questions]

        context_summary = (
            f"Case analysis of {len(symptoms_list)} symptoms, {len(diagnoses_list)} diagnoses, "
            f"{len(medications_list)} medications, {len(lab_metrics_list)} lab metrics, and {len(timeline_events_list)} timeline events."
        )

        data_completeness = "COMPLETE" if len(missing_info_list) == 0 else "PARTIAL"

        return CaseQuestionsReport(
            questions=final_questions,
            total_question_count=len(final_questions),
            source_context_summary=context_summary,
            data_completeness=data_completeness,
            insufficient_data=False,
            processing_time_seconds=round(time.time() - start_time, 3),
        )


case_question_engine = CaseQuestionEngine()
