from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter()


@router.get("/dashboard")
def dashboard(request: Request):
    cards = [
        {
            "title": "Текущий курс",
            "body": "Python backend и AI application foundations",
        },
        {
            "title": "Следующий шаг",
            "body": "Сохранить основу маленькой и готовой к Phase 2",
        },
        {
            "title": "Прогресс недели",
            "body": "0% до появления учебных данных",
        },
    ]
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"cards": cards},
    )
