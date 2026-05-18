from __future__ import annotations

from functools import lru_cache

from app.content_loader import ContentIndex, load_content_index


@lru_cache
def get_content_registry() -> ContentIndex:
    return load_content_index()


def _lesson_keys_for_course(course_slug: str) -> list[str]:
    registry = get_content_registry()
    course = registry.courses.get(course_slug)
    if not course:
        return []
    keys: list[str] = []
    for module in course.modules:
        keys.extend(module.lesson_keys)
    return keys


def get_next_lesson_key(lesson_key: str) -> str | None:
    lesson = get_content_registry().lessons.get(lesson_key)
    if lesson is None:
        return None
    ordered = _lesson_keys_for_course(lesson.course_slug)
    try:
        index = ordered.index(lesson_key)
    except ValueError:
        return None
    next_index = index + 1
    if next_index >= len(ordered):
        return None
    return ordered[next_index]


def get_prev_lesson_key(lesson_key: str) -> str | None:
    lesson = get_content_registry().lessons.get(lesson_key)
    if lesson is None:
        return None
    ordered = _lesson_keys_for_course(lesson.course_slug)
    try:
        index = ordered.index(lesson_key)
    except ValueError:
        return None
    prev_index = index - 1
    if prev_index < 0:
        return None
    return ordered[prev_index]
