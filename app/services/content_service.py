from fastapi import HTTPException

from app.content_registry import get_content_registry, get_next_lesson_key, get_prev_lesson_key

ACTIVE_COURSE_SLUG = "python-backend-ai-foundation"


def get_course_or_404(course_slug: str):
    course = get_content_registry().courses.get(course_slug)
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return course


def get_active_course_or_404():
    return get_course_or_404(ACTIVE_COURSE_SLUG)


def get_active_course_first_lesson_key() -> str | None:
    course = get_content_registry().courses.get(ACTIVE_COURSE_SLUG)
    if not course:
        return None
    for module in course.modules:
        if module.lessons:
            return module.lessons[0].key
    return None


def get_lesson_or_404(lesson_key: str):
    lesson = get_content_registry().lessons.get(lesson_key)
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    return lesson


def lesson_neighbors(lesson_key: str) -> tuple[str | None, str | None]:
    return get_prev_lesson_key(lesson_key), get_next_lesson_key(lesson_key)
