from __future__ import annotations

from app.config import Settings
from app.services.lain_provider import LainProviderError, LainProviderRequest, request_lain_reply

_FALLBACK_QUOTES = (
    "Собери маленький рабочий шаг сейчас, и весь маршрут станет проще.",
    "Не ищи идеальный ритм: закрой один проверяемый action и двигайся дальше.",
    "Прогресс строится из коротких сессий, а не из редких рывков.",
)


def get_dashboard_session_quote(*, settings: Settings, next_step: str) -> str:
    if not settings.ai_helper_enabled or not settings.openai_api_key:
        return _FALLBACK_QUOTES[0]

    try:
        quote = request_lain_reply(
            LainProviderRequest(
                api_key=settings.openai_api_key,
                model=settings.ai_helper_model,
                timeout_seconds=min(settings.ai_helper_timeout_seconds, 6),
                system_prompt=(
                    "Ты даешь одну короткую мотивационную фразу для учебной сессии в стиле"
                    " спокойного AI-тьютора. Без пафоса, без эмодзи, 1-2 предложения."
                ),
                user_prompt=(
                    "Сформулируй фокус-фразу для текущей сессии.\n"
                    f"Текущий следующий шаг: {next_step}\n"
                    "Ответ: только фраза на русском языке."
                ),
            )
        ).strip()
    except LainProviderError:
        return _FALLBACK_QUOTES[1]

    if not quote:
        return _FALLBACK_QUOTES[2]
    return quote[:220]

