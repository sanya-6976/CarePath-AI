"""Production Treatment-Response Analysis Engine.

Compares documented treatment events against clinical outcomes (symptoms, lab metrics, clinical notes).
Classifies response quality, causality levels, overlapping treatments, and conflicts.
Strictly adheres to non-prescriptive evidence-analysis boundaries.
"""

from __future__ import annotations

import re
import time
from typing import List, Optional, Dict, Any, Tuple, Set

from app.core.config import settings
from app.core.logging import get_logger
from app.core.interfaces import TreatmentResponseService, ServiceHealthStatus, ServiceAvailability
from app.core.prompt_safety import sanitize_untrusted_text, detect_prompt_injection
from app.schemas.treatment_response import (
    TreatmentResponseRequest,
    TreatmentResponseReport,
    TreatmentResponseItem,
    SymptomComparison,
    LabComparison,
    ResponseClassification,
    CausalityLevel,
)

logger = get_logger(__name__)


class TreatmentResponseEngine(TreatmentResponseService):
    """Engine for analyzing clinical evidence of treatment response."""

    _SERVICE_NAME = "CarePath Treatment Response Engine"
    _SERVICE_VERSION = "1.0.0"

    def health_check(self) -> ServiceHealthStatus:
        """Return readiness status of the treatment response engine."""
        return ServiceHealthStatus(
            availability=ServiceAvailability.AVAILABLE,
            backend="treatment_response_engine",
            message="Treatment response engine is fully operational.",
        )

    def get_service_info(self) -> dict:
        """Return engine metadata."""
        return {
            "name": self._SERVICE_NAME,
            "version": self._SERVICE_VERSION,
            "status": self.health_check().availability.value,
        }

    def analyze_treatment_response(self, request: TreatmentResponseRequest) -> TreatmentResponseReport:
        """Analyze documented treatment events and evaluate clinical outcomes."""
        start_time = time.time()

        # Prompt Injection Protection
        raw_notes = request.clinical_notes or ""
        clean_notes = sanitize_untrusted_text(raw_notes) if raw_notes else ""
        has_injection, injection_types = False, []
        if raw_notes:
            has_injection, injection_types = detect_prompt_injection(raw_notes)
            if has_injection:
                logger.warning("Prompt injection detected in treatment response input: %s", injection_types)

        insufficient_data_cases: List[str] = []
        conflicts: List[str] = []
        analyzed_items: List[TreatmentResponseItem] = []

        if has_injection:
            conflicts.append(f"Prompt injection pattern ({', '.join(injection_types)}) detected and neutralized.")

        treatments = request.treatment_events or []
        symptoms = request.symptoms or []
        labs = request.labs or []
        doctor_feedback = request.doctor_feedback or ""

        # Extract treatments from clinical notes if not explicitly passed
        if not treatments and clean_notes:
            for match in re.finditer(r"\b(?:started|prescribed|taking|received)\s+([A-Za-z0-9\-]+)(?:\s+(\d+\s*mg))?\b", clean_notes, re.IGNORECASE):
                t_name = match.group(1).strip().capitalize()
                treatments.append({
                    "treatment_name": t_name,
                    "treatment_type": "MEDICATION",
                    "start_date": "Documented in notes",
                    "source": "Clinical Notes",
                })

        if not treatments:
            return TreatmentResponseReport(
                analyzed_treatments=[],
                insufficient_data_cases=["No documented treatment events available for analysis."],
                conflicts=conflicts,
                overall_confidence=0.0,
                processing_time_seconds=round(time.time() - start_time, 3),
            )

        multiple_treatments = len(treatments) > 1

        for trt in treatments:
            t_name = str(trt.get("treatment_name") or trt.get("name") or "Unspecified Treatment").capitalize()
            t_type = str(trt.get("treatment_type") or "MEDICATION")
            start_date = trt.get("start_date")
            end_date = trt.get("end_date")
            indication = trt.get("indication")

            symptom_comps: List[SymptomComparison] = []
            lab_comps: List[LabComparison] = []
            baseline_obs: List[str] = []
            follow_up_obs: List[str] = []
            evidence_lines: List[str] = []

            # 1. Symptom Comparison
            for sym in symptoms:
                s_name = str(sym.get("symptom_name") or sym.get("name") or "symptom").lower()
                baseline = str(sym.get("baseline_status") or sym.get("before") or "Severe/Present")
                post = str(sym.get("post_treatment_status") or sym.get("after") or "Uncertain")

                change = "UNCERTAIN"
                if any(w in post.lower() for w in ["resolved", "improved", "less", "absent", "significantly better"]):
                    change = "IMPROVED"
                elif any(w in post.lower() for w in ["worse", "increased", "severe", "worsened"]):
                    change = "WORSENED"
                elif any(w in post.lower() for w in ["unchanged", "same", "persisted", "persistent"]):
                    change = "UNCHANGED"

                symptom_comps.append(
                    SymptomComparison(
                        symptom_name=s_name.capitalize(),
                        baseline_status=baseline,
                        post_treatment_status=post,
                        observed_change=change,
                        evidence=f"Baseline: {baseline}; Post-treatment: {post}",
                        confidence=0.88,
                    )
                )
                baseline_obs.append(f"{s_name.capitalize()}: {baseline}")
                follow_up_obs.append(f"{s_name.capitalize()}: {post}")

            # 2. Lab Comparison
            for lab in labs:
                m_name = str(lab.get("metric_name") or lab.get("name") or "Lab Metric")
                b_val = str(lab.get("baseline_value") or lab.get("before_value") or "")
                p_val = str(lab.get("post_value") or lab.get("after_value") or "")
                unit = str(lab.get("unit") or "")

                dir_change = "NOT_COMPARABLE"
                try:
                    bv = float(b_val)
                    pv = float(p_val)
                    if pv < bv:
                        dir_change = "DECREASED"
                    elif pv > bv:
                        dir_change = "INCREASED"
                    else:
                        dir_change = "UNCHANGED"
                except Exception:
                    dir_change = "NOT_COMPARABLE"

                lab_comps.append(
                    LabComparison(
                        metric_name=m_name,
                        baseline_value=b_val if b_val else None,
                        baseline_unit=unit if unit else None,
                        post_treatment_value=p_val if p_val else None,
                        post_treatment_unit=unit if unit else None,
                        direction_of_change=dir_change,
                        evidence=f"{m_name}: {b_val} {unit} -> {p_val} {unit}".strip(),
                        confidence=0.92,
                    )
                )

            # Analyze doctor feedback text
            if doctor_feedback:
                follow_up_obs.append(f"Doctor Feedback: {doctor_feedback[:100]}")

            # Determine Response Classification
            response_class = ResponseClassification.INSUFFICIENT_DATA
            if not symptom_comps and not lab_comps:
                insufficient_data_cases.append(f"Insufficient outcome data to evaluate {t_name}.")
                data_sufficiency = False
            else:
                data_sufficiency = True
                changes = [s.observed_change for s in symptom_comps]
                if all(c == "IMPROVED" for c in changes) and changes:
                    response_class = ResponseClassification.IMPROVED
                    evidence_lines.append(f"All documented symptoms improved following {t_name}.")
                elif all(c == "WORSENED" for c in changes) and changes:
                    response_class = ResponseClassification.WORSENED
                    evidence_lines.append(f"All documented symptoms worsened following {t_name}.")
                elif "IMPROVED" in changes and ("WORSENED" in changes or "UNCHANGED" in changes):
                    response_class = ResponseClassification.MIXED_RESPONSE
                    evidence_lines.append(f"Mixed response: some symptoms improved while others persisted or worsened.")
                elif all(c == "UNCHANGED" for c in changes) and changes:
                    response_class = ResponseClassification.STABLE
                    evidence_lines.append(f"Symptoms remained stable/unchanged following {t_name}.")
                else:
                    response_class = ResponseClassification.NO_CLEAR_RESPONSE
                    evidence_lines.append(f"No clear response pattern documented for {t_name}.")

            # Causality Level
            causality = CausalityLevel.UNKNOWN
            if "clinically documented" in (clean_notes + doctor_feedback).lower():
                causality = CausalityLevel.DOCUMENTED_CLINICAL_ASSOCIATION
            elif response_class in (ResponseClassification.IMPROVED, ResponseClassification.WORSENED, ResponseClassification.MIXED_RESPONSE):
                causality = CausalityLevel.TEMPORAL_ASSOCIATION

            item_conf = 0.90 if data_sufficiency else 0.40
            if not start_date or not end_date:
                item_conf = max(0.30, item_conf - 0.15)
            if multiple_treatments:
                item_conf = max(0.30, item_conf - 0.10)

            analyzed_items.append(
                TreatmentResponseItem(
                    treatment_name=t_name,
                    treatment_type=t_type,
                    start_date=start_date,
                    end_date=end_date,
                    indication=indication,
                    baseline_observations=baseline_obs,
                    follow_up_observations=follow_up_obs,
                    symptom_comparisons=symptom_comps,
                    lab_comparisons=lab_comps,
                    response_classification=response_class,
                    evidence=evidence_lines if evidence_lines else ["Documented clinical timeline observation."],
                    causality_level=causality,
                    multiple_contributors=multiple_treatments,
                    conflicts=conflicts,
                    confidence=round(item_conf, 2),
                    data_sufficiency=data_sufficiency,
                    source_references=["Clinical Notes", "Patient Record", "Lab Reports"],
                )
            )

        overall_conf = 0.92 if analyzed_items and any(i.data_sufficiency for i in analyzed_items) else 0.40
        if has_injection:
            overall_conf -= 0.15

        return TreatmentResponseReport(
            analyzed_treatments=analyzed_items,
            insufficient_data_cases=insufficient_data_cases,
            conflicts=conflicts,
            overall_confidence=max(0.10, min(1.0, round(overall_conf, 2))),
            processing_time_seconds=round(time.time() - start_time, 3),
        )


treatment_response_engine = TreatmentResponseEngine()
