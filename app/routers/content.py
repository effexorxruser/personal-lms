from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.db import get_engine
from app.services.checkpoint_service import (
    checkpoint_course_slug,
    checkpoint_submission_type_label,
    create_checkpoint_submission,
    get_checkpoint,
)
from app.services.content_service import (
    get_active_course_first_lesson_key,
    get_course_or_404,
    get_lesson_or_404,
    lesson_neighbors,
)
from app.services.execution_service import can_complete_lesson, get_lesson_execution_context
from app.services.ai_helper_view import build_ai_helper_view_context
from app.services.progress_service import (
    ensure_progress_initialized,
    get_lesson_status,
    mark_lesson_completed,
    mark_lesson_opened,
)
from app.services.submission_service import create_submission, submission_type_label
from app.services.stuck_service import create_stuck_event, resolve_stuck_event, stuck_context_for_lesson
from app.services.task_service import resolve_lesson_task
from app.services.view_mode import is_mobile_view

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
    mobile_view = is_mobile_view(request)

    course = get_course_or_404(course_slug)
    with Session(get_engine()) as session:
        snapshot = ensure_progress_initialized(session, user_id, course.slug)
        session.commit()
        snapshot = ensure_progress_initialized(session, user_id, course.slug)

    first_lesson_key = course.modules[0].lessons[0].key if course.modules and course.modules[0].lessons else None
    first_lesson_href = (
        f"/lessons/{snapshot.next_lesson_key}"
        if snapshot.next_lesson_key
        else (f"/lessons/{first_lesson_key}" if first_lesson_key else "/dashboard")
    )
    helper_lesson_key = snapshot.next_lesson_key or first_lesson_key or get_active_course_first_lesson_key()
    return templates.TemplateResponse(
        request=request,
        name="course_map.html",
        context={
            "course": course,
            "next_step_key": snapshot.next_lesson_key,
            "lesson_statuses": snapshot.lesson_statuses,
            "module_statuses": snapshot.module_statuses,
            "module_checkpoint_snapshots": snapshot.module_checkpoint_snapshots,
            "checkpoint_submission_type_label": checkpoint_submission_type_label,
            "progress_pct": snapshot.progress_pct,
            "nav_course_href": f"/courses/{course.slug}",
            "nav_lessons_href": first_lesson_href,
            "mobile_view": mobile_view,
            **build_ai_helper_view_context(lesson_key=helper_lesson_key),
        },
    )


@router.get("/lessons/{lesson_key}")
def lesson_page(request: Request, lesson_key: str):
    auth_result = _require_auth(request)
    if isinstance(auth_result, RedirectResponse):
        return auth_result
    user_id = auth_result
    mobile_view = is_mobile_view(request)

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
        lesson_status_label = snapshot.lesson_statuses.get(lesson.key, get_lesson_status(session, user_id, lesson.key))
        session.commit()

    with Session(get_engine()) as session:
        execution = get_lesson_execution_context(
            session,
            user_id,
            lesson,
            completion_blocked_reason=request.query_params.get("completion_blocked"),
        )
        stuck_context = stuck_context_for_lesson(
            session,
            user_id,
            lesson,
            execution.task,
            prev_lesson_key,
            next_lesson_key,
        )
    return templates.TemplateResponse(
        request=request,
        name="lesson.html",
        context={
            "lesson": lesson,
            "course_title": course.title,
            "module_title": module_title,
            "lesson_status_label": lesson_status_label,
            "is_lesson_completed": lesson_status_label == "завершён",
            "execution": execution,
            "submission_type_label": submission_type_label(
                execution.task.submission_type if execution.task else None
            ),
            "stuck_context": stuck_context,
            "progress_pct": snapshot.progress_pct,
            "prev_lesson_key": prev_lesson_key,
            "next_lesson_key": next_lesson_key,
            "nav_course_href": nav_course_href,
            "nav_lessons_href": nav_lessons_href,
            "mobile_view": mobile_view,
            **build_ai_helper_view_context(lesson_key=lesson.key),
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
        if not can_complete_lesson(session, user_id, lesson):
            session.commit()
            return RedirectResponse(
                url=f"/lessons/{lesson.key}?completion_blocked=review_required#task",
                status_code=303,
            )
        mark_lesson_completed(session, user_id, lesson.key)
        snapshot = ensure_progress_initialized(session, user_id, lesson.course_slug)
        session.commit()

    if snapshot.next_lesson_key and snapshot.next_lesson_key != lesson.key:
        return RedirectResponse(url=f"/lessons/{snapshot.next_lesson_key}", status_code=303)
    return RedirectResponse(url=f"/lessons/{lesson.key}", status_code=303)


@router.post("/lessons/{lesson_key}/submissions")
def submit_lesson_task(
    request: Request,
    lesson_key: str,
    submission_type: str = Form(...),
    content_text: str = Form(default=""),
    content_link: str = Form(default=""),
):
    auth_result = _require_auth(request)
    if isinstance(auth_result, RedirectResponse):
        return auth_result
    user_id = auth_result

    lesson = get_lesson_or_404(lesson_key)
    task_resolution = resolve_lesson_task(lesson)
    if task_resolution.task is None:
        return RedirectResponse(url=f"/lessons/{lesson.key}?submission_error=task_missing#task", status_code=303)

    with Session(get_engine()) as session:
        ensure_progress_initialized(session, user_id, lesson.course_slug)
        try:
            create_submission(
                session=session,
                user_id=user_id,
                lesson=lesson,
                task=task_resolution.task,
                submission_type=submission_type,
                content_text=content_text,
                content_link=content_link,
            )
        except ValueError:
            session.rollback()
            return RedirectResponse(
                url=f"/lessons/{lesson.key}?submission_error=invalid_submission#task",
                status_code=303,
            )
        ensure_progress_initialized(session, user_id, lesson.course_slug)
        session.commit()

    return RedirectResponse(url=f"/lessons/{lesson.key}#task", status_code=303)


@router.post("/checkpoints/{checkpoint_slug}/submissions")
def submit_checkpoint(
    request: Request,
    checkpoint_slug: str,
    submission_type: str = Form(...),
    content_text: str = Form(default=""),
    content_link: str = Form(default=""),
):
    auth_result = _require_auth(request)
    if isinstance(auth_result, RedirectResponse):
        return auth_result
    user_id = auth_result

    checkpoint = get_checkpoint(checkpoint_slug)
    if checkpoint is None:
        return RedirectResponse(url="/dashboard", status_code=303)
    course_slug = checkpoint_course_slug(checkpoint)
    if course_slug is None:
        return RedirectResponse(url="/dashboard", status_code=303)

    with Session(get_engine()) as session:
        try:
            create_checkpoint_submission(
                session=session,
                user_id=user_id,
                checkpoint=checkpoint,
                submission_type=submission_type,
                content_text=content_text,
                content_link=content_link,
            )
        except ValueError:
            session.rollback()
            return RedirectResponse(
                url="/dashboard?checkpoint_error=invalid_submission",
                status_code=303,
            )
        ensure_progress_initialized(session, user_id, course_slug)
        session.commit()

    return RedirectResponse(
        url=f"/courses/{course_slug}#checkpoint-{checkpoint.slug}",
        status_code=303,
    )


@router.post("/lessons/{lesson_key}/stuck")
def mark_lesson_stuck(
    request: Request,
    lesson_key: str,
    reason_code: str = Form(...),
    note: str = Form(default=""),
):
    auth_result = _require_auth(request)
    if isinstance(auth_result, RedirectResponse):
        return auth_result
    user_id = auth_result

    lesson = get_lesson_or_404(lesson_key)
    with Session(get_engine()) as session:
        ensure_progress_initialized(session, user_id, lesson.course_slug)
        try:
            create_stuck_event(session, user_id, lesson, reason_code, note)
        except ValueError:
            session.rollback()
            return RedirectResponse(url=f"/lessons/{lesson.key}?stuck_error=invalid_reason#stuck", status_code=303)
        session.commit()

    return RedirectResponse(url=f"/lessons/{lesson.key}#stuck", status_code=303)


@router.post("/stuck/{event_id}/resolve")
def resolve_stuck(request: Request, event_id: int):
    auth_result = _require_auth(request)
    if isinstance(auth_result, RedirectResponse):
        return auth_result
    user_id = auth_result

    redirect_to = request.headers.get("referer") or "/dashboard"
    with Session(get_engine()) as session:
        resolve_stuck_event(session, user_id, event_id)
        session.commit()

    return RedirectResponse(url=redirect_to, status_code=303)
