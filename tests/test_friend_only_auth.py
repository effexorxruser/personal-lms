"""Сценарии friend-only авторизации и feature flags без публичной регистрации."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session, delete

os.environ["PERSONAL_LMS_DATABASE_URL"] = "sqlite:///./instance/test_friend_only.db"
os.environ.setdefault(
    "PERSONAL_LMS_SESSION_SECRET_KEY",
    "integration-test-session-secret-xxxx",
)


from app.config import get_settings
from app.db import get_engine, init_db
from app.main import create_app
from app.models import User
from app.security import hash_password


DB_PATH = Path("instance/test_friend_only.db")


def _prepare_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    get_settings.cache_clear()
    get_engine.cache_clear()
    init_db()
    with Session(get_engine()) as session:
        session.exec(delete(User))
        session.commit()
        session.add(
            User(
                username="active_friend",
                display_name="Активный",
                password_hash=hash_password("friend-pass"),
                role="admin",
                is_active=True,
            ),
        )
        session.add(
            User(
                username="paused_friend",
                display_name="Неактивный",
                password_hash=hash_password("friend-pass"),
                role="learner",
                is_active=False,
            ),
        )
        session.commit()


def test_login_rejects_inactive_user() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        response = client.post(
            "/login",
            data={"username": "paused_friend", "password": "friend-pass"},
            follow_redirects=False,
        )
        assert response.status_code == 401
        board = client.get("/dashboard", follow_redirects=False)
        assert board.status_code == 303
        assert board.headers["location"] == "/login"


def test_login_rejects_bad_password() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        response = client.post(
            "/login",
            data={"username": "active_friend", "password": "wrong-pass"},
            follow_redirects=False,
        )
        assert response.status_code == 401


def test_login_sets_session_cookie_and_redirects() -> None:
    _prepare_db()
    cookie_name = get_settings().session_cookie_name
    with TestClient(create_app()) as client:
        response = client.post(
            "/login",
            data={"username": "active_friend", "password": "friend-pass"},
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/dashboard"
        assert cookie_name in response.cookies


def test_logout_clears_session() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        client.post(
            "/login",
            data={"username": "active_friend", "password": "friend-pass"},
            follow_redirects=False,
        )
        client.post("/logout", follow_redirects=False)
        board = client.get("/dashboard", follow_redirects=False)
        assert board.status_code == 303
        assert board.headers["location"] == "/login"


def test_terminal_api_forbidden_when_disabled(monkeypatch) -> None:
    _prepare_db()
    monkeypatch.setenv("PERSONAL_LMS_ENABLE_TERMINAL", "false")
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        client.post(
            "/login",
            data={"username": "active_friend", "password": "friend-pass"},
            follow_redirects=False,
        )
        response = client.post(
            "/api/terminal/lessons/__feature_gate_only__/run",
            json={"command": "echo test"},
            follow_redirects=False,
        )
        assert response.status_code == 403
        payload = response.json()
        assert "detail" in payload
        body = response.text.lower()
        assert "traceback" not in body


def test_ai_helper_chat_forbidden_when_disabled(monkeypatch) -> None:
    _prepare_db()
    monkeypatch.setenv("PERSONAL_LMS_ENABLE_AI_HELPER", "false")
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        client.post(
            "/login",
            data={"username": "active_friend", "password": "friend-pass"},
            follow_redirects=False,
        )
        response = client.post(
            "/api/ai-helper/chat",
            json={"path": "/", "message": "привет"},
            follow_redirects=False,
        )
        assert response.status_code == 403
        payload = response.json()
        assert "detail" in payload


def test_login_secure_cookie_when_configured(monkeypatch) -> None:
    _prepare_db()
    monkeypatch.setenv("PERSONAL_LMS_SESSION_COOKIE_SECURE", "true")
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        response = client.post(
            "/login",
            data={"username": "active_friend", "password": "friend-pass"},
            follow_redirects=False,
        )
    set_cookie_header = response.headers.get("set-cookie", "")
    assert "secure" in set_cookie_header.lower()
