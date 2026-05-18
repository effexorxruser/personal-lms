from __future__ import annotations

from fastapi import HTTPException

from app.config import get_settings


def require_terminal_enabled() -> None:
    if not get_settings().enable_terminal:
        raise HTTPException(status_code=403, detail="Терминал отключён конфигурацией.")


def require_ai_helper_enabled() -> None:
    if not get_settings().enable_ai_helper:
        raise HTTPException(status_code=403, detail="Помощник Lain AI отключён конфигурацией.")
