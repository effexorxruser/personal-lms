from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.content_loader import LessonContent, TaskContent
from app.models import ReviewResult, TaskSubmission
from app.services.review_service import VERDICT_APPROVED, create_review_for_submission, get_latest_review_for_submission

SUBMISSION_DRAFT = "draft"
SUBMISSION_SUBMITTED = "submitted"
SUBMISSION_APPROVED = "approved"
SUBMISSION_NEEDS_REVISION = "needs_revision"

STATUS_LABELS = {
    SUBMISSION_DRAFT: "черновик",
    SUBMISSION_SUBMITTED: "отправлено",
    SUBMISSION_APPROVED: "review пройден",
    SUBMISSION_NEEDS_REVISION: "требует доработки",
}

SUPPORTED_SUBMISSION_TYPES = {"text", "link", "command_output"}
SUBMISSION_TYPE_LABELS = {
    "text": "Текстовый отчёт",
    "link": "Ссылка",
    "command_output": "Вывод команды",
}


@dataclass(frozen=True)
class SubmissionSnapshot:
    submission: TaskSubmission | None
    review: ReviewResult | None
    state: str
    state_label: str
    is_approved: bool


def _now() -> datetime:
    return datetime.now(timezone.utc)


def submission_type_label(submission_type: str | None) -> str:
    if not submission_type:
        return "Не задано"
    return SUBMISSION_TYPE_LABELS.get(submission_type, submission_type)


def latest_submission(session: Session, user_id: int, lesson_key: str, task_slug: str) -> TaskSubmission | None:
    statement = (
        select(TaskSubmission)
        .where(
            TaskSubmission.user_id == user_id,
            TaskSubmission.lesson_key == lesson_key,
            TaskSubmission.task_slug == task_slug,
        )
        .order_by(TaskSubmission.updated_at.desc(), TaskSubmission.id.desc())
    )
    return session.exec(statement).first()


def get_submission_snapshot(session: Session, user_id: int, lesson: LessonContent) -> SubmissionSnapshot:
    if not lesson.task_slug:
        return SubmissionSnapshot(
            submission=None,
            review=None,
            state="no_task",
            state_label="без задачи",
            is_approved=True,
        )

    submission = latest_submission(session, user_id, lesson.key, lesson.task_slug)
    if submission is None:
        return SubmissionSnapshot(
            submission=None,
            review=None,
            state="not_submitted",
            state_label="ожидает submission",
            is_approved=False,
        )

    review = get_latest_review_for_submission(session, submission.id)
    state = review.verdict if review else submission.status
    return SubmissionSnapshot(
        submission=submission,
        review=review,
        state=state,
        state_label=STATUS_LABELS.get(state, state),
        is_approved=state == VERDICT_APPROVED,
    )


def create_submission(
    session: Session,
    user_id: int,
    lesson: LessonContent,
    task: TaskContent,
    submission_type: str,
    content_text: str | None,
    content_link: str | None,
) -> SubmissionSnapshot:
    if submission_type not in SUPPORTED_SUBMISSION_TYPES:
        raise ValueError("Unsupported submission type")
    if submission_type != task.submission_type:
        raise ValueError("Submission type does not match task definition")

    current_time = _now()
    submission = TaskSubmission(
        user_id=user_id,
        lesson_key=lesson.key,
        task_slug=task.slug,
        submission_type=submission_type,
        content_text=(content_text or "").strip() or None,
        content_link=(content_link or "").strip() or None,
        status=SUBMISSION_SUBMITTED,
        created_at=current_time,
        updated_at=current_time,
    )
    session.add(submission)
    session.flush()
    review = create_review_for_submission(session, submission)
    return SubmissionSnapshot(
        submission=submission,
        review=review,
        state=review.verdict,
        state_label=STATUS_LABELS.get(review.verdict, review.verdict),
        is_approved=review.verdict == VERDICT_APPROVED,
    )
