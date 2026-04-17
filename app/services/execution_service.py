from __future__ import annotations

from dataclasses import dataclass

from sqlmodel import Session

from app.content_loader import LessonContent, TaskContent
from app.services.submission_service import SubmissionSnapshot, get_submission_snapshot
from app.services.task_service import resolve_lesson_task


@dataclass(frozen=True)
class LessonExecutionContext:
    task: TaskContent | None
    missing_task_slug: str | None
    submission_snapshot: SubmissionSnapshot
    completion_blocked_reason: str | None = None


@dataclass(frozen=True)
class DashboardExecutionSummary:
    lesson: LessonContent | None
    task: TaskContent | None
    state_label: str
    review_label: str
    href: str | None
    needs_revision: bool


def get_lesson_execution_context(
    session: Session,
    user_id: int,
    lesson: LessonContent,
    completion_blocked_reason: str | None = None,
) -> LessonExecutionContext:
    task_resolution = resolve_lesson_task(lesson)
    submission_snapshot = get_submission_snapshot(session, user_id, lesson)
    return LessonExecutionContext(
        task=task_resolution.task,
        missing_task_slug=task_resolution.missing_slug,
        submission_snapshot=submission_snapshot,
        completion_blocked_reason=completion_blocked_reason,
    )


def can_complete_lesson(session: Session, user_id: int, lesson: LessonContent) -> bool:
    if not lesson.task_slug:
        return True
    task_resolution = resolve_lesson_task(lesson)
    if task_resolution.task is None:
        return False
    return get_submission_snapshot(session, user_id, lesson).is_approved


def dashboard_execution_summary(
    session: Session,
    user_id: int,
    lesson: LessonContent | None,
) -> DashboardExecutionSummary:
    if lesson is None:
        return DashboardExecutionSummary(
            lesson=None,
            task=None,
            state_label="Курс завершён",
            review_label="Нет активной задачи",
            href=None,
            needs_revision=False,
        )

    task_resolution = resolve_lesson_task(lesson)
    if task_resolution.task is None:
        return DashboardExecutionSummary(
            lesson=lesson,
            task=None,
            state_label="Задача не задана",
            review_label="Можно двигаться по уроку",
            href=f"/lessons/{lesson.key}",
            needs_revision=False,
        )

    submission_snapshot = get_submission_snapshot(session, user_id, lesson)
    review_label = (
        submission_snapshot.review.feedback
        if submission_snapshot.review
        else "Submission ещё не отправлен"
    )
    return DashboardExecutionSummary(
        lesson=lesson,
        task=task_resolution.task,
        state_label=submission_snapshot.state_label,
        review_label=review_label,
        href=f"/lessons/{lesson.key}#task",
        needs_revision=submission_snapshot.state == "needs_revision",
    )
