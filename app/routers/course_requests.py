from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.db import get_engine
from app.deps.auth import redirect_if_anonymous
from app.services.content_service import get_active_course_first_lesson_key
from app.services.course_request_service import (
    create_course_request,
    decode_json_list,
    get_course_request,
    list_course_requests,
)
from app.services.view_mode import is_mobile_view
from app.web_templates import templates

router = APIRouter(tags=["course-requests"])


def _nav_defaults(request: Request) -> dict:
    first_lesson = get_active_course_first_lesson_key()
    lesson_href = f"/lessons/{first_lesson}" if first_lesson else "/dashboard"
    return {
        "nav_course_href": "/courses",
        "nav_lessons_href": lesson_href,
        "mobile_view": is_mobile_view(request),
    }


@router.get("/course-requests/new")
def course_request_new(request: Request):
    redir = redirect_if_anonymous(request)
    if redir is not None:
        return redir
    ctx = _nav_defaults(request)
    ctx["error_message"] = None
    return templates.TemplateResponse(
        request,
        "course_requests/new.html",
        context=ctx,
    )


@router.post("/course-requests")
def course_request_create(
    request: Request,
    title: str = Form(...),
    goal: str = Form(...),
    current_level: str = Form(...),
    duration_weeks: str = Form(...),
    preferred_format: str = Form(...),
    required_topics: str = Form(default=""),
    excluded_topics: str = Form(default=""),
    expected_artifacts: str = Form(default=""),
):
    redir = redirect_if_anonymous(request)
    if redir is not None:
        return redir
    user_id = int(request.session["user_id"])

    ctx = _nav_defaults(request)

    errors: list[str] = []
    try:
        weeks = int(duration_weeks.strip())
        if weeks < 1:
            errors.append("Срок недель должен быть не менее 1.")
        elif weeks > 520:
            errors.append("Укажите реалистичный срок (не более 520 недель).")
    except ValueError:
        errors.append("Срок недель должен быть целым числом.")

    if not title.strip():
        errors.append("Укажите заголовок.")
    if not goal.strip():
        errors.append("Опишите цель.")
    if not current_level.strip():
        errors.append("Укажите текущий уровень.")

    if errors:
        merged = dict(ctx)
        merged["error_message"] = " ".join(errors)
        merged["form"] = {
            "title": title,
            "goal": goal,
            "current_level": current_level,
            "duration_weeks": duration_weeks,
            "preferred_format": preferred_format,
            "required_topics": required_topics,
            "excluded_topics": excluded_topics,
            "expected_artifacts": expected_artifacts,
        }
        return templates.TemplateResponse(
            request,
            "course_requests/new.html",
            context=merged,
            status_code=400,
        )

    with Session(get_engine()) as session:
        row = create_course_request(
            session,
            user_id=user_id,
            title=title,
            goal=goal,
            current_level=current_level,
            duration_weeks=weeks,
            preferred_format=preferred_format or "Не указано",
            required_topics_text=required_topics,
            excluded_topics_text=excluded_topics,
            expected_artifacts_text=expected_artifacts,
        )
        session.commit()
        new_id = row.id
    return RedirectResponse(url=f"/course-requests/{new_id}", status_code=303)


@router.get("/course-requests")
def course_request_index(request: Request):
    redir = redirect_if_anonymous(request)
    if redir is not None:
        return redir
    user_id = int(request.session["user_id"])

    ctx = _nav_defaults(request)

    with Session(get_engine()) as session:
        items = list_course_requests(session, user_id=user_id, for_admin=False)

    status_labels_ru = {
        "submitted": "Подана на рассмотрение",
        "reviewing": "На проверке",
        "accepted": "Принята к работе",
        "rejected": "Отклонена",
        "implemented": "Внедрено в каталог",
    }
    merged = dict(ctx)
    merged["course_requests_items"] = items
    merged["status_labels"] = status_labels_ru

    return templates.TemplateResponse(request, "course_requests/list.html", context=merged)


@router.get("/course-requests/{request_id}")
def course_request_detail(request: Request, request_id: int):
    redir = redirect_if_anonymous(request)
    if redir is not None:
        return redir
    user_id = int(request.session["user_id"])

    ctx = _nav_defaults(request)

    with Session(get_engine()) as session:
        row = get_course_request(session, request_id, scoped_user_id=user_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Заявка не найдена.")

    merged = dict(ctx)
    merged["course_request"] = row
    merged["status_labels"] = {
        "submitted": "Подана на рассмотрение",
        "reviewing": "На проверке",
        "accepted": "Принята к работе",
        "rejected": "Отклонена",
        "implemented": "Внедрено в каталог",
    }
    merged["topics_required"] = decode_json_list(row.required_topics_json)
    merged["topics_excluded"] = decode_json_list(row.excluded_topics_json)
    merged["artifacts"] = decode_json_list(row.expected_artifacts_json)

    return templates.TemplateResponse(request, "course_requests/detail.html", context=merged)
