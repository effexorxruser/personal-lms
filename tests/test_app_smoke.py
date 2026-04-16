import os
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session, delete

os.environ["PERSONAL_LMS_DATABASE_URL"] = "sqlite:///./instance/test_auth.db"
os.environ["PERSONAL_LMS_SESSION_SECRET_KEY"] = "test-session-secret"

from app.config import get_settings
from app.db import get_engine, init_db
from app.main import create_app
from app.models import User
from app.security import hash_password

DB_PATH = Path("instance/test_auth.db")


def _prepare_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    get_settings.cache_clear()
    get_engine.cache_clear()

    init_db()
    with Session(get_engine()) as session:
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


def test_protected_route_redirect() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        response = client.get("/dashboard", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_login_success() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        login_response = client.post(
            "/login",
            data={"username": "admin", "password": "admin-pass"},
            follow_redirects=False,
        )

        dashboard_response = client.get("/dashboard")

    assert login_response.status_code == 303
    assert login_response.headers["location"] == "/dashboard"
    assert dashboard_response.status_code == 200
    assert "Вы вошли как <strong>admin</strong>" in dashboard_response.text


def test_login_fail() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        response = client.post(
            "/login",
            data={"username": "admin", "password": "wrong"},
            follow_redirects=False,
        )

    assert response.status_code == 401
    assert "Неверный логин или пароль" in response.text


def test_course_page_returns_200() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        response = client.get("/courses/python-backend-ai")

    assert response.status_code == 200
    assert "Карта курса" in response.text


def test_lesson_page_returns_200() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        response = client.get("/lessons/foundation-intro")

    assert response.status_code == 200
    assert "Урок 1: Введение в трек" in response.text


def test_missing_course_or_lesson_returns_404() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        missing_course = client.get("/courses/unknown-course")
        missing_lesson = client.get("/lessons/unknown-lesson")

    assert missing_course.status_code == 404
    assert missing_lesson.status_code == 404


def test_lesson_markdown_is_rendered() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        response = client.get("/lessons/backend-structure")

    assert response.status_code == 200
    assert "<strong>FastAPI</strong>" in response.text
