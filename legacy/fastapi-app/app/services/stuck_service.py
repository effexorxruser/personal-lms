from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.content_loader import LessonContent, TaskContent
from app.models import StuckEvent

STUCK_OPEN = "open"
STUCK_RESOLVED = "resolved"

REASON_LABELS = {
    "unclear_task": "Не понимаю задачу",
    "blocked_by_error": "Уперся в ошибку",
    "missing_context": "Не хватает контекста",
    "review_confusion": "Не понимаю review",
}


@dataclass(frozen=True)
class RecoveryStep:
    title: str
    body: str


@dataclass(frozen=True)
class StuckContext:
    active_event: StuckEvent | None
    reason_options: dict[str, str]
    recovery_steps: list[RecoveryStep]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def reason_label(reason_code: str | None) -> str:
    if not reason_code:
        return "Не указано"
    return REASON_LABELS.get(reason_code, reason_code)


def create_stuck_event(
    session: Session,
    user_id: int,
    lesson: LessonContent,
    reason_code: str,
    note: str | None,
) -> StuckEvent:
    if reason_code not in REASON_LABELS:
        raise ValueError("Unsupported stuck reason")

    event = StuckEvent(
        user_id=user_id,
        course_slug=lesson.course_slug,
        lesson_key=lesson.key,
        task_slug=lesson.task_slug,
        reason_code=reason_code,
        note=(note or "").strip() or None,
        status=STUCK_OPEN,
    )
    session.add(event)
    session.flush()
    return event


def latest_open_stuck_event(
    session: Session,
    user_id: int,
    course_slug: str | None = None,
    lesson_key: str | None = None,
) -> StuckEvent | None:
    statement = select(StuckEvent).where(
        StuckEvent.user_id == user_id,
        StuckEvent.status == STUCK_OPEN,
    )
    if course_slug:
        statement = statement.where(StuckEvent.course_slug == course_slug)
    if lesson_key:
        statement = statement.where(StuckEvent.lesson_key == lesson_key)

    statement = statement.order_by(StuckEvent.created_at.desc(), StuckEvent.id.desc())
    return session.exec(statement).first()


def resolve_stuck_event(session: Session, user_id: int, event_id: int) -> StuckEvent | None:
    event = session.get(StuckEvent, event_id)
    if event is None or event.user_id != user_id:
        return None

    event.status = STUCK_RESOLVED
    event.resolved_at = event.resolved_at or _now()
    session.add(event)
    return event


def recovery_steps_for_lesson(
    lesson: LessonContent,
    task: TaskContent | None,
    prev_lesson_key: str | None,
    next_lesson_key: str | None,
) -> list[RecoveryStep]:
    steps: list[RecoveryStep] = []
    if lesson.objectives:
        steps.append(
            RecoveryStep(
                title="Вернись к цели урока",
                body=lesson.objectives[0],
            )
        )
    if task and task.hints:
        steps.append(
            RecoveryStep(
                title="Открой первую подсказку",
                body=task.hints[0],
            )
        )
    if task and task.definition_of_done:
        steps.append(
            RecoveryStep(
                title="Сверься с definition of done",
                body=task.definition_of_done[0],
            )
        )
    if prev_lesson_key:
        steps.append(
            RecoveryStep(
                title="Сделай шаг назад",
                body="Открой предыдущий урок и проверь, какой контекст мог выпасть.",
            )
        )
    if next_lesson_key:
        steps.append(
            RecoveryStep(
                title="Не перепрыгивай дальше",
                body="Сначала закрой текущий blocker, потом переходи к следующему уроку.",
            )
        )
    return steps[:4]


def stuck_context_for_lesson(
    session: Session,
    user_id: int,
    lesson: LessonContent,
    task: TaskContent | None,
    prev_lesson_key: str | None,
    next_lesson_key: str | None,
) -> StuckContext:
    return StuckContext(
        active_event=latest_open_stuck_event(session, user_id, lesson.course_slug, lesson.key),
        reason_options=REASON_LABELS,
        recovery_steps=recovery_steps_for_lesson(lesson, task, prev_lesson_key, next_lesson_key),
    )
