"""Application Settings and Environment Configuration."""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "CarePath AI Platform"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # API Keys
    GEMINI_API_KEY: str = ""

    # Paths
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    UPLOADS_DIRECTORY: str = "./data/uploads"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Upload & Request Limits
    MAX_UPLOAD_SIZE_MB: int = 20
    REQUEST_TIMEOUT_SECONDS: int = 60

    # ChromaDB
    CHROMA_COLLECTION_NAME: str = "medical_guidelines"
    EMBEDDING_PROVIDER: str = "local"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    # Per-module confidence thresholds (used by validation helpers)
    NLP_CONFIDENCE_THRESHOLD: float = 0.75
    VISION_CONFIDENCE_THRESHOLD: float = 0.70
    OCR_MIN_CONFIDENCE: float = 0.50

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

# Ensure required data directories exist
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
os.makedirs(settings.UPLOADS_DIRECTORY, exist_ok=True)
