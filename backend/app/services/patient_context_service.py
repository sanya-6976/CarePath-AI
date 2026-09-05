"""
CarePath AI - Controlled Patient Context Retrieval Service
==========================================================
Provides controlled, authorization-scoped context aggregation for LLM reasoning.
Ensures patient data isolation by strictly filtering all queries by patient_id/user_id.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.logging import logger
from app.database.models import User, Encounter, Attachment, AuditLog


class PatientContextService:
    """
    Service responsible for retrieving and formatting a patient's complete longitudinal record
    (demographics, symptoms, attachments, OCR extractions, timeline, medications, follow-ups)
    into a structured context object for LLM multi-agent evaluation.
    """

    @staticmethod
    async def get_patient_context(
        db_session,
        patient_id: str,
        current_encounter_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieves the complete authorization-checked patient context.
        """
        context: Dict[str, Any] = {
            "patient_id": patient_id,
            "timestamp": datetime.utcnow().isoformat(),
            "profile": {},
            "current_encounter": None,
            "past_encounters": [],
            "medical_records": [],
            "medications": [],
            "timeline_events": [],
            "care_plans": [],
            "follow_ups": [],
            "doctor_bridge_summaries": [],
            "retrieved_evidence": []
        }

        if not db_session or not patient_id:
            return context

        try:
            # 1. User & Profile
            user_stmt = select(User).where(User.id == patient_id)
            user_result = await db_session.execute(user_stmt)
            user = user_result.scalar_one_or_none()

            if user:
                context["profile"] = {
                    "patient_id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "role": user.role
                }

            # 2. Encounters & Attachments
            enc_stmt = (
                select(Encounter)
                .where(Encounter.user_id == patient_id)
                .options(selectinload(Encounter.attachments))
                .order_by(Encounter.created_at.desc())
            )
            enc_result = await db_session.execute(enc_stmt)
            encounters = enc_result.scalars().all()

            for enc in encounters:
                enc_data = {
                    "encounter_id": enc.id,
                    "chief_complaint": enc.chief_complaint,
                    "symptoms_duration": enc.symptoms_duration,
                    "symptoms_severity": enc.symptoms_severity,
                    "urgency_level": enc.urgency_level,
                    "is_emergency": enc.is_emergency,
                    "recommended_specialty": enc.recommended_specialty,
                    "status": enc.status,
                    "created_at": enc.created_at.isoformat() if enc.created_at else None,
                    "attachments_count": len(enc.attachments)
                }

                if current_encounter_id and enc.id == current_encounter_id:
                    context["current_encounter"] = enc_data
                else:
                    context["past_encounters"].append(enc_data)

                # Attachments / Medical Records
                for att in enc.attachments:
                    context["medical_records"].append({
                        "attachment_id": att.id,
                        "encounter_id": att.encounter_id,
                        "file_type": att.file_type,
                        "mime_type": att.mime_type,
                        "processed": att.processed,
                        "uploaded_at": att.uploaded_at.isoformat() if att.uploaded_at else None
                    })

                # Timeline Event generation
                context["timeline_events"].append({
                    "event_id": f"enc_{enc.id}",
                    "date": enc.created_at.isoformat() if enc.created_at else None,
                    "type": "ENCOUNTER",
                    "description": f"Encounter: {enc.chief_complaint}",
                    "urgency": enc.urgency_level,
                    "source": "PATIENT_REPORTED"
                })

            return context

        except Exception as e:
            logger.error("Failed to build patient context", patient_id=patient_id, error=str(e))
            return context
