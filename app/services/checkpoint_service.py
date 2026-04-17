from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.content_loader import CheckpointContent
from app.content_registry import get_content_registry
from app.models import CheckpointReview, CheckpointSubmission

CHECKPOINT_SUBMITTED = "submitted"
CHECKPOINT_APPROVED = "approved"
CHECKPOINT_NEEDS_REVISION = "needs_revision"

CHECKPOINT_STATUS_LABELS = {
    "no_checkpoint": "без checkpoint",
    "not_submitted": "checkpoint ожидает отправки",
    CHECKPOINT_SUBMITTED: "checkpoint отправлен",
    CHECKPOINT_APPROVED: "checkpoint пройден",
    CHECKPOINT_NEEDS_REVISION: "требует доработки",
}

SUPPORTED_CHECKPOINT_SUBMISSION_TYPES = {"text", "link", "repository_link", "command_output"}
CHECKPOINT_SUBMISSION_TYPE_LABELS = {
    "text": "Текстовый отчёт",
    "link": "Ссылка",
    "repository_link": "Ссылка на репозиторий",
    "command_output": "Вывод команды",
}


@dataclass(frozen=True)
class CheckpointSnapshot:
    checkpoint: CheckpointContent | None
    latest_submission: CheckpointSubmission | None
    review: CheckpointReview | None
    state: str
    state_label: str
    is_approved: bool


@dataclass(frozen=True)
class CheckpointDecision:
    verdict: str
    feedback: str


def _now() -> datetime:
    return datetime.now(timezone.utc)


def checkpoint_submission_type_label(submission_type: str | None) -> str:
    if not submission_type:
        return "Не задано"
    return CHECKPOINT_SUBMISSION_TYPE_LABELS.get(submission_type, submission_type)


def get_checkpoint(checkpoint_slug: str | None) -> CheckpointContent | None:
    if not checkpoint_slug:
        return None
    return get_content_registry().checkpoints.get(checkpoint_slug)


def checkpoint_course_slug(checkpoint: CheckpointContent) -> str | None:
    for course in get_content_registry().courses.values():
        if checkpoint.module_slug in course.module_order:
            return course.slug
    return None


def resolve_module_checkpoint(module_slug: str) -> CheckpointContent | None:
    registry = get_content_registry()
    for checkpoint in registry.checkpoints.values():
        if checkpoint.module_slug == module_slug:
            return checkpoint
    return None


def latest_checkpoint_submission(
    session: Session,
    user_id: int,
    checkpoint_slug: str,
) -> CheckpointSubmission | None:
    statement = (
        select(CheckpointSubmission)
        .where(
            CheckpointSubmission.user_id == user_id,
            CheckpointSubmission.checkpoint_slug == checkpoint_slug,
        )
        .order_by(CheckpointSubmission.updated_at.desc(), CheckpointSubmission.id.desc())
    )
    return session.exec(statement).first()


def get_latest_checkpoint_review(
    session: Session,
    submission_id: int | None,
) -> CheckpointReview | None:
    if submission_id is None:
        return None
    statement = (
        select(CheckpointReview)
        .where(CheckpointReview.submission_id == submission_id)
        .order_by(CheckpointReview.created_at.desc(), CheckpointReview.id.desc())
    )
    return session.exec(statement).first()


def _checkpoint_payload(submission: CheckpointSubmission) -> str:
    return "\n".join(
        item.strip()
        for item in [submission.content_text or "", submission.content_link or ""]
        if item and item.strip()
    )


def evaluate_checkpoint_submission(submission: CheckpointSubmission) -> CheckpointDecision:
    payload = _checkpoint_payload(submission)
    if not payload:
        return CheckpointDecision(
            verdict=CHECKPOINT_NEEDS_REVISION,
            feedback="Checkpoint submission пустой. Добавь ссылку или описание артефакта и отправь повторно.",
        )

    if submission.submission_type in {"link", "repository_link"}:
        if not submission.content_link:
            return CheckpointDecision(
                verdict=CHECKPOINT_NEEDS_REVISION,
                feedback="Для checkpoint нужен проверяемый link на результат.",
            )
        if not submission.content_link.startswith(("http://", "https://")):
            return CheckpointDecision(
                verdict=CHECKPOINT_NEEDS_REVISION,
                feedback="Ссылка на checkpoint должна начинаться с http:// или https://.",
            )

    if len(payload) < 32:
        return CheckpointDecision(
            verdict=CHECKPOINT_NEEDS_REVISION,
            feedback="Checkpoint submission слишком короткий. Нужен проверяемый артефакт, а не только отметка о выполнении.",
        )

    return CheckpointDecision(
        verdict=CHECKPOINT_APPROVED,
        feedback="Checkpoint принят. Артефакт выглядит достаточно конкретным для MVP review.",
    )


def create_checkpoint_review(
    session: Session,
    submission: CheckpointSubmission,
) -> CheckpointReview:
    decision = evaluate_checkpoint_submission(submission)
    review = CheckpointReview(
        submission_id=submission.id or 0,
        checkpoint_slug=submission.checkpoint_slug,
        verdict=decision.verdict,
        feedback=decision.feedback,
    )
    session.add(review)

    submission.status = decision.verdict
    submission.updated_at = _now()
    session.add(submission)
    session.flush()
    return review


def get_checkpoint_snapshot(
    session: Session,
    user_id: int,
    checkpoint: CheckpointContent | None,
) -> CheckpointSnapshot:
    if checkpoint is None:
        return CheckpointSnapshot(
            checkpoint=None,
            latest_submission=None,
            review=None,
            state="no_checkpoint",
            state_label=CHECKPOINT_STATUS_LABELS["no_checkpoint"],
            is_approved=True,
        )

    submission = latest_checkpoint_submission(session, user_id, checkpoint.slug)
    if submission is None:
        return CheckpointSnapshot(
            checkpoint=checkpoint,
            latest_submission=None,
            review=None,
            state="not_submitted",
            state_label=CHECKPOINT_STATUS_LABELS["not_submitted"],
            is_approved=False,
        )

    review = get_latest_checkpoint_review(session, submission.id)
    state = review.verdict if review else submission.status
    return CheckpointSnapshot(
        checkpoint=checkpoint,
        latest_submission=submission,
        review=review,
        state=state,
        state_label=CHECKPOINT_STATUS_LABELS.get(state, state),
        is_approved=state == CHECKPOINT_APPROVED,
    )


def is_checkpoint_approved(session: Session, user_id: int, checkpoint: CheckpointContent | None) -> bool:
    return get_checkpoint_snapshot(session, user_id, checkpoint).is_approved


def create_checkpoint_submission(
    session: Session,
    user_id: int,
    checkpoint: CheckpointContent,
    submission_type: str,
    content_text: str | None,
    content_link: str | None,
) -> CheckpointSnapshot:
    if submission_type not in SUPPORTED_CHECKPOINT_SUBMISSION_TYPES:
        raise ValueError("Unsupported checkpoint submission type")
    if submission_type != checkpoint.submission_type:
        raise ValueError("Submission type does not match checkpoint definition")

    course_slug = checkpoint_course_slug(checkpoint)
    if course_slug is None:
        raise ValueError("Checkpoint module is not attached to a course")

    current_time = _now()
    submission = CheckpointSubmission(
        user_id=user_id,
        course_slug=course_slug,
        module_slug=checkpoint.module_slug,
        checkpoint_slug=checkpoint.slug,
        submission_type=submission_type,
        content_text=(content_text or "").strip() or None,
        content_link=(content_link or "").strip() or None,
        status=CHECKPOINT_SUBMITTED,
        created_at=current_time,
        updated_at=current_time,
    )
    session.add(submission)
    session.flush()
    review = create_checkpoint_review(session, submission)
    return CheckpointSnapshot(
        checkpoint=checkpoint,
        latest_submission=submission,
        review=review,
        state=review.verdict,
        state_label=CHECKPOINT_STATUS_LABELS.get(review.verdict, review.verdict),
        is_approved=review.verdict == CHECKPOINT_APPROVED,
    )
