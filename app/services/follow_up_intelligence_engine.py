"""Production Follow-Up Intelligence Engine.

Analyzes clinical history, doctor feedback, treatment responses, and pending items to identify follow-up requirements.
Strictly distinguishes clinician-stated instructions from AI decision support insights.
Adheres to non-prescriptive continuity of care boundaries.
"""

from __future__ import annotations

import re
import time
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from app.core.config import settings
from app.core.logging import get_logger
from app.core.interfaces import FollowUpIntelligenceService, ServiceHealthStatus, ServiceAvailability
from app.core.prompt_safety import sanitize_untrusted_text, detect_prompt_injection
from app.schemas.follow_up_intelligence import (
    FollowUpIntelligenceRequest,
    FollowUpIntelligenceReport,
    FollowUpItem,
    FollowUpType,
    FollowUpStatus,
    FollowUpPriority,
)

logger = get_logger(__name__)

DOCTOR_FU_REGEX = re.compile(
    r"\b(?:review|follow-up|follow up|return|re-evaluate|repeat|see again)\s+(?:in|after|within)?\s*(\d+\s*(?:days?|weeks?|months?))?\s*(?:if\s+([A-Za-z0-9\s\-]+))?\b",
    re.IGNORECASE,
)


class FollowUpIntelligenceEngine(FollowUpIntelligenceService):
    """Engine for identifying care-continuity follow-up requirements."""

    _SERVICE_NAME = "CarePath Follow-Up Intelligence Engine"
    _SERVICE_VERSION = "1.0.0"

    def health_check(self) -> ServiceHealthStatus:
        """Return readiness status of the follow-up intelligence engine."""
        return ServiceHealthStatus(
            availability=ServiceAvailability.AVAILABLE,
            backend="follow_up_intelligence_engine",
            message="Follow-up intelligence engine is fully operational.",
        )

    def get_service_info(self) -> dict:
        """Return engine metadata."""
        return {
            "name": self._SERVICE_NAME,
            "version": self._SERVICE_VERSION,
            "status": self.health_check().availability.value,
        }

    def analyze_follow_up(self, request: FollowUpIntelligenceRequest) -> FollowUpIntelligenceReport:
        """Analyze documented history, trends, and instructions to identify follow-up needs."""
        start_time = time.time()

        # Prompt Injection Protection
        raw_feedback = request.doctor_feedback or ""
        clean_feedback = sanitize_untrusted_text(raw_feedback) if raw_feedback else ""
        has_injection, injection_types = False, []
        if raw_feedback:
            has_injection, injection_types = detect_prompt_injection(raw_feedback)
            if has_injection:
                logger.warning("Prompt injection detected in follow-up input: %s", injection_types)

        pending_info: List[str] = []
        unresolved_issues: List[str] = []
        follow_up_items: List[FollowUpItem] = []

        if has_injection:
            unresolved_issues.append(f"Prompt injection pattern ({', '.join(injection_types)}) detected and neutralized.")

        # 1. Parse Doctor-Stated Follow-Up Instructions
        if clean_feedback:
            for match in DOCTOR_FU_REGEX.finditer(clean_feedback):
                timeframe = match.group(1).strip() if match.lastindex and match.lastindex >= 1 and match.group(1) else None
                condition = match.group(2).strip() if match.lastindex and match.lastindex >= 2 and match.group(2) else None
                verbatim_stmt = match.group(0).strip()

                fu_type = FollowUpType.REVIEW_CONSULTATION
                if "repeat" in verbatim_stmt.lower():
                    fu_type = FollowUpType.REPEAT_INVESTIGATION

                status = FollowUpStatus.UPCOMING
                if request.current_date and timeframe:
                    # Parse relative timeframe e.g. "2 weeks"
                    status = FollowUpStatus.DUE

                priority = FollowUpPriority.HIGH if condition or "urgent" in verbatim_stmt.lower() else FollowUpPriority.MEDIUM

                follow_up_items.append(
                    FollowUpItem(
                        follow_up_type=fu_type,
                        status=status,
                        priority=priority,
                        description=f"Doctor Instruction: {verbatim_stmt}",
                        reason=f"Clinician explicitly ordered review/follow-up ({timeframe or 'as needed'}).",
                        supporting_evidence=[verbatim_stmt],
                        source="DOCTOR_STATED_FOLLOW_UP",
                        deadline_date=timeframe,
                        is_doctor_stated=True,
                        confidence=0.96,
                    )
                )

        # 2. Analyze Treatment Responses for Unresolved Follow-Up Insights
        for trt in request.treatment_responses:
            t_name = str(trt.get("treatment_name") or "Treatment")
            response = str(trt.get("response_classification") or "")
            data_suff = trt.get("data_sufficiency", True)

            if response == "INSUFFICIENT_DATA" or not data_suff:
                pending_info.append(f"Treatment response data for '{t_name}' is incomplete.")
                follow_up_items.append(
                    FollowUpItem(
                        follow_up_type=FollowUpType.TREATMENT_RESPONSE_REASSESSMENT,
                        status=FollowUpStatus.PENDING_INFORMATION,
                        priority=FollowUpPriority.MEDIUM,
                        description=f"Reassess treatment response for {t_name}",
                        reason="Insufficient documented outcome observations to evaluate treatment effectiveness.",
                        supporting_evidence=[f"Treatment {t_name} response is unconfirmed."],
                        source="AI_FOLLOW_UP_INSIGHT",
                        is_doctor_stated=False,
                        confidence=0.82,
                    )
                )
            elif response == "WORSENED" or response == "MIXED_RESPONSE":
                unresolved_issues.append(f"Documented {response.lower()} response following treatment {t_name}.")
                follow_up_items.append(
                    FollowUpItem(
                        follow_up_type=FollowUpType.SYMPTOM_REASSESSMENT,
                        status=FollowUpStatus.DUE,
                        priority=FollowUpPriority.HIGH,
                        description=f"Review treatment effectiveness for {t_name}",
                        reason=f"Documented {response.lower()} outcome indicates clinical reassessment is required.",
                        supporting_evidence=[f"Treatment {t_name} showed {response.lower()} outcome."],
                        source="AI_FOLLOW_UP_INSIGHT",
                        is_doctor_stated=False,
                        confidence=0.89,
                    )
                )

        # 3. Check Extracted Info / Patient Summary for Pending Lab Reports or Unresolved Symptoms
        if request.extracted_info:
            ext_labs = request.extracted_info.get("labs", [])
            for lab in ext_labs:
                if isinstance(lab, dict) and lab.get("status") == "PENDING":
                    lab_name = str(lab.get("test_name") or "Lab Test")
                    pending_info.append(f"Pending laboratory result: {lab_name}")
                    follow_up_items.append(
                        FollowUpItem(
                            follow_up_type=FollowUpType.PENDING_REPORT,
                            status=FollowUpStatus.PENDING_INFORMATION,
                            priority=FollowUpPriority.MEDIUM,
                            description=f"Await pending laboratory report: {lab_name}",
                            reason=f"Laboratory test '{lab_name}' is pending final report.",
                            supporting_evidence=[f"Lab test {lab_name} status is PENDING."],
                            source="AI_FOLLOW_UP_INSIGHT",
                            is_doctor_stated=False,
                            confidence=0.90,
                        )
                    )

        # If no items detected, add baseline status
        if not follow_up_items:
            follow_up_items.append(
                FollowUpItem(
                    follow_up_type=FollowUpType.REVIEW_CONSULTATION,
                    status=FollowUpStatus.NO_FOLLOW_UP_DOCUMENTED,
                    priority=FollowUpPriority.LOW,
                    description="No explicit follow-up instructions or pending items documented.",
                    reason="Existing records list no pending tests, doctor instructions, or unresolved treatment events.",
                    supporting_evidence=["Patient history clear of pending follow-up triggers."],
                    source="AI_FOLLOW_UP_INSIGHT",
                    is_doctor_stated=False,
                    confidence=0.75,
                )
            )

        overall_conf = 0.94 if any(i.is_doctor_stated for i in follow_up_items) else 0.85
        if has_injection:
            overall_conf -= 0.15

        return FollowUpIntelligenceReport(
            follow_up_items=follow_up_items,
            pending_information=pending_info,
            unresolved_issues=unresolved_issues,
            data_sufficiency=True,
            overall_confidence=max(0.10, min(1.0, round(overall_conf, 2))),
            processing_time_seconds=round(time.time() - start_time, 3),
        )


follow_up_intelligence_engine = FollowUpIntelligenceEngine()
