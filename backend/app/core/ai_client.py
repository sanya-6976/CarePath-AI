"""
CarePath AI - Gemini AI Client Service
======================================
Provides a robust, server-side HTTP client wrapper for calling Gemini API models
(e.g., gemini-3.6-flash) using httpx. Supports structured JSON generation, timeout
resilience, and graceful error fallbacks.
"""

import os
import json
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"


async def generate_gemini_json(
    prompt: str,
    system_instruction: Optional[str] = None,
    temperature: float = 0.1
) -> Optional[Dict[str, Any]]:
    """
    Sends a prompt to Gemini 3.6 Flash requesting JSON structured output.
    Returns parsed dictionary or None if key missing/API error.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        logger.warning("GEMINI_API_KEY not configured in environment. Using rule-based fallbacks.")
        return None

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "aistudio-build"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "responseMimeType": "application/json"
        }
    }

    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{GEMINI_API_URL}?key={api_key}",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(raw_text)
            else:
                logger.error("Gemini API Error Response", status_code=response.status_code, text=response.text)
                return None

    except Exception as e:
        logger.error("Gemini API Invocation Exception", error=str(e))
        return None
