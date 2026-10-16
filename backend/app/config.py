"""Runtime configuration, read from environment variables (see .env.example)."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Gemini / Vertex AI -------------------------------------------------
    # "vertex" uses Application Default Credentials (service account on Cloud Run).
    # "off" disables live AI calls; the app runs in clearly labelled demo mode.
    ai_backend: Literal["vertex", "off"] = "vertex"
    google_cloud_project: str | None = None
    google_cloud_location: str = "global"
    gemini_model: str = "gemini-2.5-flash"
    gemini_composer_model: str | None = None  # defaults to gemini_model
    gemini_timeout_s: float = 45.0
    gemini_max_retries: int = 2

    # When the AI composer fails, fall back to the deterministic matcher.
    # The response is always labelled with engine="rules" so it is never
    # presented as a Gemini result.
    composer_fallback: Literal["rules", "none"] = "rules"

    # --- Persistence ----------------------------------------------------------
    storage_backend: Literal["local", "gcp"] = "local"
    local_data_dir: Path = Path(".data")
    firestore_database: str = "(default)"
    gcs_bucket: str | None = None

    # --- Fashion knowledge retrieval (future vector index seam) -------------
    fashion_knowledge_backend: Literal["none", "local", "vector"] = "local"
    fashion_knowledge_path: Path | None = None  # defaults to bundled JSON
    fashion_knowledge_timeout_s: float = 2.0
    fashion_knowledge_top_k: int = 4

    # --- HTTP -----------------------------------------------------------------
    cors_origins: str = "http://localhost:3000"
    max_upload_bytes: int = 8 * 1024 * 1024
    max_wardrobe_items: int = 200

    @property
    def composer_model(self) -> str:
        return self.gemini_composer_model or self.gemini_model

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def ai_enabled(self) -> bool:
        return self.ai_backend == "vertex" and bool(self.google_cloud_project)


@lru_cache
def get_settings() -> Settings:
    return Settings()
