"""
CarePath AI — Groq Reviewer Structured Contract Schema
======================================================
Defines the Pydantic schema for the independent AI Reviewer output contract.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class GroqReviewResult(BaseModel):
    """
    Structured response contract returned by the Groq Reviewer.
    """
    review_status: str = Field(
        default="pass",
        description="Overall review verdict: 'pass', 'revise', 'escalate', or 'unavailable'"
    )
    safety_concerns: List[str] = Field(
        default_factory=list,
        description="Flags for emergency/safety issues overlooked by primary reasoning"
    )
    contradictions: List[str] = Field(
        default_factory=list,
        description="Inconsistencies detected between symptoms, timeline, documents, and medications"
    )
    missing_information: List[str] = Field(
        default_factory=list,
        description="Critical medical data or documents missing for safe navigation"
    )
    unsupported_claims: List[str] = Field(
        default_factory=list,
        description="Conclusions not backed by retrieved patient context or evidence"
    )
    overconfidence_flags: List[str] = Field(
        default_factory=list,
        description="Statements presenting excessive certainty"
    )
    diagnosis_language_flags: List[str] = Field(
        default_factory=list,
        description="Phrases crossing into formal diagnosis"
    )
    medication_safety_flags: List[str] = Field(
        default_factory=list,
        description="Phrases attempting autonomous prescription or dosage modification"
    )
    specialty_pathway_concern: Optional[str] = Field(
        default=None,
        description="Concerns regarding suggested specialist pathway appropriateness"
    )
    recommended_changes: List[str] = Field(
        default_factory=list,
        description="Suggested navigation adjustments"
    )
    review_summary: str = Field(
        default="",
        description="Human-readable synthesis of reviewer findings"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Reviewer confidence score"
    )
