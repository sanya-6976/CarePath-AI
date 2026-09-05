"""
CarePath AI — Groq Independent AI Reviewer Client Service
==========================================================
Provides a server-side HTTP client for invoking Groq API models (e.g. llama-3.3-70b-versatile)
to perform independent clinical consistency, safety, and reasoning reviews.
"""

import os
import json
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger
from app.schemas.review_schema import GroqReviewResult

GROQ_DEFAULT_API_URL = "https://api.groq.com/openai/v1/chat/completions"


async def review_with_groq(
    patient_context: Dict[str, Any],
    proposed_navigation: Dict[str, Any],
    system_instruction: Optional[str] = None,
    temperature: float = 0.1
) -> Dict[str, Any]:
    """
    Invokes Groq API to independently evaluate proposed primary care navigation against patient context.
    Returns parsed dictionary matching GroqReviewResult schema or safe fallback.
    """
    api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
    api_url = settings.GROQ_API_URL or GROQ_DEFAULT_API_URL
    model_name = settings.GROQ_MODEL or "llama-3.3-70b-versatile"

    if not api_key:
        logger.info("GROQ_API_KEY not configured. Falling back to rule-based reviewer status.")
        return GroqReviewResult(
            review_status="unavailable",
            review_summary="Groq API key optional/absent during development. Reviewer safely bypassed."
        ).model_dump()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    sys_prompt = system_instruction or (
        "You are an independent clinical consistency critic and patient-friendly reviewer for CarePath AI healthcare navigation. "
        "Your role is to independently review the proposed care navigation plan against the retrieved patient context. "
        "Do NOT diagnose the patient or prescribe/change medication. "
        "Evaluate: 1) Did the primary model ignore context? 2) Are there contradictions between symptoms, timeline, and reports? "
        "3) Is information missing? 4) Are claims unsupported by evidence? 5) Is there overconfidence or diagnosis language? "
        "6) Are safety concerns overlooked? "
        "CRITICAL FORMATTING INSTRUCTION: Write your 'review_summary' in warm, easy-to-read, plain English for a patient. "
        "Avoid raw code snippets, technical jargon, repeated file name boilerplate, or machine string concatenations. "
        "Return ONLY a valid JSON object with keys:\n"
        '{"review_status": "pass|revise|escalate", "safety_concerns": [], "contradictions": [], '
        '"missing_information": [], "unsupported_claims": [], "overconfidence_flags": [], '
        '"diagnosis_language_flags": [], "medication_safety_flags": [], "specialty_pathway_concern": null, '
        '"recommended_changes": [], "review_summary": "", "confidence": 1.0}'
    )

    user_content = json.dumps({
        "retrieved_patient_context": patient_context,
        "proposed_care_navigation": proposed_navigation
    }, indent=2)

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"}
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(api_url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                result = GroqReviewResult(**parsed)
                return result.model_dump()
            else:
                logger.error("Groq API Error Response", status_code=response.status_code, text=response.text)
                return GroqReviewResult(
                    review_status="unavailable",
                    review_summary=f"Groq API returned HTTP {response.status_code}. Safe fallback applied."
                ).model_dump()

    except Exception as e:
        logger.error("Groq API Invocation Exception", error=str(e))
        return GroqReviewResult(
            review_status="unavailable",
            review_summary=f"Groq exception: {str(e)}. Safe fallback applied."
        ).model_dump()
