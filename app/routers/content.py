from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.services.content_service import (
    get_course_or_404,
    get_lesson_or_404,
    lesson_neighbors,
)

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter()


@router.get("/courses/{course_slug}")
def course_map(request: Request, course_slug: str):
    course = get_course_or_404(course_slug)

    first_lesson_key = course.modules[0].lessons[0].key if course.modules and course.modules[0].lessons else None
    first_lesson_href = f"/lessons/{first_lesson_key}" if first_lesson_key else "/lessons/foundation-intro"

    return templates.TemplateResponse(
        request=request,
        name="course_map.html",
        context={
            "course": course,
            "next_step_key": first_lesson_key,
            "nav_course_href": f"/courses/{course.slug}",
            "nav_lessons_href": first_lesson_href,
        },
    )


@router.get("/lessons/{lesson_key}")
def lesson_page(request: Request, lesson_key: str):
    lesson = get_lesson_or_404(lesson_key)
    prev_lesson_key, next_lesson_key = lesson_neighbors(lesson_key)
    nav_course_href = f"/courses/{lesson.course_slug}"
    nav_lessons_href = f"/lessons/{lesson.key}"
    course = get_course_or_404(lesson.course_slug)
    module_title = next(
        (
            module.title
            for module in course.modules
            if module.slug == lesson.module_slug
        ),
        "Учебный модуль",
    )

    return templates.TemplateResponse(
        request=request,
        name="lesson.html",
        context={
            "lesson": lesson,
            "course_title": course.title,
            "module_title": module_title,
            "prev_lesson_key": prev_lesson_key,
            "next_lesson_key": next_lesson_key,
            "nav_course_href": nav_course_href,
            "nav_lessons_href": nav_lessons_href,
        },
    )
