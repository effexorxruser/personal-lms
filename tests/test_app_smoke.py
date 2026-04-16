import os
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session, delete, select

os.environ["PERSONAL_LMS_DATABASE_URL"] = "sqlite:///./instance/test_auth.db"
os.environ["PERSONAL_LMS_SESSION_SECRET_KEY"] = "test-session-secret"

from app.config import get_settings
from app.db import get_engine, init_db
from app.main import create_app
from app.models import CourseProgress, LessonProgress, User
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


def _login(client: TestClient) -> None:
    response = client.post(
        "/login",
        data={"username": "admin", "password": "admin-pass"},
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_protected_routes_redirect_to_login() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        dashboard = client.get("/dashboard", follow_redirects=False)
        course = client.get("/courses/python-backend-ai", follow_redirects=False)
        lesson = client.get("/lessons/foundation-intro", follow_redirects=False)

    assert dashboard.status_code == 303
    assert dashboard.headers["location"] == "/login"
    assert course.status_code == 303
    assert course.headers["location"] == "/login"
    assert lesson.status_code == 303
    assert lesson.headers["location"] == "/login"


def test_login_success() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)
        dashboard_response = client.get("/dashboard")

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
        _login(client)
        response = client.get("/courses/python-backend-ai")

    assert response.status_code == 200
    assert "Карта курса" in response.text


def test_lesson_page_returns_200_and_marks_opened() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)
        response = client.get("/lessons/foundation-intro")

    assert response.status_code == 200
    assert "Урок 1: Введение в трек" in response.text

    with Session(get_engine()) as session:
        user = session.exec(select(User).where(User.username == "admin")).first()
        assert user is not None
        progress = session.exec(
            select(LessonProgress).where(
                LessonProgress.user_id == user.id,
                LessonProgress.lesson_key == "foundation-intro",
            )
        ).first()

    assert progress is not None
    assert progress.opened_count >= 1
    assert progress.status in {"in_progress", "completed"}


def test_missing_course_or_lesson_returns_404_for_authed_user() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)
        missing_course = client.get("/courses/unknown-course")
        missing_lesson = client.get("/lessons/unknown-lesson")

    assert missing_course.status_code == 404
    assert missing_lesson.status_code == 404


def test_lesson_markdown_is_rendered() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)
        response = client.get("/lessons/backend-structure")

    assert response.status_code == 200
    assert "<strong>FastAPI</strong>" in response.text


def test_completing_lesson_updates_progress_and_next_step() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)

        client.get("/dashboard")
        before_dashboard = client.get("/dashboard")
        assert "foundation-intro" in before_dashboard.text

        complete_response = client.post("/lessons/foundation-intro/complete", follow_redirects=False)
        assert complete_response.status_code == 303

        after_dashboard = client.get("/dashboard")

    assert "backend-structure" in after_dashboard.text

    with Session(get_engine()) as session:
        user = session.exec(select(User).where(User.username == "admin")).first()
        assert user is not None
        lesson_progress = session.exec(
            select(LessonProgress).where(
                LessonProgress.user_id == user.id,
                LessonProgress.lesson_key == "foundation-intro",
            )
        ).first()
        course_progress = session.exec(
            select(CourseProgress).where(
                CourseProgress.user_id == user.id,
                CourseProgress.course_slug == "python-backend-ai",
            )
        ).first()

    assert lesson_progress is not None
    assert lesson_progress.status == "completed"
    assert lesson_progress.completed_at is not None
    assert course_progress is not None
    assert course_progress.progress_pct == 33
    assert course_progress.current_lesson_slug == "backend-structure"
