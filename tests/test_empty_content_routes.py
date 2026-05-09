"""HTTP 200 без 500 при пустом learner-visible каталоге курсов."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

os.environ.setdefault("PERSONAL_LMS_DATABASE_URL", "sqlite:///./instance/test_empty_content.db")
os.environ.setdefault("PERSONAL_LMS_SESSION_SECRET_KEY", "test-empty-content-secret-xx")
os.environ.setdefault("PERSONAL_LMS_ENABLE_TERMINAL", "true")

from app.config import get_settings
from app.db import get_engine, init_db
from app.main import create_app
from app.models import User
from app.security import hash_password
from tests.content_runtime_utils import use_empty_catalog

DB_PATH = Path("instance/test_empty_content.db")


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
                username="empty-tester",
                display_name="Empty",
                password_hash=hash_password("empty-pass"),
                role="admin",
                is_active=True,
            ),
        )
        session.commit()


@pytest.fixture(autouse=True)
def _prepare_db_fixture() -> None:
    _prepare_db()


def _login(client: TestClient) -> None:
    response = client.post(
        "/login",
        data={"username": "empty-tester", "password": "empty-pass"},
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_dashboard_recap_and_courses_200_when_catalog_empty(monkeypatch, tmp_path) -> None:
    use_empty_catalog(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        _login(client)
        dashboard = client.get("/dashboard")
        recap = client.get("/recap")
        catalog = client.get("/courses")

    assert dashboard.status_code == 200
    assert recap.status_code == 200
    assert catalog.status_code == 200
    assert "Курсы пока не добавлены." in dashboard.text


def test_missing_course_and_lesson_404(monkeypatch, tmp_path) -> None:
    use_empty_catalog(monkeypatch, tmp_path)
    with TestClient(create_app()) as client:
        _login(client)
        missing_course = client.get("/courses/nonexistent-course-slug-xyz")
        missing_lesson = client.get("/lessons/nonexistent-lesson-key-xyz")

    assert missing_course.status_code == 404
    assert missing_lesson.status_code == 404


def test_terminal_returns_403_when_disabled_even_if_catalog_empty(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("PERSONAL_LMS_ENABLE_TERMINAL", "false")
    use_empty_catalog(monkeypatch, tmp_path)
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        _login(client)
        terminal = client.post(
            "/api/terminal/lessons/__noop__/run",
            json={"command": "pwd"},
            follow_redirects=False,
        )
    assert terminal.status_code == 403


def test_ai_helper_returns_403_when_disabled_even_if_catalog_empty(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("PERSONAL_LMS_ENABLE_AI_HELPER", "false")
    use_empty_catalog(monkeypatch, tmp_path)
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        _login(client)
        ai = client.post(
            "/api/ai-helper/chat",
            json={"path": "/", "message": "привет"},
            follow_redirects=False,
        )
    assert ai.status_code == 403
