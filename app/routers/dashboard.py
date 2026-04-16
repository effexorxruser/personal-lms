from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.content_registry import get_content_registry

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
    first_lesson_key = registry.lesson_order[0] if registry.lesson_order else None

    cards = [
        {
            "title": "Текущий курс",
            "body": (f"{course.title}" if course else "Курс пока не загружен"),
            "href": (f"/courses/{course.slug}" if course else None),
            "link_label": "Открыть карту курса",
        },
        {
            "title": "Следующий шаг",
            "body": (
                "Перейти к первому уроку контент-карты"
                if first_lesson_key
                else "Подготовить первый урок в content/"
            ),
            "href": (f"/lessons/{first_lesson_key}" if first_lesson_key else None),
            "link_label": "Открыть следующий урок",
        },
        {
            "title": "Прогресс недели",
            "body": "0% до появления учебных данных",
            "href": None,
            "link_label": None,
        },
    ]
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"cards": cards, "username": username},
    )
