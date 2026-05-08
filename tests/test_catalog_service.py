from __future__ import annotations

from app.content_loader import ContentIndex, CourseContent
from app.services.catalog_service import list_learner_visible_course_cards


def _course(slug: str, *, status: str = "available") -> CourseContent:
    return CourseContent(
        slug=slug,
        title=f"{slug} title",
        description=f"{slug} description",
        version="1.0.0",
        estimated_weeks=4,
        status=status,
        level="beginner",
        duration_weeks=None,
        tags=["python"],
        outcomes=[],
        prerequisites=[],
        module_order=[],
        modules=[],
    )


def _index(*courses: CourseContent) -> ContentIndex:
    return ContentIndex(
        courses={course.slug: course for course in courses},
        lessons={},
        lesson_order=[],
        tasks={},
        checkpoints={},
    )


def test_catalog_service_returns_only_available_courses() -> None:
    cards = list_learner_visible_course_cards(
        _index(
            _course("available-course"),
            _course("draft-course", status="draft"),
            _course("archived-course", status="archived"),
        )
    )

    assert [card.slug for card in cards] == ["available-course"]


def test_catalog_service_handles_empty_index() -> None:
    assert list_learner_visible_course_cards(_index()) == []
