from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.content_registry import get_content_registry
from app.models import CourseProgress, LessonProgress
from app.services.checkpoint_service import CheckpointSnapshot, get_checkpoint_snapshot, resolve_module_checkpoint
from app.services.submission_service import get_submission_snapshot

STATUS_NOT_STARTED = "not_started"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"


@dataclass
class ProgressSnapshot:
    course_slug: str
    total_lessons: int
    completed_lessons: int
    progress_pct: int
    next_lesson_key: str | None
    next_lesson_title: str | None
    lesson_statuses: dict[str, str]
    module_statuses: dict[str, str]
    module_checkpoint_snapshots: dict[str, CheckpointSnapshot]
    next_checkpoint_slug: str | None
    next_checkpoint_title: str | None
    next_checkpoint_module_slug: str | None


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _course_lesson_keys(course_slug: str) -> list[str]:
    registry = get_content_registry()
    course = registry.courses.get(course_slug)
    if not course:
        return []

    keys: list[str] = []
    for module in course.modules:
        for lesson in module.lessons:
            keys.append(lesson.key)
    return keys


def _get_or_create_course_progress(session: Session, user_id: int, course_slug: str) -> CourseProgress:
    statement = select(CourseProgress).where(
        CourseProgress.user_id == user_id,
        CourseProgress.course_slug == course_slug,
    )
    course_progress = session.exec(statement).first()
    if course_progress:
        return course_progress

    course_progress = CourseProgress(
        user_id=user_id,
        course_slug=course_slug,
        status=STATUS_NOT_STARTED,
        current_module_slug=None,
        current_lesson_slug=None,
        progress_pct=0,
    )
    session.add(course_progress)
    session.flush()
    return course_progress


def _ensure_lesson_progresses(session: Session, user_id: int, lesson_keys: list[str]) -> None:
    if not lesson_keys:
        return

    statement = select(LessonProgress).where(
        LessonProgress.user_id == user_id,
        LessonProgress.lesson_key.in_(lesson_keys),
    )
    existing = session.exec(statement).all()
    existing_keys = {item.lesson_key for item in existing}

    for lesson_key in lesson_keys:
        if lesson_key in existing_keys:
            continue
        session.add(
            LessonProgress(
                user_id=user_id,
                lesson_key=lesson_key,
                status=STATUS_NOT_STARTED,
                opened_count=0,
            )
        )


def _status_label(status: str) -> str:
    if status == STATUS_COMPLETED:
        return "завершён"
    if status == STATUS_IN_PROGRESS:
        return "в процессе"
    return "доступен"


def _lesson_state_label(session: Session, user_id: int, lesson_key: str, status: str) -> str:
    if status == STATUS_COMPLETED:
        return "завершён"

    registry = get_content_registry()
    lesson = registry.lessons[lesson_key]
    if not lesson.task_slug:
        return _status_label(status)

    submission_snapshot = get_submission_snapshot(session, user_id, lesson)
    if submission_snapshot.state == "needs_revision":
        return "требует доработки"
    if submission_snapshot.state == "approved":
        return "review пройден"
    if submission_snapshot.submission is not None:
        return "отправлено"
    if status == STATUS_IN_PROGRESS:
        return "в процессе"
    return "доступен"


def _compute_snapshot(session: Session, user_id: int, course_slug: str) -> ProgressSnapshot:
    registry = get_content_registry()
    course = registry.courses[course_slug]
    lesson_keys = _course_lesson_keys(course_slug)

    statement = select(LessonProgress).where(
        LessonProgress.user_id == user_id,
        LessonProgress.lesson_key.in_(lesson_keys),
    )
    lesson_progress_rows = session.exec(statement).all()
    by_key = {row.lesson_key: row for row in lesson_progress_rows}

    completed_count = 0
    next_lesson_key: str | None = None
    lesson_statuses: dict[str, str] = {}
    lesson_progress_statuses: dict[str, str] = {}

    for lesson_key in lesson_keys:
        lesson_progress = by_key.get(lesson_key)
        status = lesson_progress.status if lesson_progress else STATUS_NOT_STARTED
        lesson_progress_statuses[lesson_key] = status
        lesson_statuses[lesson_key] = _lesson_state_label(session, user_id, lesson_key, status)

        if status == STATUS_COMPLETED:
            completed_count += 1
        elif next_lesson_key is None:
            next_lesson_key = lesson_key

    total = len(lesson_keys)
    progress_pct = int((completed_count / total) * 100) if total > 0 else 0

    next_lesson_title = None
    if next_lesson_key:
        next_lesson_title = registry.lessons[next_lesson_key].title

    module_statuses: dict[str, str] = {}
    module_checkpoint_snapshots: dict[str, CheckpointSnapshot] = {}
    next_checkpoint_slug: str | None = None
    next_checkpoint_title: str | None = None
    next_checkpoint_module_slug: str | None = None

    for module in course.modules:
        module_lesson_keys = [lesson.key for lesson in module.lessons]
        module_lesson_statuses = [
            lesson_progress_statuses.get(lesson_key, STATUS_NOT_STARTED)
            for lesson_key in module_lesson_keys
        ]
        lessons_completed = bool(module_lesson_statuses) and all(
            status == STATUS_COMPLETED for status in module_lesson_statuses
        )
        lessons_started = any(status != STATUS_NOT_STARTED for status in module_lesson_statuses)

        checkpoint = resolve_module_checkpoint(module.slug)
        checkpoint_snapshot = get_checkpoint_snapshot(session, user_id, checkpoint)
        module_checkpoint_snapshots[module.slug] = checkpoint_snapshot

        if not lessons_completed:
            module_statuses[module.slug] = "в процессе" if lessons_started else "доступен"
            continue

        if checkpoint and not checkpoint_snapshot.is_approved:
            if checkpoint_snapshot.state == "needs_revision":
                module_statuses[module.slug] = "требует доработки"
            else:
                module_statuses[module.slug] = checkpoint_snapshot.state_label
            if next_checkpoint_slug is None:
                next_checkpoint_slug = checkpoint.slug
                next_checkpoint_title = checkpoint.title
                next_checkpoint_module_slug = module.slug
            continue

        module_statuses[module.slug] = "завершён"

    return ProgressSnapshot(
        course_slug=course_slug,
        total_lessons=total,
        completed_lessons=completed_count,
        progress_pct=progress_pct,
        next_lesson_key=next_lesson_key,
        next_lesson_title=next_lesson_title,
        lesson_statuses=lesson_statuses,
        module_statuses=module_statuses,
        module_checkpoint_snapshots=module_checkpoint_snapshots,
        next_checkpoint_slug=next_checkpoint_slug,
        next_checkpoint_title=next_checkpoint_title,
        next_checkpoint_module_slug=next_checkpoint_module_slug,
    )


def _update_course_progress_record(
    session: Session,
    user_id: int,
    course_slug: str,
    snapshot: ProgressSnapshot,
) -> CourseProgress:
    registry = get_content_registry()
    course_progress = _get_or_create_course_progress(session, user_id, course_slug)
    current_time = _now()

    course_progress.progress_pct = snapshot.progress_pct
    course_progress.updated_at = current_time

    modules_completed = bool(snapshot.module_statuses) and all(
        status == "завершён" for status in snapshot.module_statuses.values()
    )

    if (
        snapshot.completed_lessons == snapshot.total_lessons
        and snapshot.total_lessons > 0
        and modules_completed
    ):
        course_progress.status = STATUS_COMPLETED
        course_progress.completed_at = course_progress.completed_at or current_time
        course_progress.current_lesson_slug = None
        course_progress.current_module_slug = None
    else:
        if snapshot.completed_lessons > 0:
            course_progress.status = STATUS_IN_PROGRESS
        else:
            course_progress.status = STATUS_NOT_STARTED
        course_progress.completed_at = None

        if snapshot.next_lesson_key:
            lesson = registry.lessons[snapshot.next_lesson_key]
            course_progress.current_lesson_slug = lesson.key
            course_progress.current_module_slug = lesson.module_slug
        elif snapshot.next_checkpoint_module_slug:
            course_progress.current_lesson_slug = None
            course_progress.current_module_slug = snapshot.next_checkpoint_module_slug

    if course_progress.started_at is None and (
        snapshot.completed_lessons > 0
        or snapshot.next_lesson_key is not None
        or snapshot.next_checkpoint_slug is not None
    ):
        course_progress.started_at = current_time

    session.add(course_progress)
    return course_progress


def ensure_progress_initialized(session: Session, user_id: int, course_slug: str) -> ProgressSnapshot:
    lesson_keys = _course_lesson_keys(course_slug)
    _get_or_create_course_progress(session, user_id, course_slug)
    _ensure_lesson_progresses(session, user_id, lesson_keys)
    snapshot = _compute_snapshot(session, user_id, course_slug)
    _update_course_progress_record(session, user_id, course_slug, snapshot)
    return snapshot


def mark_lesson_opened(session: Session, user_id: int, lesson_key: str) -> None:
    statement = select(LessonProgress).where(
        LessonProgress.user_id == user_id,
        LessonProgress.lesson_key == lesson_key,
    )
    lesson_progress = session.exec(statement).first()
    if not lesson_progress:
        lesson_progress = LessonProgress(
            user_id=user_id,
            lesson_key=lesson_key,
            status=STATUS_NOT_STARTED,
            opened_count=0,
        )

    lesson_progress.opened_count += 1
    lesson_progress.last_opened_at = _now()
    if lesson_progress.started_at is None:
        lesson_progress.started_at = lesson_progress.last_opened_at
    if lesson_progress.status != STATUS_COMPLETED:
        lesson_progress.status = STATUS_IN_PROGRESS

    session.add(lesson_progress)


def mark_lesson_completed(session: Session, user_id: int, lesson_key: str) -> None:
    statement = select(LessonProgress).where(
        LessonProgress.user_id == user_id,
        LessonProgress.lesson_key == lesson_key,
    )
    lesson_progress = session.exec(statement).first()
    if not lesson_progress:
        lesson_progress = LessonProgress(
            user_id=user_id,
            lesson_key=lesson_key,
            status=STATUS_NOT_STARTED,
            opened_count=0,
        )

    current_time = _now()
    lesson_progress.status = STATUS_COMPLETED
    lesson_progress.completed_at = lesson_progress.completed_at or current_time
    lesson_progress.started_at = lesson_progress.started_at or current_time
    lesson_progress.last_opened_at = current_time
    lesson_progress.opened_count = max(1, lesson_progress.opened_count)

    session.add(lesson_progress)


def get_lesson_status(session: Session, user_id: int, lesson_key: str) -> str:
    statement = select(LessonProgress).where(
        LessonProgress.user_id == user_id,
        LessonProgress.lesson_key == lesson_key,
    )
    lesson_progress = session.exec(statement).first()
    if not lesson_progress:
        return _status_label(STATUS_NOT_STARTED)
    return _status_label(lesson_progress.status)
