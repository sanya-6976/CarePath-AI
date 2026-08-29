"""Production schemas for CarePath AI medical knowledge retrieval."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RAGQueryRequest(BaseModel):
    """Request for medical evidence retrieval."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        min_length=1,
        max_length=4096,
        description="Clinical question or medical information request.",
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
    )

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str) -> str:
        value = " ".join(value.split()).strip()

        if not value:
            raise ValueError("Clinical query cannot be empty.")

        return value


class DocumentChunk(BaseModel):
    """A retrieved evidence chunk with provenance."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str = Field(min_length=1)

    title: str = Field(min_length=1)

    content: str = Field(min_length=1)

    source: str = Field(min_length=1)

    relevance_score: float = Field(
        ge=0.0,
        le=1.0,
    )

    rank: int = Field(
        ge=1,
    )

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )


class RAGQueryResponse(BaseModel):
    """Evidence-grounded medical retrieval response."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)

    retrieved_chunks: list[DocumentChunk] = Field(
        default_factory=list,
    )

    synthesized_guideline_answer: str = Field(
        min_length=1,
    )

    citations: list[str] = Field(
        default_factory=list,
    )

    processing_time_seconds: float = Field(
        ge=0.0,
    )

    backend: str = Field(
        min_length=1,
    )

    evidence_found: bool

    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
    )