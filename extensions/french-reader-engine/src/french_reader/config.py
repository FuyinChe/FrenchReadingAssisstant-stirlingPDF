from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FRENCH_READER_", extra="ignore")

    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 5002
    cors_origins: str = "http://localhost:5173,http://localhost:8080"


settings = Settings()
