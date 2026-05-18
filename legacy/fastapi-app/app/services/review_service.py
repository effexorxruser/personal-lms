from __future__ import annotations

from dataclasses import dataclass

from sqlmodel import Session, select

from app.models import ReviewResult, TaskSubmission

VERDICT_APPROVED = "approved"
VERDICT_NEEDS_REVISION = "needs_revision"


@dataclass(frozen=True)
class ReviewDecision:
    verdict: str
    feedback: str
    blocking_reason: str | None = None


def _submission_payload(submission: TaskSubmission) -> str:
    return "\n".join(
        item.strip()
        for item in [submission.content_text or "", submission.content_link or ""]
        if item and item.strip()
    )


def evaluate_submission(submission: TaskSubmission) -> ReviewDecision:
    payload = _submission_payload(submission)
    if not payload:
        return ReviewDecision(
            verdict=VERDICT_NEEDS_REVISION,
            feedback="Submission пустой. Добавь результат выполнения задачи и отправь повторно.",
            blocking_reason="empty_submission",
        )

    if submission.submission_type == "link" and submission.content_link:
        if not submission.content_link.startswith(("http://", "https://")):
            return ReviewDecision(
                verdict=VERDICT_NEEDS_REVISION,
                feedback="Ссылка должна начинаться с http:// или https://.",
                blocking_reason="invalid_link",
            )

    if len(payload) < 24:
        return ReviewDecision(
            verdict=VERDICT_NEEDS_REVISION,
            feedback="Submission слишком короткий. Нужен проверяемый результат, а не только отметка о выполнении.",
            blocking_reason="too_short",
        )

    return ReviewDecision(
        verdict=VERDICT_APPROVED,
        feedback="Базовая проверка пройдена. Submission выглядит достаточно конкретным для MVP review.",
    )


def create_review_for_submission(session: Session, submission: TaskSubmission) -> ReviewResult:
    decision = evaluate_submission(submission)
    review = ReviewResult(
        submission_id=submission.id or 0,
        task_slug=submission.task_slug,
        verdict=decision.verdict,
        feedback=decision.feedback,
        blocking_reason=decision.blocking_reason,
    )
    session.add(review)

    submission.status = decision.verdict
    session.add(submission)
    session.flush()
    return review


def get_latest_review_for_submission(session: Session, submission_id: int | None) -> ReviewResult | None:
    if submission_id is None:
        return None

    statement = (
        select(ReviewResult)
        .where(ReviewResult.submission_id == submission_id)
        .order_by(ReviewResult.created_at.desc(), ReviewResult.id.desc())
    )
    return session.exec(statement).first()
