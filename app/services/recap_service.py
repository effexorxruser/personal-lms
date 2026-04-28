from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.content_loader import LessonContent
from app.content_registry import get_content_registry
from app.models import LessonProgress, ReviewResult, StuckEvent, TaskSubmission
from app.services.progress_service import ProgressSnapshot, ensure_progress_initialized
from app.services.stuck_service import latest_open_stuck_event, reason_label
from app.services.submission_service import STATUS_LABELS


@dataclass(frozen=True)
class RecapItem:
    title: str
    meta: str


@dataclass(frozen=True)
class WeeklyRecap:
    since: datetime
    until: datetime
    completed_lessons: list[RecapItem]
    submissions: list[RecapItem]
    reviews: list[RecapItem]
    stuck_events: list[RecapItem]
    next_focus_title: str
    next_focus_href: str | None
    active_stuck: StuckEvent | None

    @property
    def completed_count(self) -> int:
        return len(self.completed_lessons)

    @property
    def submission_count(self) -> int:
        return len(self.submissions)

    @property
    def review_count(self) -> int:
        return len(self.reviews)

    @property
    def stuck_count(self) -> int:
        return len(self.stuck_events)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _lesson_title(lesson_key: str) -> str:
    registry = get_content_registry()
    lesson = registry.lessons.get(lesson_key)
    return lesson.title if lesson else lesson_key


def _task_title(task_slug: str) -> str:
    registry = get_content_registry()
    task = registry.tasks.get(task_slug)
    return task.title if task else task_slug


def _format_date(value: datetime | None) -> str:
    if value is None:
        return "без даты"
    return value.strftime("%d.%m")


def _state_label(state: str) -> str:
    return STATUS_LABELS.get(state, state)


def build_weekly_recap(
    session: Session,
    user_id: int,
    course_slug: str,
    snapshot: ProgressSnapshot | None = None,
) -> WeeklyRecap:
    until = _now()
    since = until - timedelta(days=7)
    snapshot = snapshot or ensure_progress_initialized(session, user_id, course_slug)

    completed_rows = session.exec(
        select(LessonProgress)
        .where(
            LessonProgress.user_id == user_id,
            LessonProgress.status == "completed",
            LessonProgress.completed_at >= since,
        )
        .order_by(LessonProgress.completed_at.desc())
    ).all()

    submission_rows = session.exec(
        select(TaskSubmission)
        .where(
            TaskSubmission.user_id == user_id,
            TaskSubmission.created_at >= since,
        )
        .order_by(TaskSubmission.created_at.desc(), TaskSubmission.id.desc())
    ).all()

    submission_ids = [row.id for row in submission_rows if row.id is not None]
    review_rows: list[ReviewResult] = []
    if submission_ids:
        review_rows = session.exec(
            select(ReviewResult)
            .where(
                ReviewResult.submission_id.in_(submission_ids),
                ReviewResult.created_at >= since,
            )
            .order_by(ReviewResult.created_at.desc(), ReviewResult.id.desc())
        ).all()

    stuck_rows = session.exec(
        select(StuckEvent)
        .where(
            StuckEvent.user_id == user_id,
            StuckEvent.created_at >= since,
        )
        .order_by(StuckEvent.created_at.desc(), StuckEvent.id.desc())
    ).all()

    completed = [
        RecapItem(title=_lesson_title(row.lesson_key), meta=f"завершено {_format_date(row.completed_at)}")
        for row in completed_rows
    ]
    submissions = [
        RecapItem(title=_task_title(row.task_slug), meta=f"{_state_label(row.status)} / {_format_date(row.created_at)}")
        for row in submission_rows
    ]
    reviews = [
        RecapItem(title=_task_title(row.task_slug), meta=f"{_state_label(row.verdict)} / {_format_date(row.created_at)}")
        for row in review_rows
    ]
    stuck_events = [
        RecapItem(
            title=_lesson_title(row.lesson_key),
            meta=f"{reason_label(row.reason_code)} / {row.status} / {_format_date(row.created_at)}",
        )
        for row in stuck_rows
    ]

    next_lesson: LessonContent | None = None
    if snapshot.next_lesson_key:
        next_lesson = get_content_registry().lessons.get(snapshot.next_lesson_key)

    next_focus_title = next_lesson.title if next_lesson else "Курс завершён, можно повторить материалы"
    next_focus_href = f"/lessons/{next_lesson.key}" if next_lesson else None

    return WeeklyRecap(
        since=since,
        until=until,
        completed_lessons=completed,
        submissions=submissions,
        reviews=reviews,
        stuck_events=stuck_events,
        next_focus_title=next_focus_title,
        next_focus_href=next_focus_href,
        active_stuck=latest_open_stuck_event(session, user_id, None),
    )
