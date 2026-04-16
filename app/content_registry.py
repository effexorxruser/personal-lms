from __future__ import annotations

from functools import lru_cache

from app.content_loader import ContentIndex, load_content_index


@lru_cache
def get_content_registry() -> ContentIndex:
    return load_content_index()


def get_next_lesson_key(lesson_key: str) -> str | None:
    registry = get_content_registry()
    try:
        index = registry.lesson_order.index(lesson_key)
    except ValueError:
        return None

    next_index = index + 1
    if next_index >= len(registry.lesson_order):
        return None
    return registry.lesson_order[next_index]


def get_prev_lesson_key(lesson_key: str) -> str | None:
    registry = get_content_registry()
    try:
        index = registry.lesson_order.index(lesson_key)
    except ValueError:
        return None

    prev_index = index - 1
    if prev_index < 0:
        return None
    return registry.lesson_order[prev_index]
