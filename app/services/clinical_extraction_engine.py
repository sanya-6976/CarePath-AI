"""Production Clinical Information Extraction Engine.

Extracts normalized medical entities, medications, lab findings, procedures, allergies,
history items, temporal expressions, body sites, and cross-source conflicts from multi-modal inputs.
Ensures negation detection, source traceability, prompt injection safety, and quality control.
"""

from __future__ import annotations

import re
import time
from typing import List, Optional, Set, Dict, Tuple

from app.core.config import settings
from app.core.logging import get_logger
from app.core.interfaces import ClinicalExtractionService, ServiceHealthStatus, ServiceAvailability
from app.core.prompt_safety import sanitize_untrusted_text, detect_prompt_injection
from app.schemas.clinical_extraction import (
    ClinicalExtractionRequest,
    ClinicalExtractionReport,
    ExtractedClinicalEntity,
    ExtractedMedicationFact,
    ExtractedLabFact,
    ExtractedProcedureFact,
    ExtractedTemporalEvent,
    ClinicalConflictRecord,
    ClinicalSourceType,
    FactType,
)
from app.schemas.ocr import OCRResult, PrescriptionItem, LabMetricItem
from app.schemas.nlp import BioNERResult
from app.services.nlp_engine import nlp_engine

logger = get_logger(__name__)

# Regular expressions for temporal parsing, procedures, allergies, and family history
TEMPORAL_DURATION_REGEX = re.compile(r"\b(?:for|during|over)\s+(\d+|\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b)\s+(day|days|week|weeks|month|months|year|years)\b", re.IGNORECASE)
TEMPORAL_ONSET_REGEX = re.compile(r"\b(?:started|began|onset)\s+(yesterday|today|\d+\s+days?\s+ago|\d+\s+weeks?\s+ago|in\s+\d{4})\b", re.IGNORECASE)
ANATOMICAL_BODY_SITES = [
    "left lower lung", "right lower lung", "bilateral lungs", "chest", "abdomen",
    "abdominal region", "right knee", "left knee", "head", "throat", "back", "forearm",
]
PROCEDURE_KEYWORDS = [
    "appendectomy", "chest x-ray", "ct scan", "mri", "ultrasound", "echocardiogram",
    "coronary angiography", "bronchoscopy", "physiotherapy", "lumbar puncture",
]
ALLERGY_REGEX = re.compile(r"\b(?:allergy|allergic)\s+to\s+([A-Za-z0-9\s\-]+?)(?=[.,;\n]|$)", re.IGNORECASE)
FAMILY_HISTORY_REGEX = re.compile(r"\b(?:father|mother|brother|sister|parent|maternal|paternal)\s+(?:had|has|history of)\s+([A-Za-z0-9\s\-]+?)(?=[.,;\n]|$)", re.IGNORECASE)


class ClinicalExtractionEngine(ClinicalExtractionService):
    """Engine responsible for extracting structured clinical facts and resolving conflicts."""

    _SERVICE_NAME = "CarePath Clinical Extraction Engine"
    _SERVICE_VERSION = "1.0.0"

    def health_check(self) -> ServiceHealthStatus:
        """Return the readiness state of the extraction engine and NLP sub-engine."""
        nlp_health = nlp_engine.health_check()
        if not nlp_health.is_ok:
            return ServiceHealthStatus(
                availability=ServiceAvailability.DEGRADED,
                backend="clinical_extraction_engine",
                message="NLP sub-engine running in degraded mode.",
            )
        return ServiceHealthStatus(
            availability=ServiceAvailability.AVAILABLE,
            backend="clinical_extraction_engine",
            message="Clinical extraction engine is fully operational.",
        )

    def get_service_info(self) -> dict:
        """Return service metadata."""
        return {
            "name": self._SERVICE_NAME,
            "version": self._SERVICE_VERSION,
            "status": self.health_check().availability.value,
        }

    def extract_clinical_info(self, request: ClinicalExtractionRequest) -> ClinicalExtractionReport:
        """Process multi-modal inputs and produce a validated ClinicalExtractionReport."""
        start_time = time.time()

        # 1. Sanitize Untrusted Clinical Text
        raw_text = request.clinical_text or ""
        clean_text = sanitize_untrusted_text(raw_text) if raw_text else ""
        has_injection, injection_types = False, []
        if raw_text:
            has_injection, injection_types = detect_prompt_injection(raw_text)
            if has_injection:
                logger.warning("Prompt injection detected during clinical extraction: %s", injection_types)

        uncertain_info: List[str] = []
        source_refs: List[str] = []
        if has_injection:
            uncertain_info.append(f"Prompt injection pattern ({', '.join(injection_types)}) detected and neutralized.")

        # 2. Extracted Entity Containers
        all_entities: List[ExtractedClinicalEntity] = []
        symptoms_list: List[ExtractedClinicalEntity] = []
        diagnoses_list: List[ExtractedClinicalEntity] = []
        medications_list: List[ExtractedMedicationFact] = []
        lab_findings_list: List[ExtractedLabFact] = []
        procedures_list: List[ExtractedProcedureFact] = []
        allergies_list: List[ExtractedClinicalEntity] = []
        history_list: List[ExtractedClinicalEntity] = []
        temporal_events_list: List[ExtractedTemporalEvent] = []
        conflicts_list: List[ClinicalConflictRecord] = []

        source_type_default = request.default_source_type

        # 3. NLP Bio-NER Extraction from Clinical Text
        if clean_text:
            source_refs.append(f"Clinical Text ({len(clean_text)} chars)")
            try:
                bioner = nlp_engine.extract_entities(clean_text)

                # Process NLP Medical Entities
                for entity in bioner.entities:
                    # Detect temporal context in surrounding snippet
                    temp_event: Optional[ExtractedTemporalEvent] = None
                    if entity.context:
                        dur_match = TEMPORAL_DURATION_REGEX.search(entity.context)
                        if dur_match:
                            temp_expr = dur_match.group(0)
                            temp_event = ExtractedTemporalEvent(
                                event_name=entity.text,
                                temporal_expression=temp_expr,
                                normalized_duration=dur_match.group(1),
                                relationship="DURATION",
                            )
                            temporal_events_list.append(temp_event)

                    # Detect body site
                    body_site_match: Optional[str] = None
                    if entity.context:
                        for site in ANATOMICAL_BODY_SITES:
                            if site in entity.context.lower():
                                body_site_match = site
                                break

                    fact_type = FactType.EXPLICIT_FACT
                    confidence = entity.confidence
                    if has_injection:
                        confidence = max(0.40, confidence - 0.20)

                    extracted_entity = ExtractedClinicalEntity(
                        text=entity.text,
                        normalized_text=entity.normalized_text,
                        category=entity.category,
                        fact_type=fact_type,
                        negated=entity.negated,
                        body_site=body_site_match,
                        temporal_context=temp_event,
                        source_type=source_type_default,
                        source_snippet=entity.context[:100] if entity.context else entity.text,
                        confidence=confidence,
                    )

                    all_entities.append(extracted_entity)
                    if entity.category == "SYMPTOM":
                        symptoms_list.append(extracted_entity)
                    elif entity.category == "DIAGNOSIS":
                        diagnoses_list.append(extracted_entity)
                    elif entity.category == "MEDICATION":
                        medications_list.append(
                            ExtractedMedicationFact(
                                drug_name=entity.text,
                                negated=entity.negated,
                                status="DISCONTINUED" if entity.negated else "REPORTED",
                                source_type=source_type_default,
                                source_snippet=entity.context[:100] if entity.context else entity.text,
                                confidence=confidence,
                            )
                        )

                # Process NLP Medication Instructions
                for inst in bioner.medication_instructions:
                    med_fact = ExtractedMedicationFact(
                        drug_name=inst.medication,
                        dosage=inst.dosage,
                        frequency=inst.frequency,
                        duration=inst.duration,
                        route=inst.route,
                        negated=inst.negated,
                        status="DISCONTINUED" if inst.negated else "REPORTED",
                        source_type=source_type_default,
                        source_snippet=f"{inst.medication} {inst.dosage or ''}".strip(),
                        confidence=inst.confidence,
                    )
                    medications_list.append(med_fact)

            except Exception as e:
                logger.error("NLP extraction failed in clinical extraction engine: %s", e)

            # Medication & Dosage extraction via regex
            for match in re.finditer(r"\b([A-Z][a-zA-Z]{2,})\s+(\d+\s*(?:mg|g|mcg|ml|units))\b", clean_text, re.IGNORECASE):
                med_name = match.group(1).strip()
                med_dose = match.group(2).strip()
                med_fact = ExtractedMedicationFact(
                    drug_name=med_name.capitalize(),
                    dosage=med_dose,
                    negated=False,
                    status="REPORTED",
                    source_type=source_type_default,
                    source_snippet=match.group(0),
                    confidence=0.92,
                )
                medications_list.append(med_fact)

            # Procedures Extraction via regex
            for proc in PROCEDURE_KEYWORDS:
                if re.search(r"\b" + re.escape(proc) + r"\b", clean_text, re.IGNORECASE):
                    proc_fact = ExtractedProcedureFact(
                        procedure_name=proc.title(),
                        status="COMPLETED",
                        source_type=source_type_default,
                        source_snippet=proc,
                        confidence=0.90,
                    )
                    procedures_list.append(proc_fact)

            # Allergy Extraction via regex
            for match in ALLERGY_REGEX.finditer(clean_text):
                allergy_target = match.group(1).strip()
                allergy_entity = ExtractedClinicalEntity(
                    text=f"Allergy to {allergy_target}",
                    normalized_text=allergy_target,
                    category="ALLERGY",
                    fact_type=FactType.EXPLICIT_FACT,
                    negated=False,
                    source_type=source_type_default,
                    source_snippet=match.group(0),
                    confidence=0.92,
                )
                allergies_list.append(allergy_entity)
                all_entities.append(allergy_entity)

            # Family History Extraction via regex
            for match in FAMILY_HISTORY_REGEX.finditer(clean_text):
                fam_target = match.group(0).strip()
                fam_entity = ExtractedClinicalEntity(
                    text=fam_target,
                    category="FAMILY_HISTORY",
                    fact_type=FactType.EXPLICIT_FACT,
                    negated=False,
                    source_type=source_type_default,
                    source_snippet=match.group(0),
                    confidence=0.88,
                )
                history_list.append(fam_entity)
                all_entities.append(fam_entity)

        # 4. Process Request Prescriptions & Lab Metrics
        for pres in request.prescriptions:
            source_refs.append(f"Prescription: {pres.drug_name}")
            medications_list.append(
                ExtractedMedicationFact(
                    drug_name=pres.drug_name,
                    dosage=pres.dosage,
                    frequency=pres.frequency,
                    duration=pres.duration,
                    negated=False,
                    status="ACTIVE",
                    source_type=ClinicalSourceType.PRESCRIPTION,
                    source_snippet=f"{pres.drug_name} {pres.dosage or ''}".strip(),
                    confidence=1.0,
                )
            )

        for lab in request.lab_metrics:
            source_refs.append(f"Lab Report: {lab.test_name}")
            lab_findings_list.append(
                ExtractedLabFact(
                    test_name=lab.test_name,
                    value=lab.value,
                    unit=lab.unit,
                    reference_range=lab.reference_range,
                    status=lab.status or ("ABNORMAL" if lab.status else "NORMAL"),
                    source_type=ClinicalSourceType.MEDICAL_REPORT,
                    source_snippet=f"{lab.test_name} = {lab.value} {lab.unit or ''}".strip(),
                    confidence=1.0,
                )
            )

        # 5. Process OCR Results
        for ocr in request.ocr_results:
            source_label = f"OCR Document ({ocr.filename})"
            source_refs.append(source_label)

            clean_ocr_text = sanitize_untrusted_text(ocr.raw_text)
            ocr_conf = ocr.confidence_score

            for pres in ocr.prescriptions:
                medications_list.append(
                    ExtractedMedicationFact(
                        drug_name=pres.drug_name,
                        dosage=pres.dosage,
                        frequency=pres.frequency,
                        duration=pres.duration,
                        negated=False,
                        status="ACTIVE",
                        source_type=ClinicalSourceType.OCR,
                        source_snippet=f"{ocr.filename}: {pres.drug_name}",
                        confidence=ocr_conf,
                    )
                )

            for lab in ocr.lab_metrics:
                lab_findings_list.append(
                    ExtractedLabFact(
                        test_name=lab.test_name,
                        value=lab.value,
                        unit=lab.unit,
                        reference_range=lab.reference_range,
                        status=lab.status,
                        source_type=ClinicalSourceType.OCR,
                        source_snippet=f"{ocr.filename}: {lab.test_name} = {lab.value}",
                        confidence=ocr_conf,
                    )
                )

        # 6. Process Existing Summary if Provided
        if request.existing_summary:
            ps = request.existing_summary
            for s in ps.current_symptoms:
                sym_ent = ExtractedClinicalEntity(
                    text=s,
                    category="SYMPTOM",
                    fact_type=FactType.EXPLICIT_FACT,
                    source_type=ClinicalSourceType.DOCTOR_INPUT,
                    source_snippet="Patient Summary",
                    confidence=0.95,
                )
                symptoms_list.append(sym_ent)
                all_entities.append(sym_ent)

            for d in ps.relevant_diagnoses:
                diag_ent = ExtractedClinicalEntity(
                    text=d,
                    category="DIAGNOSIS",
                    fact_type=FactType.EXPLICIT_FACT,
                    source_type=ClinicalSourceType.DOCTOR_INPUT,
                    source_snippet="Patient Summary",
                    confidence=0.95,
                )
                diagnoses_list.append(diag_ent)
                all_entities.append(diag_ent)

            for m in ps.current_medications:
                medications_list.append(
                    ExtractedMedicationFact(
                        drug_name=m.drug_name,
                        dosage=m.dosage,
                        frequency=m.frequency,
                        duration=m.duration,
                        status=m.status,
                        source_type=ClinicalSourceType.DOCTOR_INPUT,
                        source_snippet=f"Patient Summary Medication ({m.source})",
                        confidence=m.confidence,
                    )
                )

        # 7. Cross-Source Conflict Detection
        # Check medication status conflicts (e.g. active vs discontinued)
        med_dict: Dict[str, List[ExtractedMedicationFact]] = {}
        for med in medications_list:
            key = med.drug_name.lower().strip()
            med_dict.setdefault(key, []).append(med)

        for drug_key, facts in med_dict.items():
            if len(facts) > 1:
                statuses = {f.status for f in facts}
                negations = {f.negated for f in facts}
                dosages = {f.dosage for f in facts if f.dosage}

                if len(negations) > 1 or ("ACTIVE" in statuses and "DISCONTINUED" in statuses):
                    fact_a = facts[0]
                    fact_b = facts[1]
                    conflicts_list.append(
                        ClinicalConflictRecord(
                            conflicting_topic=f"Medication Status Conflict for {fact_a.drug_name}",
                            source_statement_a=f"{fact_a.source_type.value}: {fact_a.drug_name} status={fact_a.status} (negated={fact_a.negated})",
                            source_statement_b=f"{fact_b.source_type.value}: {fact_b.drug_name} status={fact_b.status} (negated={fact_b.negated})",
                            source_a_type=fact_a.source_type,
                            source_b_type=fact_b.source_type,
                            uncertainty_description=f"Contradictory administration/discontinuation records for medication '{fact_a.drug_name}'.",
                        )
                    )
                elif len(dosages) > 1:
                    fact_a = facts[0]
                    fact_b = facts[1]
                    conflicts_list.append(
                        ClinicalConflictRecord(
                            conflicting_topic=f"Medication Dosage Conflict for {fact_a.drug_name}",
                            source_statement_a=f"{fact_a.source_type.value}: {fact_a.drug_name} dosage={fact_a.dosage}",
                            source_statement_b=f"{fact_b.source_type.value}: {fact_b.drug_name} dosage={fact_b.dosage}",
                            source_a_type=fact_a.source_type,
                            source_b_type=fact_b.source_type,
                            uncertainty_description=f"Differing dosages documented for '{fact_a.drug_name}': {', '.join(dosages)}.",
                        )
                    )

        # 8. Deduplication & Quality Control
        unique_entities: List[ExtractedClinicalEntity] = []
        seen_entity_keys: Set[Tuple[str, str, bool]] = set()

        for ent in all_entities:
            key = (ent.text.lower().strip(), ent.category, ent.negated)
            if key not in seen_entity_keys:
                seen_entity_keys.add(key)
                unique_entities.append(ent)

        # Deduplicate symptoms and diagnoses lists
        unique_symptoms = [e for e in unique_entities if e.category == "SYMPTOM"]
        unique_diagnoses = [e for e in unique_entities if e.category == "DIAGNOSIS"]

        # Deduplicate medications list
        unique_meds: List[ExtractedMedicationFact] = []
        seen_med_keys: Set[Tuple[str, Optional[str], bool]] = set()
        for m in medications_list:
            key = (m.drug_name.lower().strip(), m.dosage, m.negated)
            if key not in seen_med_keys:
                seen_med_keys.add(key)
                unique_meds.append(m)

        # Deduplicate lab findings list
        unique_labs: List[ExtractedLabFact] = []
        seen_lab_keys: Set[Tuple[str, str]] = set()
        for l in lab_findings_list:
            key = (l.test_name.lower().strip(), l.value.strip())
            if key not in seen_lab_keys:
                seen_lab_keys.add(key)
                unique_labs.append(l)

        # Sort entities by confidence descending
        unique_entities.sort(key=lambda e: e.confidence, reverse=True)

        # 9. Compute Overall Confidence Score
        total_items = len(unique_entities) + len(unique_meds) + len(unique_labs)
        if total_items == 0:
            overall_confidence = 0.0
            uncertain_info.append("No clinical entities or structured metrics extracted.")
        else:
            conf_sum = (
                sum(e.confidence for e in unique_entities) +
                sum(m.confidence for m in unique_meds) +
                sum(l.confidence for l in unique_labs)
            )
            overall_confidence = round(conf_sum / total_items, 2)
            if conflicts_list:
                overall_confidence = max(0.10, round(overall_confidence - 0.15, 2))

        elapsed_time = round(time.time() - start_time, 3)

        return ClinicalExtractionReport(
            entities=unique_entities,
            symptoms=unique_symptoms,
            diagnoses=unique_diagnoses,
            medications=unique_meds,
            laboratory_findings=unique_labs,
            procedures=procedures_list,
            allergies=allergies_list,
            history_items=history_list,
            temporal_events=temporal_events_list,
            conflicts=conflicts_list,
            uncertain_information=uncertain_info,
            source_references=source_refs,
            overall_confidence=overall_confidence,
            processing_time_seconds=elapsed_time,
        )


clinical_extraction_engine = ClinicalExtractionEngine()
