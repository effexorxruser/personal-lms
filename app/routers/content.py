from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.db import get_engine
from app.services.content_service import (
    get_course_or_404,
    get_lesson_or_404,
    lesson_neighbors,
)
from app.services.progress_service import (
    ensure_progress_initialized,
    get_lesson_status,
    mark_lesson_completed,
    mark_lesson_opened,
)

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter()


def _require_auth(request: Request) -> int | RedirectResponse:
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    return int(user_id)


@router.get("/courses/{course_slug}")
def course_map(request: Request, course_slug: str):
    auth_result = _require_auth(request)
    if isinstance(auth_result, RedirectResponse):
        return auth_result
    user_id = auth_result

    course = get_course_or_404(course_slug)
    with Session(get_engine()) as session:
        snapshot = ensure_progress_initialized(session, user_id, course.slug)
        session.commit()

    first_lesson_key = course.modules[0].lessons[0].key if course.modules and course.modules[0].lessons else None
    first_lesson_href = (
        f"/lessons/{snapshot.next_lesson_key}"
        if snapshot.next_lesson_key
        else (f"/lessons/{first_lesson_key}" if first_lesson_key else "/lessons/foundation-intro")
    )

    return templates.TemplateResponse(
        request=request,
        name="course_map.html",
        context={
            "course": course,
            "next_step_key": snapshot.next_lesson_key,
            "lesson_statuses": snapshot.lesson_statuses,
            "progress_pct": snapshot.progress_pct,
            "nav_course_href": f"/courses/{course.slug}",
            "nav_lessons_href": first_lesson_href,
        },
    )


@router.get("/lessons/{lesson_key}")
def lesson_page(request: Request, lesson_key: str):
    auth_result = _require_auth(request)
    if isinstance(auth_result, RedirectResponse):
        return auth_result
    user_id = auth_result

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
    with Session(get_engine()) as session:
        ensure_progress_initialized(session, user_id, lesson.course_slug)
        mark_lesson_opened(session, user_id, lesson.key)
        snapshot = ensure_progress_initialized(session, user_id, lesson.course_slug)
        lesson_status_label = get_lesson_status(session, user_id, lesson.key)
        session.commit()

    return templates.TemplateResponse(
        request=request,
        name="lesson.html",
        context={
            "lesson": lesson,
            "course_title": course.title,
            "module_title": module_title,
            "lesson_status_label": lesson_status_label,
            "is_lesson_completed": lesson_status_label == "завершён",
            "progress_pct": snapshot.progress_pct,
            "prev_lesson_key": prev_lesson_key,
            "next_lesson_key": next_lesson_key,
            "nav_course_href": nav_course_href,
            "nav_lessons_href": nav_lessons_href,
        },
    )


@router.post("/lessons/{lesson_key}/complete")
def complete_lesson(request: Request, lesson_key: str):
    auth_result = _require_auth(request)
    if isinstance(auth_result, RedirectResponse):
        return auth_result
    user_id = auth_result

    lesson = get_lesson_or_404(lesson_key)
    with Session(get_engine()) as session:
        ensure_progress_initialized(session, user_id, lesson.course_slug)
        mark_lesson_completed(session, user_id, lesson.key)
        snapshot = ensure_progress_initialized(session, user_id, lesson.course_slug)
        session.commit()

    if snapshot.next_lesson_key and snapshot.next_lesson_key != lesson.key:
        return RedirectResponse(url=f"/lessons/{snapshot.next_lesson_key}", status_code=303)
    return RedirectResponse(url=f"/lessons/{lesson.key}", status_code=303)
