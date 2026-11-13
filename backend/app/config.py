import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = ROOT_DIR / ".env"

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    MODEL_NAME: str = "gemini-3.5-flash"
    EMBEDDING_MODEL_NAME: str = "gemini-embedding-001"
    EMBEDDING_DIM: int = 768

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5433/contract_risk_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    STORAGE_TYPE: str = "local"
    UPLOAD_DIR: str = str(ROOT_DIR / "backend" / "uploads")
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    # "celery" = queue jobs on Redis (local dev); "inline" = run in a background
    # thread inside the API process (single-container hosting, no Redis needed).
    TASK_MODE: str = "celery"
    # When set, FastAPI also serves the built React app from this folder.
    FRONTEND_DIST_DIR: str = ""

    SIMILARITY_THRESHOLD: float = 0.65
    MAX_AGENT_CONCURRENCY: int = 1

    BANK_RATE_PCT: float = 5.75
    BANK_RATE_DATE: str = "2026-10-07"

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
