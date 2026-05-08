from __future__ import annotations

import logging

from app.config import get_settings

log = logging.getLogger(__name__)

_DEFAULT_SECRET = "change-me-in-env"
_SECRET_MIN_LEN = 32


def _is_weak_session_secret(secret: str) -> bool:
    if secret == _DEFAULT_SECRET or "change-me" in secret.lower():
        return True
    return len(secret) < _SECRET_MIN_LEN


def emit_runtime_warnings() -> None:
    settings = get_settings()
    if _is_weak_session_secret(settings.session_secret_key):
        log.warning(
            "Слабый или дефолтный SESSION_SECRET_KEY: задайте длинную случайную строку перед production.",
        )

    if settings.debug:
        log.warning(
            "PERSONAL_LMS_DEBUG=true: режим отладки включён — не использовать в открытом production.",
        )
    if settings.debug and settings.session_cookie_secure:
        log.warning(
            "Включены одновременно debug и SESSION_COOKIE_SECURE: проверьте, что это ожидаемо для сервера.",
        )

    if settings.enable_terminal:
        log.warning(
            "ENABLE_TERMINAL=true: команды выполняются на доверенном хосте без изоляции sandbox; см. docs/product/TERMINAL_READINESS.md.",
        )

    if settings.app_mode == "public" or settings.enable_public_mode:
        log.warning(
            "Режим public / ENABLE_PUBLIC_MODE: платформа изначально friend-only без публичной регистрации — проверьте политику доступа VPS.",
        )

    if settings.enable_experimental_imports:
        log.warning("ENABLE_EXPERIMENTAL_IMPORTS=true: экспериментальная функциональность.")
