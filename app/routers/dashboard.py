from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.content_registry import get_content_registry
from app.db import get_engine
from app.services.execution_service import dashboard_execution_summary
from app.services.progress_service import ensure_progress_initialized

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter()


@router.get("/dashboard")
def dashboard(request: Request):
    user_id = request.session.get("user_id")
    username = request.session.get("username")
    if not user_id or not username:
        return RedirectResponse(url="/login", status_code=303)

    registry = get_content_registry()
    course = registry.courses.get("python-backend-ai")
    if not course:
        return RedirectResponse(url="/login", status_code=303)

    with Session(get_engine()) as session:
        snapshot = ensure_progress_initialized(session, int(user_id), course.slug)
        next_lesson = registry.lessons.get(snapshot.next_lesson_key) if snapshot.next_lesson_key else None
        execution_summary = dashboard_execution_summary(session, int(user_id), next_lesson)
        session.commit()

    next_lesson_key = snapshot.next_lesson_key
    course_href = f"/courses/{course.slug}" if course else "/courses/python-backend-ai"
    lesson_href = f"/lessons/{next_lesson_key}" if next_lesson_key else "/lessons/foundation-intro"
    next_step_body = (
        f"{snapshot.next_lesson_title}" if snapshot.next_lesson_title else "Курс завершён, можно повторить материалы"
    )

    cards = [
        {
            "title": "Текущий курс",
            "body": (f"{course.title}" if course else "Курс пока не загружен"),
            "href": (course_href if course else None),
            "link_label": "Открыть карту курса",
        },
        {
            "title": "Следующий шаг",
            "body": next_step_body,
            "href": (lesson_href if next_lesson_key else None),
            "link_label": ("Открыть следующий урок" if next_lesson_key else "Открыть карту курса"),
        },
        {
            "title": "Прогресс недели",
            "body": f"{snapshot.progress_pct}% завершено ({snapshot.completed_lessons}/{snapshot.total_lessons} уроков)",
            "href": None,
            "link_label": None,
        },
    ]
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "cards": cards,
            "username": username,
            "continue_href": lesson_href,
            "execution_summary": execution_summary,
            "nav_course_href": course_href,
            "nav_lessons_href": lesson_href,
        },
    )
