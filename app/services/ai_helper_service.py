from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re

import httpx
from sqlmodel import Session, delete, select

from app.config import get_settings
from app.content_registry import get_content_registry
from app.models import AIHelperMessage, TerminalRun
from app.services.content_service import get_course_or_404, get_lesson_or_404
from app.services.task_service import resolve_lesson_task

MAX_HISTORY_MESSAGES = 40


@dataclass
class HelperContext:
    key: str
    label: str
    scope_summary: str
    lesson_key: str | None
    command_hints: list[str]


def _sanitize_path(path: str) -> str:
    clean = (path or "").strip()
    if not clean.startswith("/"):
        clean = "/" + clean
    return clean.split("?", 1)[0]


def resolve_helper_context(path: str) -> HelperContext:
    normalized = _sanitize_path(path)
    lesson_match = re.match(r"^/lessons/([^/]+)$", normalized)
    if lesson_match:
        lesson_key = lesson_match.group(1)
        lesson = get_lesson_or_404(lesson_key)
        task_resolution = resolve_lesson_task(lesson)
        command_hints: list[str] = []
        if task_resolution.task and task_resolution.task.terminal:
            command_hints = [preset.command for preset in task_resolution.task.terminal.presets[:3]]
        summary = f"Урок: {lesson.title}. Отвечай только в рамках этого урока, его задачи и связанного модуля."
        return HelperContext(
            key=f"lesson:{lesson.key}",
            label=f"Урок · {lesson.title}",
            scope_summary=summary,
            lesson_key=lesson.key,
            command_hints=command_hints,
        )

    course_match = re.match(r"^/courses/([^/]+)$", normalized)
    if course_match:
        course_slug = course_match.group(1)
        course = get_course_or_404(course_slug)
        return HelperContext(
            key=f"course:{course.slug}",
            label=f"Курс · {course.title}",
            scope_summary=f"Курс: {course.title}. Отвечай только по структуре курса, модулей, уроков и next step.",
            lesson_key=None,
            command_hints=[],
        )

    if normalized == "/dashboard":
        registry = get_content_registry()
        active_course = registry.courses.get("python-backend-ai-foundation")
        title = active_course.title if active_course else "Текущий курс"
        return HelperContext(
            key="page:dashboard",
            label="Панель",
            scope_summary=f"Панель прогресса. Отвечай только по курсу '{title}', текущему шагу и учебному ритму.",
            lesson_key=None,
            command_hints=[],
        )

    if normalized == "/recap":
        return HelperContext(
            key="page:recap",
            label="Итоги",
            scope_summary="Страница итогов. Отвечай только по прогрессу, блокерам и следующему учебному шагу.",
            lesson_key=None,
            command_hints=[],
        )

    page_key = normalized.replace("/", "_").strip("_") or "root"
    return HelperContext(
        key=f"page:{page_key}",
        label=f"Страница · {normalized}",
        scope_summary="Отвечай только по текущей странице LMS и учебному контексту курса.",
        lesson_key=None,
        command_hints=[],
    )


def get_history(session: Session, user_id: int, context_key: str) -> list[AIHelperMessage]:
    statement = (
        select(AIHelperMessage)
        .where(AIHelperMessage.user_id == user_id, AIHelperMessage.context_key == context_key)
        .order_by(AIHelperMessage.created_at.asc(), AIHelperMessage.id.asc())
    )
    return list(session.exec(statement))


def clear_history(session: Session, user_id: int, context_key: str) -> None:
    session.exec(
        delete(AIHelperMessage).where(
            AIHelperMessage.user_id == user_id,
            AIHelperMessage.context_key == context_key,
        )
    )


def _recent_terminal_evidence(session: Session, user_id: int, lesson_key: str | None) -> str:
    if not lesson_key:
        return ""
    statement = (
        select(TerminalRun)
        .where(TerminalRun.user_id == user_id, TerminalRun.lesson_key == lesson_key)
        .order_by(TerminalRun.created_at.desc(), TerminalRun.id.desc())
        .limit(3)
    )
    runs = list(session.exec(statement))
    if not runs:
        return ""
    lines = ["Последние команды пользователя:"]
    for run in runs:
        cmd = run.normalized_command or run.command_text
        lines.append(f"- $ {cmd} -> exit {run.exit_code if run.exit_code is not None else 'n/a'}")
    return "\n".join(lines)


def _format_history_for_model(history: list[AIHelperMessage]) -> list[dict[str, str]]:
    tail = history[-MAX_HISTORY_MESSAGES:]
    return [{"role": message.role, "content": message.message_text} for message in tail]


def _fallback_reply(context: HelperContext, message: str, socratic_mode: bool, terminal_evidence: str) -> str:
    text = message.lower()
    off_topic_markers = ["погода", "полит", "фильм", "музык", "игр", "рецепт"]
    if any(marker in text for marker in off_topic_markers):
        return "Я помогаю только по текущему курсу и шагу. Вернись к задаче в этом уроке/странице, и я помогу точечно."
    prefix = "Вопросом наводкой: " if socratic_mode else ""
    command_line = ""
    if context.command_hints:
        command_line = f"\nКоманды для старта: {', '.join(context.command_hints)}."
    evidence_line = "\nУчту твой вывод команд из истории." if terminal_evidence else ""
    return (
        f"{prefix}держимся контекста '{context.label}'. "
        "Сформулируй 1 конкретный шаг, который ты хочешь закрыть прямо сейчас."
        f"{command_line}{evidence_line}"
    )


def is_helper_online() -> bool:
    settings = get_settings()
    return settings.ai_helper_enabled and bool(settings.openai_api_key.strip())


def _build_system_prompt(context: HelperContext, socratic_mode: bool, terminal_evidence: str) -> str:
    mode_line = (
        "Режим: сократический. Задавай 1-2 уточняющих вопроса вместо готового решения, если это уместно."
        if socratic_mode
        else "Режим: обычный. Дай краткий прямой ответ."
    )
    command_line = (
        f"Если релевантно, предложи 1-3 команды: {', '.join(context.command_hints)}."
        if context.command_hints
        else "Если релевантно, предложи 1-2 безопасные команды для проверки гипотезы."
    )
    evidence_line = terminal_evidence if terminal_evidence else "История команд пока пустая."
    return (
        "Ты Lain AI Helper v1.0 внутри LMS.\n"
        "Всегда отвечай только на русском.\n"
        "Отвечай кратко: максимум 6 предложений.\n"
        "Нельзя выходить за учебный контекст. Если запрос оффтоп — коротко откажи и верни к текущему шагу.\n"
        f"Контекст: {context.scope_summary}\n"
        f"{mode_line}\n"
        f"{command_line}\n"
        "Разрешен формат: короткий текст + блок команд/действий.\n"
        f"{evidence_line}"
    )


def generate_assistant_reply(
    session: Session,
    *,
    user_id: int,
    context: HelperContext,
    user_message: str,
    socratic_mode: bool,
) -> str:
    settings = get_settings()
    history = get_history(session, user_id, context.key)
    terminal_evidence = _recent_terminal_evidence(session, user_id, context.lesson_key)

    if not is_helper_online():
        return _fallback_reply(context, user_message, socratic_mode, terminal_evidence)

    payload_messages = [{"role": "system", "content": _build_system_prompt(context, socratic_mode, terminal_evidence)}]
    payload_messages.extend(_format_history_for_model(history))
    payload_messages.append({"role": "user", "content": user_message})

    try:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.ai_helper_model,
                "messages": payload_messages,
                "temperature": 0.2,
            },
            timeout=settings.ai_helper_timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return (content or "").strip() or _fallback_reply(context, user_message, socratic_mode, terminal_evidence)
    except Exception:
        return _fallback_reply(context, user_message, socratic_mode, terminal_evidence)


def create_chat_turn(
    session: Session,
    *,
    user_id: int,
    context: HelperContext,
    user_message: str,
    socratic_mode: bool,
) -> tuple[AIHelperMessage, AIHelperMessage]:
    user_row = AIHelperMessage(
        user_id=user_id,
        context_key=context.key,
        context_label=context.label,
        role="user",
        message_text=user_message.strip(),
        socratic_mode=socratic_mode,
    )
    session.add(user_row)
    session.flush()

    assistant_text = generate_assistant_reply(
        session,
        user_id=user_id,
        context=context,
        user_message=user_message.strip(),
        socratic_mode=socratic_mode,
    )
    assistant_row = AIHelperMessage(
        user_id=user_id,
        context_key=context.key,
        context_label=context.label,
        role="assistant",
        message_text=assistant_text,
        socratic_mode=socratic_mode,
    )
    session.add(assistant_row)
    session.flush()
    return user_row, assistant_row


def serialize_message(message: AIHelperMessage) -> dict[str, str | int | bool]:
    return {
        "id": message.id or 0,
        "role": message.role,
        "text": message.message_text,
        "socratic_mode": message.socratic_mode,
        "created_at": message.created_at.isoformat() if isinstance(message.created_at, datetime) else "",
    }
