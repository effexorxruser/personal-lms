import os
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session, delete, select

os.environ["PERSONAL_LMS_DATABASE_URL"] = "sqlite:///./instance/test_ai_helper.db"
os.environ["PERSONAL_LMS_SESSION_SECRET_KEY"] = "test-session-secret"
os.environ["PERSONAL_LMS_OPENAI_API_KEY"] = ""

from app.config import get_settings
from app.db import get_engine, init_db
from app.main import create_app
from app.models import AIHelperMessage, User
from app.security import hash_password

DB_PATH = Path("instance/test_ai_helper.db")


def _prepare_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    get_settings.cache_clear()
    get_engine.cache_clear()
    init_db()
    with Session(get_engine()) as session:
        session.exec(delete(AIHelperMessage))
        session.exec(delete(User))
        session.add(
            User(
                username="admin",
                display_name="Администратор",
                password_hash=hash_password("admin-pass"),
                role="admin",
                is_active=True,
            )
        )
        session.commit()


def _login(client: TestClient) -> None:
    response = client.post("/login", data={"username": "admin", "password": "admin-pass"}, follow_redirects=False)
    assert response.status_code == 303


def test_helper_chat_history_is_scoped_by_context() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)
        lesson_response = client.post(
            "/api/ai-helper/chat",
            json={
                "path": "/lessons/foundation-real-cli-python",
                "message": "Подскажи, что делать дальше",
                "socratic_mode": False,
            },
        )
        assert lesson_response.status_code == 200

        course_response = client.post(
            "/api/ai-helper/chat",
            json={
                "path": "/courses/python-backend-ai-foundation",
                "message": "Какой следующий модуль?",
                "socratic_mode": False,
            },
        )
        assert course_response.status_code == 200

        lesson_history = client.post(
            "/api/ai-helper/history",
            json={"path": "/lessons/foundation-real-cli-python"},
        )
        course_history = client.post(
            "/api/ai-helper/history",
            json={"path": "/courses/python-backend-ai-foundation"},
        )

    assert lesson_history.status_code == 200
    assert course_history.status_code == 200
    assert lesson_history.json()["context_key"].startswith("lesson:")
    assert course_history.json()["context_key"].startswith("course:")
    assert len(lesson_history.json()["messages"]) == 2
    assert len(course_history.json()["messages"]) == 2


def test_helper_clear_removes_only_current_context_history() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)
        client.post(
            "/api/ai-helper/chat",
            json={"path": "/dashboard", "message": "Что у меня по прогрессу?", "socratic_mode": False},
        )
        client.post(
            "/api/ai-helper/chat",
            json={
                "path": "/lessons/foundation-real-cli-python",
                "message": "Я застрял",
                "socratic_mode": True,
            },
        )
        clear_response = client.post("/api/ai-helper/clear", json={"path": "/dashboard"})
        assert clear_response.status_code == 200

        dashboard_history = client.post("/api/ai-helper/history", json={"path": "/dashboard"})
        lesson_history = client.post("/api/ai-helper/history", json={"path": "/lessons/foundation-real-cli-python"})

    assert dashboard_history.status_code == 200
    assert lesson_history.status_code == 200
    assert dashboard_history.json()["messages"] == []
    assert len(lesson_history.json()["messages"]) == 2

    with Session(get_engine()) as session:
        stored = list(session.exec(select(AIHelperMessage)))
    assert stored
