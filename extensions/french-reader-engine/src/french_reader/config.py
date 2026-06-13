import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FRENCH_READER_", extra="ignore")

    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 5002
    cors_origins: str = "http://localhost:5173,http://localhost:8080"
    tts_max_chars: int = 5000
    tts_default_voice: str = "fr-FR-DeniseNeural"
    ai_max_chars: int = 5000
    llm_api_key: str = ""
    llm_base_url: str = "https://api.moonshot.ai/v1"
    llm_model: str = "moonshot-v1-32k"
    llm_timeout_seconds: float = 90.0

    def resolve_llm_api_key(self) -> str | None:
        key = self.llm_api_key.strip()
        if key:
            return key
        env_key = os.getenv("OPENAI_API_KEY", "").strip()
        return env_key or None


settings = Settings()
