from __future__ import annotations

from dataclasses import dataclass

from app.content_loader import ContentIndex
from app.content_registry import get_content_registry

LEARNER_VISIBLE_STATUS = "available"


@dataclass(frozen=True)
class CourseCard:
    slug: str
    title: str
    description: str
    status: str
    level: str
    duration_weeks: int | None
    tags: list[str]


def course_card_from_content(course) -> CourseCard:
    duration_weeks = course.duration_weeks if course.duration_weeks is not None else course.estimated_weeks
    return CourseCard(
        slug=course.slug,
        title=course.title,
        description=course.description,
        status=course.status or LEARNER_VISIBLE_STATUS,
        level=course.level or "unspecified",
        duration_weeks=duration_weeks if duration_weeks else None,
        tags=list(course.tags),
    )


def list_course_cards(index: ContentIndex | None = None) -> list[CourseCard]:
    registry = index if index is not None else get_content_registry()
    return [
        course_card_from_content(course)
        for course in sorted(registry.courses.values(), key=lambda item: item.title.casefold())
    ]


def list_learner_visible_course_cards(index: ContentIndex | None = None) -> list[CourseCard]:
    return [card for card in list_course_cards(index) if card.status == LEARNER_VISIBLE_STATUS]
