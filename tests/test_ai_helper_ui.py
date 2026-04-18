import os
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session, delete

os.environ["PERSONAL_LMS_DATABASE_URL"] = "sqlite:///./instance/test_ai_helper_ui.db"
os.environ["PERSONAL_LMS_SESSION_SECRET_KEY"] = "test-session-secret"

from app.config import get_settings
from app.db import get_engine, init_db
from app.main import create_app
from app.models import (
    CheckpointReview,
    CheckpointSubmission,
    CourseProgress,
    LainHelperInteraction,
    LessonProgress,
    ReviewResult,
    StuckEvent,
    TaskSubmission,
    TerminalRun,
    User,
)
from app.security import hash_password

DB_PATH = Path("instance/test_ai_helper_ui.db")


def _prepare_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    get_settings.cache_clear()
    get_engine.cache_clear()

    init_db()
    with Session(get_engine()) as session:
        session.exec(delete(LainHelperInteraction))
        session.exec(delete(TerminalRun))
        session.exec(delete(StuckEvent))
        session.exec(delete(CheckpointReview))
        session.exec(delete(CheckpointSubmission))
        session.exec(delete(ReviewResult))
        session.exec(delete(TaskSubmission))
        session.exec(delete(LessonProgress))
        session.exec(delete(CourseProgress))
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


def _configure_ai_helper(enabled: bool) -> None:
    os.environ["PERSONAL_LMS_AI_HELPER_ENABLED"] = "true" if enabled else "false"
    get_settings.cache_clear()


def _login(client: TestClient) -> None:
    response = client.post(
        "/login",
        data={"username": "admin", "password": "admin-pass"},
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_ai_helper_renders_on_internal_pages_with_consistent_context() -> None:
    _configure_ai_helper(enabled=True)
    _prepare_db()

    with TestClient(create_app()) as client:
        _login(client)
        dashboard = client.get("/dashboard")
        course = client.get("/courses/python-backend-ai")
        lesson = client.get("/lessons/backend-structure")
        recap = client.get("/recap")

    for response in (dashboard, course, lesson, recap):
        assert response.status_code == 200
        assert "data-ai-helper" in response.text
        assert "data-ai-endpoint=\"/api/ai/helper\"" in response.text
        assert "data-ai-history-endpoint=\"/api/ai/helper/history\"" in response.text
        assert "data-ai-lesson=\"\"" not in response.text


def test_ai_helper_panel_contains_quick_actions_and_empty_state() -> None:
    _configure_ai_helper(enabled=True)
    _prepare_db()

    with TestClient(create_app()) as client:
        _login(client)
        lesson = client.get("/lessons/backend-structure")

    assert lesson.status_code == 200
    assert "Объясни текущий урок" in lesson.text
    assert "Помоги начать" in lesson.text
    assert "Я застрял" in lesson.text
    assert "Проверь мой ответ" in lesson.text
    assert "data-ai-empty" in lesson.text
    assert "Вопрос по текущему шагу урока" in lesson.text


def test_ai_helper_is_not_rendered_when_feature_flag_is_disabled() -> None:
    _configure_ai_helper(enabled=False)
    _prepare_db()

    with TestClient(create_app()) as client:
        _login(client)
        dashboard = client.get("/dashboard")

    assert dashboard.status_code == 200
    assert "data-ai-helper" not in dashboard.text


def test_ai_helper_is_not_rendered_on_login_page() -> None:
    _configure_ai_helper(enabled=True)
    _prepare_db()

    with TestClient(create_app()) as client:
        login = client.get("/login")

    assert login.status_code == 200
    assert "data-ai-helper" not in login.text
