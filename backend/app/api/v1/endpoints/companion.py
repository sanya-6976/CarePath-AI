"""Protected, patient-facing CarePath Companion API.

This router reads records owned by the JWT subject. It explains persisted
results and safely hands new clinical needs to the existing medical workflow.
"""
from __future__ import annotations

import asyncio
import json
import re
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from database.models import (AIAnalysis, CompanionConversation, CompanionMessage,
    MedicalFile, Medication, PatientProfile, PatientSymptom, PatientUpdate,
    Recommendation, TimelineEvent, UserPreference)


def _get_db():
    from database.connections import get_db
    yield from get_db()


router = APIRouter(prefix="/companion", tags=["CarePath Companion"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: Optional[str] = None
    language: str = "en"
    page_context: Optional[str] = Field(default=None, max_length=120)
    use_carepath_history: bool = True


class PreferenceRequest(BaseModel):
    language: str = "en"
    voice_responses: bool = False
    use_carepath_history: bool = True
    simple_medical_terms: bool = True


def _safe_text(value) -> str:
    return str(value or "").strip()


def retrieve_patient_context(db: Session, user_id: uuid.UUID) -> dict:
    """Collect a bounded, ownership-scoped context for the companion."""
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()
    analyses = db.query(AIAnalysis).filter(AIAnalysis.user_id == user_id).order_by(AIAnalysis.created_at.desc()).limit(2).all()
    recommendations = db.query(Recommendation).filter(Recommendation.user_id == user_id).order_by(Recommendation.created_at.desc()).limit(3).all()
    updates = db.query(PatientUpdate).filter(PatientUpdate.user_id == user_id).order_by(PatientUpdate.created_at.desc()).limit(6).all()
    symptoms = db.query(PatientSymptom).filter(PatientSymptom.user_id == user_id).order_by(PatientSymptom.created_at.desc()).limit(8).all()
    meds = db.query(Medication).filter(Medication.user_id == user_id).order_by(Medication.created_at.desc()).limit(10).all()
    files = db.query(MedicalFile).filter(MedicalFile.user_id == user_id).order_by(MedicalFile.created_at.desc()).limit(10).all()
    timeline = db.query(TimelineEvent).filter(TimelineEvent.user_id == user_id).order_by(TimelineEvent.event_date.desc()).limit(8).all()
    return {
        "profile": _safe_text(getattr(profile, "medical_summary", None)),
        "symptoms": [_safe_text(s.symptom_name) for s in symptoms if _safe_text(s.symptom_name)],
        "updates": [_safe_text(u.content) for u in updates if _safe_text(u.content)],
        "analyses": [{"summary": _safe_text(a.summary), "findings": _safe_text(a.findings), "changed": _safe_text(a.changed_factors)} for a in analyses],
        "recommendations": [{"specialist": _safe_text(r.specialist_type), "title": _safe_text(r.title), "rationale": _safe_text(r.rationale), "description": _safe_text(r.description)} for r in recommendations],
        "medications": [_safe_text(m.medication_name) for m in meds if _safe_text(m.medication_name)],
        "documents": [_safe_text(f.file_name) for f in files if _safe_text(f.file_name)],
        "timeline": [_safe_text(e.event_title or e.event_description) for e in timeline if _safe_text(e.event_title or e.event_description)],
    }


def _grounded_fallback(message: str, context: dict, language: str) -> str:
    """Deterministic disclosure-safe fallback used only when no LLM is configured."""
    q = message.lower()
    available = any(context.get(k) for k in ("profile", "symptoms", "updates", "analyses", "recommendations", "medications", "documents", "timeline"))
    if not available:
        return "मेरे पास आपके CarePath रिकॉर्ड में यह जानकारी नहीं है।" if language == "hi" else "I don't have that information in your CarePath records."
    if any(x in q for x in ("specialist", "referred", "recommendation", "referral")):
        r = context["recommendations"][0] if context["recommendations"] else None
        if not r:
            return "मेरे पास विशेषज्ञ की सिफारिश उपलब्ध नहीं है।" if language == "hi" else "I don't have a specialist recommendation in your CarePath records."
        reason = r["rationale"] or r["description"] or "the recorded CarePath recommendation"
        return (f"आपकी CarePath सिफारिश {r['specialist']} के लिए है। दर्ज कारण: {reason}। यह डॉक्टर की सलाह का विकल्प नहीं है।" if language == "hi" else f"Your CarePath recommendation is for {r['specialist']}. The recorded reason is: {reason}. This does not replace advice from your clinician.")
    if any(x in q for x in ("changed", "change", "what changed")):
        changed = context["analyses"][0]["changed"] if context["analyses"] else ""
        return (f"नवीनतम CarePath विश्लेषण में दर्ज बदलाव: {changed or 'कोई बदलाव दर्ज नहीं है।'}" if language == "hi" else f"The latest CarePath analysis records these changes: {changed or 'No changed factors are recorded.'}")
    if any(x in q for x in ("medication", "medicine", "drug")):
        items = ", ".join(context["medications"]) or "none recorded"
        return f"आपके CarePath रिकॉर्ड में दवाएं: {items}." if language != "hi" else f"आपके CarePath रिकॉर्ड में दर्ज दवाएं: {items}।"
    if any(x in q for x in ("document", "upload")):
        items = ", ".join(context["documents"]) or "none recorded"
        return f"Documents in your CarePath record: {items}." if language != "hi" else f"आपके CarePath रिकॉर्ड में दस्तावेज़: {items}।"
    summary = context["analyses"][0]["summary"] if context["analyses"] else ""
    symptoms = ", ".join(context["symptoms"][:5])
    return (f"आपके CarePath रिकॉर्ड का संक्षिप्त सार: {summary or 'कोई विश्लेषण सार उपलब्ध नहीं है।'} {('दर्ज लक्षण: ' + symptoms + '।') if symptoms else ''} कृपया चिकित्सा निर्णय के लिए अपने डॉक्टर से बात करें।" if language == "hi" else f"A concise CarePath-record summary: {summary or 'No analysis summary is available.'} {('Recorded symptoms: ' + symptoms + '.') if symptoms else ''} Please discuss medical decisions with your clinician.")


def classify_companion_intent(message: str) -> str:
    """Route only new clinical needs; this classifier never makes a diagnosis."""
    value = message.lower()
    if re.search(r"\b(chest pain|difficulty breathing|gasping|blue lips|face drooping|slurred speech|throat closing|unconscious|suicidal)\b", value):
        return "URGENT_SAFETY_CONCERN"
    if any(term in value for term in ("getting worse", "spreading", "not working", "did not help", "new symptom", "new pain", "medicine isn't working", "medicine is not working")):
        return "SYMPTOM_CHANGE"
    if any(term in value for term in ("i have", "i am having", "symptom", "rash", "pain", "fever", "cough")):
        return "NEW_SYMPTOM"
    return "EXISTING_RESULT_EXPLANATION"


def _handoff_answer(result: dict, language: str) -> str:
    if result.get("is_emergency"):
        return "आपातकालीन चेतावनी मिली है। कृपया तुरंत स्थानीय आपातकालीन सेवा से संपर्क करें।" if language == "hi" else "A potential emergency was identified. Please contact local emergency services immediately."
    referral = result.get("referral") or {}
    specialist = referral.get("specialist")
    changed = result.get("changed_factors") or []
    summary = result.get("summary") or "A new CarePath clinical assessment has been completed."
    if language == "hi":
        return f"आपके नए संदेश के आधार पर CarePath ने नया मूल्यांकन किया। {summary} {'सुझाया गया विशेषज्ञ: ' + specialist + '।' if specialist else ''} {'बदलाव: ' + '; '.join(map(str, changed)) if changed else ''} कृपया चिकित्सा निर्णय के लिए अपने चिकित्सक से बात करें।"
    return f"CarePath completed a new assessment based on your message. {summary} {('Suggested specialist: ' + specialist + '.') if specialist else ''} {('Changes noted: ' + '; '.join(map(str, changed))) if changed else ''} Please discuss medical decisions with your clinician."


async def _answer(message: str, context: dict, memory: list[CompanionMessage], language: str, simple_terms: bool) -> str:
    # Existing server-side AI client is used when configured; fallback remains grounded in stored records.
    try:
        from app.core.ai_client import generate_gemini_json
        prompt = json.dumps({"question": message, "carepath_context": context, "recent_conversation": [{"role": m.role, "content": m.content} for m in memory[-6:]]}, default=str)
        system = ("You are CarePath Companion, a healthcare-navigation assistant. Answer only from the supplied CarePath context; say information is unavailable when absent. Do not diagnose or override safety warnings. Use simple terms when requested. Return JSON with an 'answer' string. Answer in Hindi." if language == "hi" else "You are CarePath Companion, a healthcare-navigation assistant. Answer only from the supplied CarePath context; say information is unavailable when absent. Do not diagnose or override safety warnings. Use simple terms when requested. Return JSON with an 'answer' string. Answer in English.")
        result = await generate_gemini_json(prompt, system_instruction=system, temperature=0.1)
        if result and isinstance(result.get("answer"), str) and result["answer"].strip():
            from app.agents.companion_graph import run_companion_workflow
            return run_companion_workflow(context, result["answer"].strip(), language)
    except Exception:
        pass
    from app.agents.companion_graph import run_companion_workflow
    return run_companion_workflow(context, _grounded_fallback(message, context, language), language)


@router.post("/chat")
async def chat(req: ChatRequest, db: Session = Depends(_get_db), current_user=Depends(get_current_user)):
    if not req.message.strip():
        raise HTTPException(status_code=422, detail="Please enter a message.")
    language = "hi" if req.language.lower().startswith("hi") else "en"
    conversation = None
    if req.conversation_id:
        try:
            conversation = db.query(CompanionConversation).filter(CompanionConversation.conversation_id == uuid.UUID(req.conversation_id), CompanionConversation.user_id == current_user.user_id).first()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid conversation identifier.")
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found.")
    if not conversation:
        conversation = CompanionConversation(user_id=current_user.user_id)
        db.add(conversation); db.flush()
    memory = db.query(CompanionMessage).filter(CompanionMessage.conversation_id == conversation.conversation_id).order_by(CompanionMessage.created_at.asc()).all()
    preference = db.query(UserPreference).filter(UserPreference.user_id == current_user.user_id).first()
    use_history = req.use_carepath_history and (preference.use_carepath_history if preference else True)
    context = retrieve_patient_context(db, current_user.user_id) if use_history else {}
    db.add(CompanionMessage(conversation_id=conversation.conversation_id, role="user", content=req.message.strip(), language=language))
    intent = classify_companion_intent(req.message.strip())
    handoff = intent in {"NEW_SYMPTOM", "SYMPTOM_CHANGE", "URGENT_SAFETY_CONCERN"}
    if handoff:
        # Persist the patient-provided change, then route through the existing,
        # authenticated medical endpoint and its 11-agent LangGraph workflow.
        db.add(PatientUpdate(update_id=uuid.uuid4(), user_id=current_user.user_id, update_type="companion_clinical_handoff", content=req.message.strip(), created_at=datetime.utcnow()))
        db.flush()
        try:
            from app.api.v1.endpoints.medical import AnalyzeRequest, trigger_analysis
            result = await trigger_analysis(AnalyzeRequest(patient_id=str(current_user.user_id)), db, current_user)
            answer = _handoff_answer(result, language)
        except HTTPException:
            answer = "नया AI मूल्यांकन अस्थायी रूप से उपलब्ध नहीं है। यदि लक्षण गंभीर हैं तो तुरंत चिकित्सा सहायता लें।" if language == "hi" else "A new AI assessment is temporarily unavailable. If your symptoms are severe, seek medical care immediately."
            handoff = False
    else:
        answer = await _answer(req.message.strip(), context, memory, language, preference.simple_medical_terms if preference else True)
    db.add(CompanionMessage(conversation_id=conversation.conversation_id, role="assistant", content=answer, language=language))
    conversation.updated_at = datetime.utcnow(); db.commit()
    return {"conversation_id": str(conversation.conversation_id), "answer": answer, "language": language, "used_carepath_history": use_history, "intent": intent, "clinical_handoff": handoff}


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str, db: Session = Depends(_get_db), current_user=Depends(get_current_user)):
    try: cid = uuid.UUID(conversation_id)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid conversation identifier.")
    conversation = db.query(CompanionConversation).filter(CompanionConversation.conversation_id == cid, CompanionConversation.user_id == current_user.user_id).first()
    if not conversation: raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"conversation_id": conversation_id, "messages": [{"role": m.role, "content": m.content, "language": m.language, "created_at": m.created_at.isoformat()} for m in conversation.messages]}


@router.put("/preferences")
def save_preferences(req: PreferenceRequest, db: Session = Depends(_get_db), current_user=Depends(get_current_user)):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.user_id).first() or UserPreference(user_id=current_user.user_id)
    pref.language = "hi" if req.language.lower().startswith("hi") else "en"; pref.voice_responses = req.voice_responses; pref.use_carepath_history = req.use_carepath_history; pref.simple_medical_terms = req.simple_medical_terms
    db.add(pref); db.commit()
    return {"language": pref.language, "voice_responses": pref.voice_responses, "use_carepath_history": pref.use_carepath_history, "simple_medical_terms": pref.simple_medical_terms}
