"""Prompt Injection and Untrusted Data Defense Utility.

Treats all patient clinical text, OCR text, document inputs, and retrieved evidence
as untrusted content to prevent prompt injection and instruction hijacking.
"""

from __future__ import annotations

import re
from typing import List, Tuple

# Common prompt injection attack patterns in medical/user text
PROMPT_INJECTION_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("ignore_previous_instructions", re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE)),
    ("disregard_previous_instructions", re.compile(r"disregard\s+(all\s+)?(previous|prior|above)\s+(instructions?|rules?|prompts?)", re.IGNORECASE)),
    ("forget_previous_instructions", re.compile(r"forget\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE)),
    ("system_prompt_override", re.compile(r"(system\s+prompt|system\s+role|developer\s+mode|dan\s+mode)\s*(override|bypass|activate|enabled)?", re.IGNORECASE)),
    ("roleplay_hijack", re.compile(r"you\s+are\s+now\s+(an?\s+)?(unrestricted|evil|jailbroken|different)\s+ai", re.IGNORECASE)),
    ("override_safety", re.compile(r"override\s+(safety|clinical|medical)\s+(rules?|guidelines?|protocols?)", re.IGNORECASE)),
    ("act_as_unrestricted", re.compile(r"act\s+as\s+an?\s+unrestricted", re.IGNORECASE)),
    ("bypass_rules", re.compile(r"bypass\s+(all\s+)?(rules?|filters?|guardrails?)", re.IGNORECASE)),
]


def detect_prompt_injection(text: str) -> Tuple[bool, List[str]]:
    """Detect if *text* contains known prompt injection attempts.

    Returns:
        Tuple of (is_injection_detected, list_of_matching_pattern_names)
    """
    if not text or not isinstance(text, str):
        return False, []

    detected_patterns: List[str] = []
    for pattern_name, regex in PROMPT_INJECTION_PATTERNS:
        if regex.search(text):
            detected_patterns.append(pattern_name)

    return len(detected_patterns) > 0, detected_patterns


def sanitize_untrusted_text(text: str) -> str:
    """Sanitize untrusted input text so prompt injections are neutralized.

    Prompt injection instructions inside text are converted to harmless text representations
    and enclosed in non-executable structural block tags.
    """
    if not text or not isinstance(text, str):
        return ""

    sanitized = text

    # Replace active injection phrases with explicit text markers so LLM/parsers treat them as pure text content
    for pattern_name, regex in PROMPT_INJECTION_PATTERNS:
        sanitized = regex.sub("[PROMPT_INJECTION_NEUTRALIZED]", sanitized)

    return sanitized.strip()


def wrap_untrusted_document(text: str, document_label: str = "PATIENT_DOCUMENT") -> str:
    """Wrap untrusted document text in non-executable structural XML tags for LLM prompts."""
    clean_text = sanitize_untrusted_text(text)
    return f"<{document_label}>\n{clean_text}\n</{document_label}>"
