from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "personal-lms"
    debug: bool = False
    database_url: str = "sqlite:///./instance/personal_lms.db"
    session_secret_key: str = "change-me-in-env"
    ai_helper_enabled: bool = True
    openai_api_key: str = ""
    ai_helper_model: str = "gpt-4o-mini"
    ai_helper_timeout_seconds: int = 12

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PERSONAL_LMS_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
