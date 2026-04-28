import os
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session, delete

os.environ["PERSONAL_LMS_DATABASE_URL"] = "sqlite:///./instance/test_ai_helper_ui.db"
os.environ["PERSONAL_LMS_SESSION_SECRET_KEY"] = "test-session-secret"

from app.config import get_settings
from app.db import get_engine, init_db
from app.main import create_app
from app.models import AIHelperMessage, User
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


def test_helper_is_rendered_on_internal_page_for_authed_user() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)
        response = client.get("/dashboard")
    assert response.status_code == 200
    assert "data-ai-helper" in response.text
    assert "Lain AI" in response.text


def test_helper_is_not_rendered_on_login_page() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        response = client.get("/login")
    assert response.status_code == 200
    assert "data-ai-helper" not in response.text
