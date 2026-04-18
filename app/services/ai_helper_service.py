from __future__ import annotations

from dataclasses import dataclass
import re

import httpx
from sqlmodel import Session

from app.config import Settings, get_settings
from app.models import LainHelperInteraction
from app.services.content_service import get_lesson_or_404
from app.services.execution_service import get_lesson_execution_context
from app.services.stuck_service import latest_open_stuck_event, reason_label

SUPPORTED_AI_HELPER_MODES = {
    "explain_lesson",
    "help_start",
    "stuck_help",
    "submission_hint",
    "free_question",
}

_MODE_GUIDANCE = {
    "explain_lesson": "Кратко объясни текущий урок и зачем он нужен в маршруте.",
    "help_start": "Дай стартовый шаг на 5-10 минут и что проверить после шага.",
    "stuck_help": "Помоги снять блокер и предложи самый маленький следующий шаг.",
    "submission_hint": "Дай подсказку по улучшению черновика submission без готового решения.",
    "free_question": "Ответь только в рамках текущего урока и верни пользователя к execution.",
}

_SCOPE_REFUSAL_PATTERNS = (
    "сделай за меня",
    "сделай вместо меня",
    "реши за меня",
    "дай готовый ответ",
    "дай полный ответ",
    "напиши весь submission",
    "пройди урок за меня",
    "обойди review",
    "закрой урок автоматически",
    "сгенерируй новый курс",
)


@dataclass(frozen=True)
class LainHelperResult:
    status: str
    lesson_key: str
    mode: str
    assistant_message: str
    interaction_id: int | None


class LainHelperError(ValueError):
    pass


def _clip(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    return value[:max_chars].rstrip() + "\n..."


def _tokenize(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Zа-яА-Я0-9_]+", value.lower()) if len(token) >= 3}


def _mode_instruction(mode: str) -> str:
    return _MODE_GUIDANCE.get(mode, _MODE_GUIDANCE["free_question"])


def _scope_fallback_message(lesson_title: str) -> str:
    return (
        "Это выходит за рамки текущего шага.\n"
        f"Сейчас держим фокус на уроке: {lesson_title}.\n"
        "Давай зафиксируем один следующий практический шаг по этому уроку и вернемся к выполнению."
    )


def _disabled_message(lesson_title: str) -> str:
    return (
        "Lain сейчас отключена конфигурацией.\n"
        f"Продолжай по уроку: {lesson_title}.\n"
        "Если нужно, открой блок «Блокер» и зафиксируй, где именно остановился."
    )


def _missing_key_message(lesson_title: str) -> str:
    return (
        "Lain сейчас недоступна: не задан API ключ.\n"
        f"Фокус урока: {lesson_title}.\n"
        "Сделай минимальный следующий шаг и вернись к задаче, затем можно повторить запрос."
    )


def _provider_error_message(lesson_title: str) -> str:
    return (
        "Не удалось получить ответ Lain прямо сейчас.\n"
        f"Остаемся в контексте урока: {lesson_title}.\n"
        "Сделай один короткий шаг по задаче и повтори запрос через минуту."
    )


def _build_context_text(
    lesson_title: str,
    lesson_summary: str,
    lesson_objectives: list[str],
    lesson_checklist: list[str],
    lesson_body_markdown: str,
    task_title: str | None,
    task_summary: str | None,
    task_instructions: str | None,
    task_definition_of_done: list[str],
    task_hints: list[str],
    submission_state_label: str,
    review_feedback: str | None,
    active_stuck_label: str | None,
    active_stuck_note: str | None,
) -> str:
    objectives = "\n".join(f"- {item}" for item in lesson_objectives) or "- не заданы"
    checklist = "\n".join(f"- {item}" for item in lesson_checklist) or "- не задан"
    done = "\n".join(f"- {item}" for item in task_definition_of_done) or "- не задан"
    hints = "\n".join(f"- {item}" for item in task_hints[:4]) or "- нет"
    body = _clip(lesson_body_markdown.strip(), 2600)
    review = review_feedback or "нет"
    stuck_label = active_stuck_label or "нет"
    stuck_note = active_stuck_note or "нет"

    return (
        "=== LESSON CONTEXT ===\n"
        f"Урок: {lesson_title}\n"
        f"Summary: {lesson_summary}\n\n"
        "Цели:\n"
        f"{objectives}\n\n"
        "Чеклист:\n"
        f"{checklist}\n\n"
        "Содержимое урока (сокращено):\n"
        f"{body}\n\n"
        "=== TASK CONTEXT ===\n"
        f"Task title: {task_title or 'нет'}\n"
        f"Task summary: {task_summary or 'нет'}\n"
        f"Task instructions: {task_instructions or 'нет'}\n"
        "Definition of done:\n"
        f"{done}\n"
        "Hints:\n"
        f"{hints}\n\n"
        "=== EXECUTION STATE ===\n"
        f"Submission state: {submission_state_label}\n"
        f"Latest review feedback: {review}\n"
        f"Active stuck reason: {stuck_label}\n"
        f"Active stuck note: {stuck_note}\n"
    )


def _build_system_prompt(mode: str) -> str:
    return (
        "Ты Lain — встроенный AI-тьютор personal-lms. "
        "Тон спокойный, точный, сдержанный, без театральности.\n"
        "Работаешь только в рамках текущего урока и текущей задачи.\n"
        "Запрещено:\n"
        "- писать полный готовый submission за пользователя;\n"
        "- проходить урок вместо пользователя;\n"
        "- обходить review/progress pipeline;\n"
        "- уводить в новый curriculum или общий чат 'обо всем'.\n"
        "Формат ответа: 3-7 коротких предложений.\n"
        "Всегда давай один явный следующий практический шаг.\n"
        f"Режим запроса: {mode}. Инструкция режима: {_mode_instruction(mode)}"
    )


def _build_user_prompt(
    mode: str,
    user_message: str,
    submission_draft: str | None,
    context_text: str,
) -> str:
    safe_message = user_message.strip() or "Нужна помощь по текущему шагу урока."
    draft_block = _clip(submission_draft.strip(), 1200) if submission_draft and submission_draft.strip() else ""
    return (
        f"Mode: {mode}\n"
        f"User request:\n{safe_message}\n\n"
        + (f"Submission draft:\n{draft_block}\n\n" if draft_block else "")
        + context_text
    )


def _extract_openai_text(payload: dict) -> str:
    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    fragments: list[str] = []
    for item in payload.get("output", []):
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if not isinstance(content, dict):
                continue
            candidate = content.get("text") or content.get("output_text")
            if isinstance(candidate, str) and candidate.strip():
                fragments.append(candidate.strip())
    return "\n".join(fragments).strip()


def _request_openai_reply(
    *,
    api_key: str,
    model: str,
    timeout_seconds: int,
    system_prompt: str,
    user_prompt: str,
) -> str:
    response = httpx.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "instructions": system_prompt,
            "input": user_prompt,
            "temperature": 0.2,
            "max_output_tokens": 420,
        },
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    text = _extract_openai_text(response.json())
    if not text:
        raise RuntimeError("Empty AI helper response")
    return text


def _scope_refusal(user_message: str, lesson_title: str, lesson_summary: str, task_title: str | None) -> str | None:
    lowered = user_message.lower()
    if any(pattern in lowered for pattern in _SCOPE_REFUSAL_PATTERNS):
        return _scope_fallback_message(lesson_title)

    if not user_message.strip():
        return None

    anchors = _tokenize(" ".join([lesson_title, lesson_summary, task_title or ""]))
    message_tokens = _tokenize(user_message)
    if message_tokens and anchors and not (message_tokens & anchors) and len(message_tokens) >= 5:
        return _scope_fallback_message(lesson_title)

    return None


def assist_with_lain(
    *,
    session: Session,
    user_id: int,
    lesson_key: str,
    mode: str,
    user_message: str,
    submission_draft: str | None = None,
    settings: Settings | None = None,
) -> LainHelperResult:
    runtime = settings or get_settings()
    normalized_mode = mode.strip().lower()
    if normalized_mode not in SUPPORTED_AI_HELPER_MODES:
        raise LainHelperError("Unsupported helper mode")
    if not lesson_key.strip():
        raise LainHelperError("Lesson key is required")

    lesson = get_lesson_or_404(lesson_key)
    execution = get_lesson_execution_context(session, user_id, lesson)
    active_stuck = latest_open_stuck_event(session, user_id, lesson.course_slug, lesson.key)

    scope_refusal = _scope_refusal(user_message, lesson.title, lesson.summary, execution.task.title if execution.task else None)

    if not runtime.ai_helper_enabled:
        status = "disabled"
        assistant_message = _disabled_message(lesson.title)
    elif scope_refusal:
        status = "guardrail"
        assistant_message = scope_refusal
    elif not runtime.openai_api_key:
        status = "missing_key"
        assistant_message = _missing_key_message(lesson.title)
    else:
        context_text = _build_context_text(
            lesson_title=lesson.title,
            lesson_summary=lesson.summary,
            lesson_objectives=lesson.objectives,
            lesson_checklist=lesson.checklist,
            lesson_body_markdown=lesson.body_markdown,
            task_title=execution.task.title if execution.task else None,
            task_summary=execution.task.summary if execution.task else None,
            task_instructions=execution.task.instructions if execution.task else None,
            task_definition_of_done=execution.task.definition_of_done if execution.task else [],
            task_hints=execution.task.hints if execution.task else [],
            submission_state_label=execution.submission_snapshot.state_label,
            review_feedback=(
                execution.submission_snapshot.review.feedback
                if execution.submission_snapshot.review
                else None
            ),
            active_stuck_label=reason_label(active_stuck.reason_code) if active_stuck else None,
            active_stuck_note=active_stuck.note if active_stuck else None,
        )
        system_prompt = _build_system_prompt(normalized_mode)
        user_prompt = _build_user_prompt(
            mode=normalized_mode,
            user_message=user_message,
            submission_draft=submission_draft,
            context_text=context_text,
        )
        try:
            raw_reply = _request_openai_reply(
                api_key=runtime.openai_api_key,
                model=runtime.ai_helper_model,
                timeout_seconds=runtime.ai_helper_timeout_seconds,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
            assistant_message = _clip(raw_reply.strip(), 1400)
            status = "ok"
        except (httpx.HTTPError, RuntimeError):
            assistant_message = _provider_error_message(lesson.title)
            status = "provider_error"

    interaction = LainHelperInteraction(
        user_id=user_id,
        lesson_key=lesson.key,
        mode=normalized_mode,
        user_message=(user_message or "").strip(),
        assistant_message=assistant_message,
    )
    session.add(interaction)
    session.flush()

    return LainHelperResult(
        status=status,
        lesson_key=lesson.key,
        mode=normalized_mode,
        assistant_message=assistant_message,
        interaction_id=interaction.id,
    )
