"""Production Doctor Feedback Interpretation Engine.

Interprets clinician consultation notes, Q&A answers, and assessment feedback.
Classifies statement origins, structures doctor-stated medication instructions (without AI prescribing),
extracts follow-ups and referrals, detects cross-record conflicts, and structures CarePath Memory candidates.
"""

from __future__ import annotations

import re
import time
from typing import List, Optional, Set, Dict, Tuple

from app.core.config import settings
from app.core.logging import get_logger
from app.core.interfaces import DoctorFeedbackService, ServiceHealthStatus, ServiceAvailability
from app.core.prompt_safety import sanitize_untrusted_text, detect_prompt_injection
from app.schemas.doctor_feedback import (
    DoctorFeedbackRequest,
    DoctorFeedbackInterpretationReport,
    InterpretedFeedbackItem,
    DoctorMedicationInstruction,
    DoctorFollowUpInstruction,
    DoctorReferralItem,
    DoctorFeedbackConflict,
    MemoryCandidateItem,
    DoctorStatementType,
    MemoryCategory,
)
from app.schemas.patient_summary import PatientSummaryReport

logger = get_logger(__name__)

# Regex helpers for follow-ups, referrals, allergies, and medication actions
FOLLOW_UP_REGEX = re.compile(
    r"\b(?:review|follow-up|follow up|return|re-evaluate|see again)(?:\s+review|\s+patient)?\s+(?:in|after|within)?\s*(\d+\s*(?:days?|weeks?|months?))?\s*(?:if\s+([A-Za-z0-9\s\-]+))?\b",
    re.IGNORECASE,
)
REFERRAL_REGEX = re.compile(
    r"\b(?:refer|referral|consult|consultation)\s+(?:to\s+)?([A-Za-z]+(?:\s+specialist|\s+clinic)?)\s*(?:for\s+([A-Za-z0-9\s\-]+))?\b",
    re.IGNORECASE,
)
ALLERGY_FEEDBACK_REGEX = re.compile(r"\b(?:allergic|allergy)\s+to\s+([A-Za-z0-9\s\-]+)\b", re.IGNORECASE)
MEDICATION_ACTION_PATTERNS = [
    ("DISCONTINUE", re.compile(r"\b(?:discontinue|stop|cease|hold)\s+([A-Za-z0-9\-]+)(?:\s+(\d+\s*mg))?\b", re.IGNORECASE)),
    ("INITIATE", re.compile(r"\b(?:start|initiate|prescribe)\s+([A-Za-z0-9\-]+)(?:\s+(\d+\s*mg))?\b", re.IGNORECASE)),
    ("MODIFY_DOSAGE", re.compile(r"\b(?:change|increase|decrease|adjust)\s+([A-Za-z0-9\-]+)\s+(?:to\s+)?(\d+\s*mg)\b", re.IGNORECASE)),
    ("CONTINUE", re.compile(r"\b(?:continue|maintain)\s+([A-Za-z0-9\-]+)(?:\s+(\d+\s*mg))?\b", re.IGNORECASE)),
]


class DoctorFeedbackEngine(DoctorFeedbackService):
    """Engine for interpreting clinician feedback into memory-ready objects."""

    _SERVICE_NAME = "CarePath Doctor Feedback Engine"
    _SERVICE_VERSION = "1.0.0"

    def health_check(self) -> ServiceHealthStatus:
        """Return readiness status of the feedback engine."""
        return ServiceHealthStatus(
            availability=ServiceAvailability.AVAILABLE,
            backend="doctor_feedback_engine",
            message="Doctor feedback engine is fully operational.",
        )

    def get_service_info(self) -> dict:
        """Return engine metadata."""
        return {
            "name": self._SERVICE_NAME,
            "version": self._SERVICE_VERSION,
            "status": self.health_check().availability.value,
        }

    def interpret_feedback(self, request: DoctorFeedbackRequest) -> DoctorFeedbackInterpretationReport:
        """Interpret doctor consultation notes, Q&A answers, and assessment feedback."""
        start_time = time.time()

        # 1. Sanitize Untrusted Inputs
        raw_notes = request.doctor_notes or ""
        clean_notes = sanitize_untrusted_text(raw_notes) if raw_notes else ""
        has_injection, injection_types = False, []
        if raw_notes:
            has_injection, injection_types = detect_prompt_injection(raw_notes)
            if has_injection:
                logger.warning("Prompt injection detected in doctor feedback: %s", injection_types)

        uncertainties: List[str] = []
        source_refs: List[str] = []

        if has_injection:
            uncertainties.append(f"Prompt injection pattern ({', '.join(injection_types)}) detected and neutralized.")

        # Aggregate feedback statements
        feedback_lines: List[Tuple[str, str]] = []  # (text, source_origin)
        if clean_notes:
            source_refs.append(f"Doctor Notes ({len(clean_notes)} chars)")
            for line in clean_notes.split("\n"):
                line_str = line.strip()
                if line_str:
                    feedback_lines.append((line_str, "doctor_notes"))

        for qa in request.question_answers:
            q_text = qa.get("question", "").strip()
            a_text = sanitize_untrusted_text(qa.get("answer", "")).strip()
            if a_text:
                combined_qa = f"Answer to '{q_text}': {a_text}" if q_text else a_text
                feedback_lines.append((combined_qa, "question_answer"))
                source_refs.append(f"Q&A Answer: {q_text[:30]}")

        # Check total feedback length
        if not feedback_lines:
            return DoctorFeedbackInterpretationReport(
                interpreted_items=[],
                clinical_observations=[],
                confirmed_diagnoses=[],
                medications=[],
                follow_up_instructions=[],
                referrals=[],
                conflicts=[],
                memory_candidates=[],
                uncertainties=["No doctor feedback or Q&A answers provided."],
                source_references=source_refs,
                overall_confidence=0.0,
                processing_time_seconds=round(time.time() - start_time, 3),
            )

        # Output containers
        interpreted_items: List[InterpretedFeedbackItem] = []
        clinical_observations: List[str] = []
        confirmed_diagnoses: List[str] = []
        medications_list: List[DoctorMedicationInstruction] = []
        follow_ups_list: List[DoctorFollowUpInstruction] = []
        referrals_list: List[DoctorReferralItem] = []
        conflicts_list: List[DoctorFeedbackConflict] = []
        memory_candidates_list: List[MemoryCandidateItem] = []

        full_feedback_text = " ".join([text for text, _ in feedback_lines])

        # 2. Extract Doctor Medication Instructions
        for action_name, regex_pat in MEDICATION_ACTION_PATTERNS:
            for match in regex_pat.finditer(full_feedback_text):
                drug_name = match.group(1).strip()
                dosage = match.group(2).strip() if match.lastindex >= 2 and match.group(2) else None
                verbatim_stmt = match.group(0).strip()

                med_inst = DoctorMedicationInstruction(
                    drug_name=drug_name.capitalize(),
                    action=action_name,
                    doctor_stated_instruction=verbatim_stmt,
                    dosage=dosage,
                    statement_type=DoctorStatementType.DOCTOR_STATED,
                    confidence=0.96,
                )
                medications_list.append(med_inst)

                # Add to Memory Candidates
                memory_candidates_list.append(
                    MemoryCandidateItem(
                        content=f"Medication Instruction [{action_name}]: {verbatim_stmt}",
                        category=MemoryCategory.MEDICATION_INFORMATION,
                        statement_type=DoctorStatementType.DOCTOR_STATED,
                        importance_score=0.92,
                        reason=f"Doctor explicitly instructed {action_name.lower()} for medication {drug_name}.",
                    )
                )

        # 3. Extract Follow-up Instructions
        for match in FOLLOW_UP_REGEX.finditer(full_feedback_text):
            timeframe = match.group(1).strip() if match.lastindex and match.lastindex >= 1 and match.group(1) else None
            condition = match.group(2).strip() if match.lastindex and match.lastindex >= 2 and match.group(2) else None
            verbatim_fu = match.group(0).strip()

            fu_inst = DoctorFollowUpInstruction(
                instruction_text=verbatim_fu,
                timeframe=timeframe,
                trigger_conditions=condition,
                is_explicit_doctor_instruction=True,
                confidence=0.94,
            )
            follow_ups_list.append(fu_inst)

            memory_candidates_list.append(
                MemoryCandidateItem(
                    content=f"Follow-Up Instruction: {verbatim_fu}",
                    category=MemoryCategory.FOLLOW_UP_INSTRUCTION,
                    statement_type=DoctorStatementType.DOCTOR_STATED,
                    importance_score=0.88,
                    reason="Explicit follow-up schedule or return trigger stated by clinician.",
                )
            )

        # 4. Extract Specialist Referrals
        for match in REFERRAL_REGEX.finditer(full_feedback_text):
            specialty = match.group(1).strip()
            reason = match.group(2).strip() if match.group(2) else "Specialist evaluation"
            verbatim_ref = match.group(0).strip()

            ref_item = DoctorReferralItem(
                specialty=specialty.capitalize(),
                reason=reason,
                urgency="URGENT" if "urgent" in verbatim_ref.lower() else "ROUTINE",
                supporting_doctor_statement=verbatim_ref,
                confidence=0.93,
            )
            referrals_list.append(ref_item)

            memory_candidates_list.append(
                MemoryCandidateItem(
                    content=f"Specialist Referral: {specialty} for {reason}",
                    category=MemoryCategory.TREATMENT_EVENT,
                    statement_type=DoctorStatementType.DOCTOR_STATED,
                    importance_score=0.89,
                    reason=f"Doctor recommended referral to {specialty}.",
                )
            )

        # 5. Extract Allergies & Chronic Conditions for Memory
        for match in ALLERGY_FEEDBACK_REGEX.finditer(full_feedback_text):
            allergy_drug = match.group(1).strip()
            memory_candidates_list.append(
                MemoryCandidateItem(
                    content=f"Allergy Record: Patient allergic to {allergy_drug}",
                    category=MemoryCategory.ALLERGY_INFORMATION,
                    statement_type=DoctorStatementType.DOCTOR_STATED,
                    importance_score=1.0,
                    reason=f"Doctor explicitly recorded allergy to {allergy_drug}.",
                )
            )

        # 6. Statement Origin Classification & Observation Extraction
        for text, origin in feedback_lines:
            lower_text = text.lower()
            stmt_type = DoctorStatementType.DOCTOR_STATED

            if any(p in lower_text for p in ["patient states", "patient reports", "complains of", "denies"]):
                stmt_type = DoctorStatementType.PATIENT_REPORTED
            elif "assessment:" in lower_text or "diagnosis:" in lower_text:
                diag_match = re.search(r"(?:assessment|diagnosis):\s*([A-Za-z0-9\s\-]+)", text, re.IGNORECASE)
                if diag_match:
                    diag_name = diag_match.group(1).strip()
                    confirmed_diagnoses.append(diag_name)
                    memory_candidates_list.append(
                        MemoryCandidateItem(
                            content=f"Confirmed Diagnosis: {diag_name}",
                            category=MemoryCategory.LONG_TERM_CLINICAL_FACT,
                            statement_type=DoctorStatementType.DOCTOR_STATED,
                            importance_score=0.95,
                            reason=f"Doctor assessment confirmed diagnosis '{diag_name}'.",
                        )
                    )

            interpreted_items.append(
                InterpretedFeedbackItem(
                    text=text,
                    category="CLINICAL_OBSERVATION" if stmt_type == DoctorStatementType.PATIENT_REPORTED else "DOCTOR_ASSESSMENT",
                    statement_type=stmt_type,
                    confidence=0.80 if stmt_type == DoctorStatementType.PATIENT_REPORTED else 0.95,
                    source_snippet=text[:100],
                )
            )
            clinical_observations.append(text)

        # 7. Cross-Record Conflict Detection
        if request.existing_summary:
            ps = request.existing_summary
            # Allergy conflicts
            for match in ALLERGY_FEEDBACK_REGEX.finditer(full_feedback_text):
                allergy_drug = match.group(1).strip().lower()
                if "no allergy" in " ".join(ps.missing_information).lower() or not ps.current_medications:
                    conflicts_list.append(
                        DoctorFeedbackConflict(
                            conflicting_topic=f"Allergy Discrepancy for {allergy_drug}",
                            record_statement="Prior summary listed no active allergy records.",
                            doctor_statement=f"Doctor feedback explicitly states allergy to {allergy_drug}.",
                            conflict_description=f"New allergy statement for '{allergy_drug}' contradicts prior blank allergy history.",
                            uncertainty_status="REQUIRES_CLINICAL_RECONCILIATION",
                        )
                    )

            # Medication status conflicts
            for med_inst in medications_list:
                m_name = med_inst.drug_name.lower()
                prior_med = next((m for m in ps.current_medications if m.drug_name.lower() == m_name), None)
                if prior_med and med_inst.action == "DISCONTINUE":
                    conflicts_list.append(
                        DoctorFeedbackConflict(
                            conflicting_topic=f"Medication Discontinuation for {med_inst.drug_name}",
                            record_statement=f"Prior summary listed active medication {prior_med.drug_name} ({prior_med.dosage or 'dosage unstated'}).",
                            doctor_statement=f"Doctor instructed: '{med_inst.doctor_stated_instruction}'.",
                            conflict_description=f"Doctor discontinued active medication '{med_inst.drug_name}'.",
                            uncertainty_status="DOCTOR_OVERRIDE_RECORDED",
                        )
                    )

        # 8. Sort & Finalize Memory Candidates
        # Remove duplicate memory content
        seen_mem_content: Set[str] = set()
        unique_memory_candidates: List[MemoryCandidateItem] = []
        for mem in memory_candidates_list:
            if mem.content not in seen_mem_content:
                seen_mem_content.add(mem.content)
                unique_memory_candidates.append(mem)

        unique_memory_candidates.sort(key=lambda m: m.importance_score, reverse=True)

        overall_conf = 0.94
        if uncertainties:
            overall_conf -= 0.15
        if has_injection:
            overall_conf -= 0.10

        overall_confidence = max(0.10, min(1.0, round(overall_conf, 2)))
        elapsed_time = round(time.time() - start_time, 3)

        return DoctorFeedbackInterpretationReport(
            interpreted_items=interpreted_items,
            clinical_observations=clinical_observations,
            confirmed_diagnoses=confirmed_diagnoses,
            medications=medications_list,
            follow_up_instructions=follow_ups_list,
            referrals=referrals_list,
            conflicts=conflicts_list,
            memory_candidates=unique_memory_candidates,
            uncertainties=uncertainties,
            source_references=source_refs,
            overall_confidence=overall_confidence,
            processing_time_seconds=elapsed_time,
        )


doctor_feedback_engine = DoctorFeedbackEngine()
