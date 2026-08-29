"""Configurable embedding adapter used by the medical knowledge store."""
from __future__ import annotations

import logging
from typing import Sequence

from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

from app.core.config import settings
from app.core.exceptions import ModelInferenceError, ServiceUnavailableError

logger = logging.getLogger(__name__)


class MedicalEmbedder(EmbeddingFunction):
    """Provider adapter with explicit vector dimensions and no silent fallback."""

    _DIMENSIONS = {"local": 384, "gemini": 768}

    def __init__(self, provider: str = "local", model_name: str | None = None) -> None:
        self.provider = provider.lower().strip()
        if self.provider not in self._DIMENSIONS:
            raise ValueError(f"Unsupported embedding provider: {provider}")
        self.model_name = model_name or (
            "models/text-embedding-004" if self.provider == "gemini" else "all-MiniLM-L6-v2"
        )
        self._dimension = self._DIMENSIONS[self.provider]
        self._model = None

        if self.provider == "gemini":
            api_key = getattr(settings, "GEMINI_API_KEY", "")
            if not api_key:
                logger.warning("GEMINI_API_KEY is missing for Gemini provider; falling back to local provider.")
                self.provider = "local"
                self.model_name = "all-MiniLM-L6-v2"
                self._dimension = self._DIMENSIONS["local"]
            else:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                except Exception as exc:
                    raise ServiceUnavailableError(f"Gemini embedding service could not be configured: {exc}") from exc

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed non-empty texts and validate response cardinality and dimensions."""
        if not texts:
            return []
        if any(not isinstance(text, str) or not text.strip() for text in texts):
            raise ModelInferenceError("Embedding input must contain non-empty strings.")
        try:
            if self.provider == "local":
                if self._model is None:
                    from sentence_transformers import SentenceTransformer
                    self._model = SentenceTransformer(self.model_name)
                raw_embeddings = self._model.encode(list(texts), convert_to_numpy=True).tolist()
            else:
                import google.generativeai as genai
                raw_embeddings = [
                    genai.embed_content(
                        model=self.model_name, content=text, task_type="retrieval_document"
                    ).get("embedding")
                    for text in texts
                ]
        except Exception as exc:
            logger.exception("Embedding generation failed using %s", self.provider)
            raise ModelInferenceError(f"Embedding generation failed: {exc}") from exc

        if len(raw_embeddings) != len(texts) or any(not vector for vector in raw_embeddings):
            raise ModelInferenceError("Embedding provider returned an incomplete response.")
        embeddings = [[float(value) for value in vector] for vector in raw_embeddings]
        if any(len(vector) != self.dimension for vector in embeddings):
            raise ModelInferenceError(
                f"Embedding provider returned a vector dimension inconsistent with {self.dimension}."
            )
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    def __call__(self, input: Documents) -> Embeddings:
        return self.embed_documents(input)
