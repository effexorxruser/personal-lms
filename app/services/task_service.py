from __future__ import annotations

from dataclasses import dataclass

from app.content_loader import LessonContent, TaskContent
from app.content_registry import get_content_registry


@dataclass(frozen=True)
class TaskResolution:
    task: TaskContent | None
    missing_slug: str | None = None


def get_task(task_slug: str | None) -> TaskContent | None:
    if not task_slug:
        return None
    return get_content_registry().tasks.get(task_slug)


def resolve_lesson_task(lesson: LessonContent) -> TaskResolution:
    if not lesson.task_slug:
        return TaskResolution(task=None)

    task = get_task(lesson.task_slug)
    if task is None:
        return TaskResolution(task=None, missing_slug=lesson.task_slug)
    return TaskResolution(task=task)
