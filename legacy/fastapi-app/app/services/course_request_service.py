from __future__ import annotations

import json
from datetime import datetime, timezone
from sqlmodel import Session, select

from app.models import CourseRequest


COURSE_REQUEST_STATUSES = (
    "submitted",
    "reviewing",
    "accepted",
    "rejected",
    "implemented",
)

CONTRACT_FILENAME = "COURSE_PACK_CONTRACT.md"
CONTRACT_PATH = f"docs/course_authoring/{CONTRACT_FILENAME}"


_ALLOWED_STATUS_TRANSITIONS: dict[str, frozenset[str]] = {
    "submitted": frozenset({"reviewing", "accepted", "rejected", "implemented"}),
    "reviewing": frozenset({"submitted", "accepted", "rejected", "implemented"}),
    "accepted": frozenset({"reviewing", "rejected", "implemented"}),
    "rejected": frozenset(),
    "implemented": frozenset(),
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def topics_from_multiline(raw: str) -> list[str]:
    lines = [line.strip() for line in raw.replace("\r\n", "\n").split("\n")]
    return [line for line in lines if line]


def topics_to_json(strings: list[str]) -> str:
    return json.dumps(strings, ensure_ascii=False, separators=(",", ":"))


def decode_json_list(blob: str) -> list[str]:
    try:
        data = json.loads(blob or "[]")
    except json.JSONDecodeError:
        return []
    if isinstance(data, list):
        out: list[str] = []
        for item in data:
            if isinstance(item, str) and item.strip():
                out.append(item.strip())
        return out
    return []


def create_course_request(
    session: Session,
    *,
    user_id: int,
    title: str,
    goal: str,
    current_level: str,
    duration_weeks: int,
    preferred_format: str,
    required_topics_text: str,
    excluded_topics_text: str,
    expected_artifacts_text: str,
) -> CourseRequest:
    row = CourseRequest(
        user_id=user_id,
        title=title.strip(),
        goal=goal.strip(),
        current_level=current_level.strip(),
        duration_weeks=duration_weeks,
        preferred_format=preferred_format.strip(),
        required_topics_json=topics_to_json(topics_from_multiline(required_topics_text)),
        excluded_topics_json=topics_to_json(topics_from_multiline(excluded_topics_text)),
        expected_artifacts_json=topics_to_json(topics_from_multiline(expected_artifacts_text)),
        status="submitted",
        admin_notes="",
        updated_at=_now(),
    )
    session.add(row)
    session.flush()
    return row


def list_course_requests(
    session: Session,
    *,
    user_id: int | None,
    for_admin: bool,
    status_filter: str | None = None,
) -> list[CourseRequest]:
    if not for_admin:
        assert user_id is not None

    statement = select(CourseRequest).order_by(CourseRequest.created_at.desc())  # type: ignore[union-attr]
    if not for_admin:
        statement = statement.where(CourseRequest.user_id == user_id)  # type: ignore[arg-type]
    if status_filter and status_filter.strip().lower() in COURSE_REQUEST_STATUSES:
        statement = statement.where(CourseRequest.status == status_filter.strip().lower())
    rows = session.exec(statement).all()
    return list(rows)


def get_course_request(
    session: Session,
    request_id: int,
    *,
    scoped_user_id: int | None = None,
) -> CourseRequest | None:
    row = session.get(CourseRequest, request_id)
    if row is None:
        return None
    if scoped_user_id is not None and row.user_id != scoped_user_id:
        return None
    return row


def update_course_request_status(
    session: Session,
    *,
    row: CourseRequest,
    new_status: str,
) -> CourseRequest:
    new_status_norm = new_status.strip().lower()
    if new_status_norm not in COURSE_REQUEST_STATUSES:
        raise ValueError(f"Недопустимый статус: {new_status}")
    allowed = _ALLOWED_STATUS_TRANSITIONS.get(row.status, frozenset())
    if new_status_norm not in allowed:
        raise ValueError(f"Недопустимый переход {row.status!r} -> {new_status_norm!r}")
    row.status = new_status_norm
    row.updated_at = _now()
    session.add(row)
    return row


def update_course_request_admin_notes(
    session: Session,
    *,
    row: CourseRequest,
    notes: str,
) -> CourseRequest:
    row.admin_notes = notes.strip()
    row.updated_at = _now()
    session.add(row)
    return row


def build_chatgpt_course_generation_prompt(course_request: CourseRequest) -> str:
    required = decode_json_list(course_request.required_topics_json)
    excluded = decode_json_list(course_request.excluded_topics_json)
    artifacts = decode_json_list(course_request.expected_artifacts_json)

    def _bullets(xs: list[str]) -> str:
        return "\n".join(f"- {item}" for item in xs) if xs else "(нет)"

    return "\n".join(
        (
            "# Задача: спроектировать курс как Course Pack (authoring в ChatGPT)",
            "",
            "## Краткая заявка",
            f"- Заголовок: {course_request.title}",
            f"- Цель обучения: {course_request.goal}",
            f"- Целевая аудитория / входной уровень: {course_request.current_level}",
            f"- Желаемая длительность (недель): {course_request.duration_weeks}",
            f"- Формат (желание автора заявки): {course_request.preferred_format}",
            "",
            "## Темы которые должны быть в курсе (обязательно)",
            _bullets(required),
            "",
            "## Темы которые исключаем или минимизируем",
            _bullets(excluded),
            "",
            "## Ожидаемые артефакты после прохождения",
            _bullets(artifacts),
            "",
            "## Обязательные требования к источникам и формату результата",
            "- Используй только проверяемые и надёжные источники; для каждой значимой рекомендации укажи ссылку и краткий контекст, откуда взяты сведения.",
            f"- Результат должен полностью соответствовать структуре Course Pack, описанной в **`{CONTRACT_PATH}`** (файл `docs/course_authoring/{CONTRACT_FILENAME}` в репозитории personal-lms). Не добавляй runtime-архитектуры LMS и не «оживляй» контент здесь.",
            "",
            "## Что ты должен выдать пользователю (без упаковки в GitHub)",
            "- `course.yml` на уровень репозитория content pack.",
            "- Файлы `module.yml` и для каждого урока `lesson.md` в согласованной иерархии каталогов.",
            "- Задачи (tasks) и checkpoints (если нужны по contract), с понятными критериями готовности.",
            "- Список sources / reading list для модуля/уроков.",
            "- Краткий блок validation notes: что проверить вручную и какими командами/скриптами валидации personal-lms (например `python scripts/validate_content.py`) после импортa pack.",
            "",
            "## После authoring",
            "Администратор personal-lms перенесёт готовый pack в кодовую базу через отдельный workflow Codex/Cursor (без генерации платформы внутри LMS).",
        ),
    )


def build_codex_cursor_import_prompt(course_request: CourseRequest) -> str:
    slug_hint = "".join(ch if ch.isalnum() or ch == "-" else "-" for ch in course_request.title.lower())[:80]
    return "\n".join(
        (
            "# Инструкция для агента: Codex/Cursor импорт course pack в personal-lms",
            "",
            "## Контекст заявки (не переосмысливать свободным LLM-снапом)",
            f"- Заголовок: {course_request.title}",
            f"- Цель: {course_request.goal}",
            f"- Статус заявки в LMS: {course_request.status} (идентификатор заявки: {course_request.id})",
            "",
            "## Твои жёсткие ограничения",
            "- Работаешь только с **Codex/Cursor**: не предлагай «просто в Cursor», игнорируя Codex; формулировка **Codex/Cursor** охватывает оба инструмента.",
            "- **Не генерируй курс заново** и не переписывай учебную архитектуру с нуля по памяти. Ты уже получил текст course pack из внешнего ChatGPT/Deep Research; встрой его.",
            "- **Не переписывай runtime-платформу personal-lms** (нет FastAPI-рефакторинга ради красоты): только контент каталогов `content/`, при необходимости мелкий wiring, совместимый с текущим loader.",
            "- **Нет GitHub API, auto-commit, auto-PR/auto-merge.** Открой PR вручную через обычный git workflow после проверки.",
            "",
            "## Шаги",
            "1. Размести файлы pack в дереве репозитория согласно `docs/course_authoring/` и `course.yml` верхнего уровня.",
            "2. Сверка со схемой и contract: см. особенно `docs/course_authoring/COURSE_PACK_CONTRACT.md`.",
            "3. Исправь schema/validation ошибки:",
            "   - `python scripts/validate_content.py`",
            "   - при необходимости `python scripts/check_text_integrity.py` и `ruff check .`",
            "4. Прогони `python -m pytest` локально или оставь зелёную траекторию в CI.",
            f"5. Подбери понятный `slug`/ключ курса (например на основе: `{slug_hint}`), не конфликтуя с существующими `content/courses/`.",
            "6. Создай ветку, коммиты и предложи **pull request** (человеческое ревью, без автоматического merge от ботов).",
            "",
            "## Напоминание",
            "- LMS здесь выполняет роль deterministic request tracker; генерация содержательного текста выполняется **вне** этой платформы.",
        ),
    )


