from functools import lru_cache
from typing import Annotated, Literal

from pydantic import AliasChoices, BeforeValidator, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AppModeLiteral = Literal["friend_only", "public"]
SameSiteLiteral = Literal["lax", "strict", "none"]


def _optional_int_from_env(value: object) -> object:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    return int(str(value))


class Settings(BaseSettings):
    app_name: str = "personal-lms"
    debug: bool = False
    database_url: str = "sqlite:///./instance/personal_lms.db"

    app_mode: AppModeLiteral = Field(
        default="friend_only",
        validation_alias=AliasChoices("APP_MODE", "PERSONAL_LMS_APP_MODE"),
    )
    app_base_url: str = Field(
        default="",
        validation_alias=AliasChoices("APP_BASE_URL", "PERSONAL_LMS_APP_BASE_URL"),
    )

    session_secret_key: str = Field(
        default="change-me-in-env",
        validation_alias=AliasChoices("SESSION_SECRET_KEY", "PERSONAL_LMS_SESSION_SECRET_KEY"),
    )
    session_cookie_secure: bool = Field(
        default=False,
        validation_alias=AliasChoices("SESSION_COOKIE_SECURE", "PERSONAL_LMS_SESSION_COOKIE_SECURE"),
    )
    session_cookie_samesite: SameSiteLiteral = Field(
        default="lax",
        validation_alias=AliasChoices("SESSION_COOKIE_SAMESITE", "PERSONAL_LMS_SESSION_COOKIE_SAMESITE"),
    )
    session_cookie_name: str = Field(
        default="session",
        validation_alias=AliasChoices("SESSION_COOKIE_NAME", "PERSONAL_LMS_SESSION_COOKIE_NAME"),
    )
    session_max_age: Annotated[
        int | None,
        BeforeValidator(_optional_int_from_env),
    ] = Field(
        default=None,
        validation_alias=AliasChoices("SESSION_MAX_AGE", "PERSONAL_LMS_SESSION_MAX_AGE"),
        description="TTL cookie-сессии в секундах; пустое значение — без ограничения.",
    )

    enable_terminal: bool = Field(
        default=False,
        validation_alias=AliasChoices("ENABLE_TERMINAL", "PERSONAL_LMS_ENABLE_TERMINAL"),
    )
    enable_ai_helper: bool = Field(
        default=True,
        validation_alias=AliasChoices(
            "ENABLE_AI_HELPER",
            "PERSONAL_LMS_ENABLE_AI_HELPER",
            "AI_HELPER_ENABLED",
            "PERSONAL_LMS_AI_HELPER_ENABLED",
        ),
    )
    enable_experimental_imports: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "ENABLE_EXPERIMENTAL_IMPORTS",
            "PERSONAL_LMS_ENABLE_EXPERIMENTAL_IMPORTS",
        ),
    )
    enable_public_mode: bool = Field(
        default=False,
        validation_alias=AliasChoices("ENABLE_PUBLIC_MODE", "PERSONAL_LMS_ENABLE_PUBLIC_MODE"),
    )

    openai_api_key: str = ""
    ai_helper_model: str = "gpt-4o-mini"
    ai_helper_timeout_seconds: int = 12

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PERSONAL_LMS_",
        extra="ignore",
    )

    @field_validator("session_cookie_samesite", "app_mode", mode="before")
    @classmethod
    def _lowercase_enums(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
