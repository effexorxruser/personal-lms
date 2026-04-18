from __future__ import annotations

from app.config import Settings, get_settings

DEFAULT_HELPER_LESSON_KEY = "foundation-intro"


def build_ai_helper_view_context(
    *,
    lesson_key: str | None,
    settings: Settings | None = None,
) -> dict[str, str | bool]:
    runtime = settings or get_settings()
    normalized_lesson_key = (lesson_key or "").strip() or DEFAULT_HELPER_LESSON_KEY
    return {
        "ai_helper_enabled": bool(runtime.ai_helper_enabled),
        "ai_helper_lesson_key": normalized_lesson_key,
        "ai_helper_history_endpoint": "/api/ai/helper/history",
    }
