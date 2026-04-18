from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    display_name: str
    password_hash: str
    role: str = Field(default="learner")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CourseProgress(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "course_slug", name="uq_course_progress_user_course"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    course_slug: str = Field(index=True)
    status: str = Field(default="not_started")
    current_module_slug: str | None = None
    current_lesson_slug: str | None = None
    progress_pct: int = Field(default=0)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None


class LessonProgress(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "lesson_key", name="uq_lesson_progress_user_lesson"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    lesson_key: str = Field(index=True)
    status: str = Field(default="not_started")
    opened_count: int = Field(default=0)
    started_at: datetime | None = None
    last_opened_at: datetime | None = None
    completed_at: datetime | None = None


class TaskSubmission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    lesson_key: str = Field(index=True)
    task_slug: str = Field(index=True)
    submission_type: str
    content_text: str | None = None
    content_link: str | None = None
    status: str = Field(default="submitted", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReviewResult(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    submission_id: int = Field(index=True, foreign_key="tasksubmission.id")
    task_slug: str = Field(index=True)
    verdict: str = Field(index=True)
    feedback: str
    blocking_reason: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CheckpointSubmission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    course_slug: str = Field(index=True)
    module_slug: str = Field(index=True)
    checkpoint_slug: str = Field(index=True)
    submission_type: str
    content_text: str | None = None
    content_link: str | None = None
    status: str = Field(default="submitted", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CheckpointReview(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    submission_id: int = Field(index=True, foreign_key="checkpointsubmission.id")
    checkpoint_slug: str = Field(index=True)
    verdict: str = Field(index=True)
    feedback: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StuckEvent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    course_slug: str = Field(index=True)
    lesson_key: str = Field(index=True)
    task_slug: str | None = Field(default=None, index=True)
    reason_code: str = Field(index=True)
    note: str | None = None
    status: str = Field(default="open", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: datetime | None = None


class TerminalRun(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    lesson_key: str = Field(index=True)
    task_slug: str | None = Field(default=None, index=True)
    command_text: str
    normalized_command: str
    exit_code: int | None = None
    stdout_text: str = ""
    stderr_text: str = ""
    status: str = Field(default="completed", index=True)
    duration_ms: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
