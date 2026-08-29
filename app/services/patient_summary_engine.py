"""Production Patient Summary Generation Engine.

Synthesizes multi-modal patient data into a structured, validated PatientSummaryReport.
Handles missing inputs, prompt injection, fact vs inference separation, medical safety,
RAG evidence separation, and deterministic confidence scoring.
"""

from __future__ import annotations

import time
from typing import List, Optional, Set, Dict

from app.core.config import settings
from app.core.logging import get_logger
from app.core.interfaces import PatientSummaryService, ServiceHealthStatus, ServiceAvailability
from app.core.prompt_safety import sanitize_untrusted_text, detect_prompt_injection
from app.schemas.patient_summary import (
    PatientSummaryRequest,
    PatientSummaryReport,
    PatientOverview,
    MedicationSummaryItem,
    LabFindingSummaryItem,
    TimelineEventSummaryItem,
    ExternalEvidenceItem,
    FactVsInference,
    SummaryConfidence,
)
from app.schemas.ocr import OCRResult, PrescriptionItem, LabMetricItem
from app.schemas.nlp import BioNERResult
from app.schemas.rag import RAGQueryResponse
from app.services.nlp_engine import nlp_engine
from app.services.rag_engine import rag_engine

logger = get_logger(__name__)


class PatientSummaryEngine(PatientSummaryService):
    """Engine responsible for building validated, safe, structured patient summaries."""

    _SERVICE_NAME = "CarePath Patient Summary Engine"
    _SERVICE_VERSION = "0.1.0"

    def health_check(self) -> ServiceHealthStatus:
        """Return the readiness state of the summary engine and dependent sub-engines."""
        nlp_health = nlp_engine.health_check()
        rag_health = rag_engine.health_check()

        if not nlp_health.is_ok or not rag_health.is_ok:
            return ServiceHealthStatus(
                availability=ServiceAvailability.DEGRADED,
                backend="patient_summary_engine",
                message="Sub-engine(s) running in degraded mode.",
            )
        return ServiceHealthStatus(
            availability=ServiceAvailability.AVAILABLE,
            backend="patient_summary_engine",
            message="Patient summary engine is fully operational.",
        )

    def get_service_info(self) -> dict:
        """Return service metadata."""
        return {
            "name": self._SERVICE_NAME,
            "version": self._SERVICE_VERSION,
            "status": self.health_check().availability.value,
        }

    def generate_summary(self, request: PatientSummaryRequest) -> PatientSummaryReport:
        """Generate a validated structured patient summary from multi-modal inputs."""
        start_time = time.time()

        # 1. Sanitize Untrusted Inputs
        clinical_notes_clean = sanitize_untrusted_text(request.clinical_notes) if request.clinical_notes else ""
        
        # Check prompt injection flags
        has_injection, injection_types = False, []
        if request.clinical_notes:
            has_injection, injection_types = detect_prompt_injection(request.clinical_notes)
            if has_injection:
                logger.warning("Prompt injection attempt detected in clinical notes: %s", injection_types)

        # 2. Ingest NLP Entities from Clinical Notes
        nlp_result: Optional[BioNERResult] = None
        if clinical_notes_clean:
            try:
                nlp_result = nlp_engine.extract_entities(clinical_notes_clean)
            except Exception as e:
                logger.error("Failed to extract NLP entities in summary engine: %s", e)

        # 3. Aggregate Symptoms, Diagnoses, Medications, Lab Findings, Timeline Events
        symptoms_set: Set[str] = set(request.symptoms)
        diagnoses_set: Set[str] = set(request.diagnoses)
        medications_map: Dict[str, MedicationSummaryItem] = {}
        lab_findings_list: List[LabFindingSummaryItem] = []
        previous_events_list: List[TimelineEventSummaryItem] = []
        
        extracted_facts: List[str] = []
        conflicting_info: List[str] = []
        uncertain_extractions: List[str] = []
        high_confidence_facts: List[str] = []
        missing_info: List[str] = []

        if has_injection:
            uncertain_extractions.append(f"Prompt injection patterns detected ({', '.join(injection_types)}) and neutralized as non-executable text.")

        # From NLP
        if nlp_result:
            for s in nlp_result.symptoms:
                symptoms_set.add(s)
                extracted_facts.append(f"Reported symptom: {s}")
                high_confidence_facts.append(f"Symptom: {s}")
            for d in nlp_result.diagnoses:
                diagnoses_set.add(d)
                extracted_facts.append(f"Documented diagnosis: {d}")
                high_confidence_facts.append(f"Diagnosis: {d}")
            for m in nlp_result.medications:
                med_key = m.lower().strip()
                if med_key not in medications_map:
                    medications_map[med_key] = MedicationSummaryItem(
                        drug_name=m,
                        status="REPORTED",
                        source="clinical_notes",
                        confidence=nlp_result.overall_confidence,
                    )
                    extracted_facts.append(f"Reported medication: {m}")

            for inst in nlp_result.medication_instructions:
                med_key = inst.medication.lower().strip()
                medications_map[med_key] = MedicationSummaryItem(
                    drug_name=inst.medication,
                    dosage=inst.dosage,
                    frequency=inst.frequency,
                    duration=inst.duration,
                    status="REPORTED",
                    source="clinical_notes_instructions",
                    confidence=inst.confidence,
                )

        # From explicit Request parameters
        for med in request.medications:
            med_key = med.lower().strip()
            if med_key not in medications_map:
                medications_map[med_key] = MedicationSummaryItem(
                    drug_name=med,
                    status="VERIFIED",
                    source="structured_input",
                    confidence=1.0,
                )
                extracted_facts.append(f"Verified medication: {med}")
                high_confidence_facts.append(f"Medication: {med}")

        for pres in request.prescriptions:
            med_key = pres.drug_name.lower().strip()
            if med_key in medications_map and medications_map[med_key].dosage and pres.dosage and medications_map[med_key].dosage != pres.dosage:
                conflict_msg = f"Conflicting dosage for {pres.drug_name}: '{medications_map[med_key].dosage}' vs prescription '{pres.dosage}'"
                conflicting_info.append(conflict_msg)
                logger.warning(conflict_msg)

            medications_map[med_key] = MedicationSummaryItem(
                drug_name=pres.drug_name,
                dosage=pres.dosage,
                frequency=pres.frequency,
                duration=pres.duration,
                status="ACTIVE",
                source="prescription_document",
                confidence=1.0,
            )
            extracted_facts.append(f"Prescribed medication: {pres.drug_name} {pres.dosage or ''}".strip())
            high_confidence_facts.append(f"Prescription: {pres.drug_name}")

        for lab in request.lab_metrics:
            lab_item = LabFindingSummaryItem(
                test_name=lab.test_name,
                value=lab.value,
                unit=lab.unit,
                reference_range=lab.reference_range,
                status=lab.status or ("ABNORMAL" if lab.status else "NORMAL"),
                source="lab_report",
                confidence=1.0,
            )
            lab_findings_list.append(lab_item)
            extracted_facts.append(f"Lab metric: {lab.test_name} = {lab.value} {lab.unit or ''}".strip())
            high_confidence_facts.append(f"Lab: {lab.test_name}")

        # From OCR Results
        low_ocr_confidence = False
        for ocr_res in request.document_ocr_results:
            clean_ocr_text = sanitize_untrusted_text(ocr_res.raw_text)
            if ocr_res.confidence_score < 0.60:
                low_ocr_confidence = True
                uncertain_extractions.append(f"Low OCR confidence ({ocr_res.confidence_score:.2f}) on document '{ocr_res.filename}'.")

            for pres in ocr_res.prescriptions:
                med_key = pres.drug_name.lower().strip()
                medications_map[med_key] = MedicationSummaryItem(
                    drug_name=pres.drug_name,
                    dosage=pres.dosage,
                    frequency=pres.frequency,
                    duration=pres.duration,
                    status="VERIFIED",
                    source=f"ocr_{ocr_res.filename}",
                    confidence=ocr_res.confidence_score,
                )
                extracted_facts.append(f"OCR prescription: {pres.drug_name} from {ocr_res.filename}")

            for lab in ocr_res.lab_metrics:
                lab_item = LabFindingSummaryItem(
                    test_name=lab.test_name,
                    value=lab.value,
                    unit=lab.unit,
                    reference_range=lab.reference_range,
                    status=lab.status,
                    source=f"ocr_{ocr_res.filename}",
                    confidence=ocr_res.confidence_score,
                )
                lab_findings_list.append(lab_item)
                extracted_facts.append(f"OCR lab: {lab.test_name} = {lab.value} from {ocr_res.filename}")

        # From Timeline Events
        for te in request.timeline_events:
            event_item = TimelineEventSummaryItem(
                event_date=te.event_date,
                category=te.category,
                title=te.title,
                details=te.details,
            )
            previous_events_list.append(event_item)
            extracted_facts.append(f"Timeline event [{te.event_date or 'Undated'}]: {te.title}")

        # 4. Check Missing Information & Data Sufficiency
        symptoms_list = sorted(list(symptoms_set))
        diagnoses_list = sorted(list(diagnoses_set))
        medications_list = list(medications_map.values())

        if not medications_list:
            missing_info.append("No active or past medication history supplied.")
        if not lab_findings_list:
            missing_info.append("No laboratory reports or objective diagnostic test values supplied.")
        if not previous_events_list:
            missing_info.append("No prior clinical timeline events or past medical history recorded.")
        if not symptoms_list and not diagnoses_list:
            missing_info.append("No current chief symptoms or preliminary diagnoses recorded.")

        is_insufficient = False
        data_sufficiency_notes = "Patient information is sufficient for navigation support."

        total_inputs_count = (
            len(symptoms_list) + len(diagnoses_list) + len(medications_list) +
            len(lab_findings_list) + len(previous_events_list) + (1 if clinical_notes_clean else 0)
        )

        if total_inputs_count == 0:
            is_insufficient = True
            data_sufficiency_notes = "Insufficient patient information provided. Please supply clinical notes, documents, labs, or symptoms."

        # 5. RAG Integration & Evidence Separation
        evidence_items: List[ExternalEvidenceItem] = []
        guideline_summaries: List[str] = []

        if request.include_rag and not is_insufficient:
            rag_response: Optional[RAGQueryResponse] = request.rag_evidence

            if not rag_response and (symptoms_list or diagnoses_list or clinical_notes_clean):
                rag_query_terms = symptoms_list + diagnoses_list
                rag_query = f"Clinical management guidelines for {', '.join(rag_query_terms)}" if rag_query_terms else clinical_notes_clean[:200]
                try:
                    rag_response = rag_engine.query_guidelines(rag_query, top_k=2)
                except Exception as e:
                    logger.error("RAG query failed in summary engine: %s", e)

            if rag_response and rag_response.evidence_found:
                for chunk in rag_response.retrieved_chunks:
                    evidence_item = ExternalEvidenceItem(
                        source_title=chunk.title,
                        excerpt=chunk.content,
                        relevance_score=chunk.relevance_score,
                        citation=chunk.source,
                        guideline_id=chunk.chunk_id,
                    )
                    evidence_items.append(evidence_item)
                    guideline_summaries.append(f"External Guideline [{chunk.source}]: {chunk.title} - {chunk.content[:120]}...")

        # 6. Fact vs Inference Separation
        clinical_observations: List[str] = []
        if symptoms_list and medications_list:
            med_names = [m.drug_name for m in medications_list]
            clinical_observations.append(
                f"Patient presents with symptoms ({', '.join(symptoms_list[:3])}) while concurrently on medication(s) ({', '.join(med_names[:3])})."
            )
        if lab_findings_list:
            abnormal_labs = [f"{l.test_name} ({l.value})" for l in lab_findings_list if l.status and l.status.upper() in ("ABNORMAL", "HIGH", "LOW", "CRITICAL")]
            if abnormal_labs:
                clinical_observations.append(f"Lab metric findings require monitoring: {', '.join(abnormal_labs)}.")
            else:
                clinical_observations.append("Lab metrics reviewed; values present in documentation.")
        elif not is_insufficient:
            clinical_observations.append("Baseline clinical data recorded; additional lab workup may be clinically warranted.")

        uncertainties_gaps = list(missing_info) + list(conflicting_info) + list(uncertain_extractions)

        fact_vs_inference = FactVsInference(
            directly_extracted_facts=extracted_facts if extracted_facts else ["No direct patient facts extracted."],
            clinical_observations=clinical_observations,
            external_guideline_evidence=guideline_summaries if guideline_summaries else ["No external guideline evidence requested or retrieved."],
            uncertainties_and_gaps=uncertainties_gaps if uncertainties_gaps else ["No critical uncertainties or gaps identified."],
        )

        # 7. Confidence Calculation
        if is_insufficient:
            overall_confidence = 0.0
        else:
            base_confidence = 0.95
            if low_ocr_confidence:
                base_confidence -= 0.15
            if conflicting_info:
                base_confidence -= 0.15
            if len(missing_info) >= 3:
                base_confidence -= 0.15
            elif len(missing_info) >= 1:
                base_confidence -= 0.05
            if has_injection:
                base_confidence -= 0.10

            overall_confidence = max(0.10, min(1.0, round(base_confidence, 2)))

        confidence_indicators = SummaryConfidence(
            overall_confidence=overall_confidence,
            high_confidence_facts=high_confidence_facts,
            uncertain_extractions=uncertain_extractions,
            conflicting_information=conflicting_info,
            missing_information=missing_info,
        )

        # 8. Patient Overview Construction
        overview_text = (
            f"Patient evaluation context. Presenting chief complaint/symptoms: {', '.join(symptoms_list) if symptoms_list else 'None reported'}. "
            f"Diagnoses on file: {', '.join(diagnoses_list) if diagnoses_list else 'None recorded'}. "
            f"Active medications count: {len(medications_list)}. Lab metrics count: {len(lab_findings_list)}."
        )
        if is_insufficient:
            overview_text = "Insufficient patient presentation data available for comprehensive overview."

        overview = PatientOverview(
            patient_id=request.patient_id,
            age=request.age,
            gender=request.gender,
            chief_complaint=symptoms_list[0] if symptoms_list else (request.clinical_notes[:100] if request.clinical_notes else None),
            summary_context=overview_text,
        )

        # Treatment history & recent changes
        treatment_history: List[str] = [f"Medication: {m.drug_name} ({m.dosage or 'dosage unstated'})" for m in medications_list]
        recent_changes: List[str] = []
        if previous_events_list:
            recent_changes.append(f"Latest documented event: {previous_events_list[-1].title} on {previous_events_list[-1].event_date or 'recent date'}")

        unresolved_issues: List[str] = []
        if symptoms_list:
            unresolved_issues.append(f"Ongoing symptoms requiring evaluation: {', '.join(symptoms_list)}")
        if conflicting_info:
            unresolved_issues.extend(conflicting_info)

        elapsed_time = round(time.time() - start_time, 3)

        return PatientSummaryReport(
            overview=overview,
            current_symptoms=symptoms_list,
            relevant_diagnoses=diagnoses_list,
            current_medications=medications_list,
            laboratory_findings=lab_findings_list,
            previous_events=previous_events_list,
            treatment_history=treatment_history,
            recent_changes=recent_changes,
            unresolved_issues=unresolved_issues,
            missing_information=missing_info,
            fact_vs_inference=fact_vs_inference,
            evidence_references=evidence_items,
            confidence_indicators=confidence_indicators,
            insufficient_information=is_insufficient,
            data_sufficiency_notes=data_sufficiency_notes,
            processing_time_seconds=elapsed_time,
        )


patient_summary_engine = PatientSummaryEngine()
