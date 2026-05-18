from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.db import get_engine
from app.deps.auth import ensure_admin_web
from app.models import CourseRequest, User
from app.services.content_service import get_active_course_first_lesson_key
from app.services.course_request_service import (
    COURSE_REQUEST_STATUSES,
    build_chatgpt_course_generation_prompt,
    build_codex_cursor_import_prompt,
    decode_json_list,
    get_course_request,
    list_course_requests,
    update_course_request_admin_notes,
    update_course_request_status,
)
from app.services.view_mode import is_mobile_view
from app.web_templates import templates

router = APIRouter(tags=["admin-course-requests"])


def _nav_defaults(request: Request) -> dict:
    first_lesson = get_active_course_first_lesson_key()
    lesson_href = f"/lessons/{first_lesson}" if first_lesson else "/dashboard"
    return {
        "nav_course_href": "/courses",
        "nav_lessons_href": lesson_href,
        "mobile_view": is_mobile_view(request),
    }


STATUS_LABELS_RU = {
    "submitted": "Подана на рассмотрение",
    "reviewing": "На проверке",
    "accepted": "Принята к работе",
    "rejected": "Отклонена",
    "implemented": "Внедрено в каталог",
}


@router.get("/admin/course-requests")
def admin_course_request_list(request: Request):
    status_filter = request.query_params.get("status")

    username_map: dict[int, str] = {}
    items: list[CourseRequest] = []

    with Session(get_engine()) as session:
        redir = ensure_admin_web(request, session)
        if redir is not None:
            return redir

        items = list_course_requests(session, user_id=None, for_admin=True, status_filter=status_filter or None)
        user_ids = {r.user_id for r in items}
        if user_ids:
            users = session.exec(select(User).where(User.id.in_(user_ids))).all()
            username_map = {u.id: u.username for u in users}

    merged = dict(_nav_defaults(request))
    merged["admin_course_request_rows"] = items
    merged["username_by_user_id"] = username_map
    merged["status_labels"] = STATUS_LABELS_RU
    merged["status_enum"] = COURSE_REQUEST_STATUSES
    merged["current_filter"] = (status_filter or "").strip()

    return templates.TemplateResponse(request, "admin/course_requests/list.html", context=merged)


@router.get("/admin/course-requests/{request_id}")
def admin_course_request_detail(request: Request, request_id: int):
    with Session(get_engine()) as session:
        redir = ensure_admin_web(request, session)
        if redir is not None:
            return redir

        row = get_course_request(session, request_id, scoped_user_id=None)
        if row is None:
            raise HTTPException(status_code=404, detail="Заявка не найдена.")
        submitter = session.get(User, row.user_id)
        submitter_label = submitter.username if submitter else f"id={row.user_id}"

    merged = dict(_nav_defaults(request))
    merged["course_request"] = row
    merged["requester_username"] = submitter_label
    merged["status_labels"] = STATUS_LABELS_RU
    merged["topics_required"] = decode_json_list(row.required_topics_json)
    merged["topics_excluded"] = decode_json_list(row.excluded_topics_json)
    merged["artifacts"] = decode_json_list(row.expected_artifacts_json)
    merged["chatgpt_prompt"] = build_chatgpt_course_generation_prompt(row)
    merged["codex_prompt"] = build_codex_cursor_import_prompt(row)
    merged["status_enum"] = COURSE_REQUEST_STATUSES

    return templates.TemplateResponse(request, "admin/course_requests/detail.html", context=merged)


@router.post("/admin/course-requests/{request_id}/status")
def admin_course_request_set_status(request: Request, request_id: int, status: str = Form(...)):
    with Session(get_engine()) as session:
        redir = ensure_admin_web(request, session)
        if redir is not None:
            return redir

        row = get_course_request(session, request_id, scoped_user_id=None)
        if row is None:
            raise HTTPException(status_code=404, detail="Заявка не найдена.")
        try:
            update_course_request_status(session, row=row, new_status=status)
            session.commit()
        except ValueError as exc:
            session.rollback()
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return RedirectResponse(url=f"/admin/course-requests/{request_id}", status_code=303)


@router.post("/admin/course-requests/{request_id}/notes")
def admin_course_request_save_notes(request: Request, request_id: int, admin_notes: str = Form("")):
    with Session(get_engine()) as session:
        redir = ensure_admin_web(request, session)
        if redir is not None:
            return redir

        row = get_course_request(session, request_id, scoped_user_id=None)
        if row is None:
            raise HTTPException(status_code=404, detail="Заявка не найдена.")

        update_course_request_admin_notes(session, row=row, notes=admin_notes)
        session.commit()

    return RedirectResponse(url=f"/admin/course-requests/{request_id}", status_code=303)
