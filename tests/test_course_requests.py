"""Запросы на новые курсы: сервис, права доступа и детерминированные промпты."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

os.environ["PERSONAL_LMS_DATABASE_URL"] = "sqlite:///./instance/test_course_requests.db"
os.environ.setdefault(
    "PERSONAL_LMS_SESSION_SECRET_KEY",
    "course-request-test-session-key-32-characters",
)
os.environ.setdefault("PERSONAL_LMS_ACTIVE_COURSE_SLUG", "test-python-course")


from app.config import get_settings
from app.db import get_engine, init_db
from app.main import create_app
from app.models import CourseRequest, User
from app.security import hash_password
from app.services.course_request_service import (
    build_chatgpt_course_generation_prompt,
    build_codex_cursor_import_prompt,
    create_course_request,
    list_course_requests,
    update_course_request_admin_notes,
    update_course_request_status,
)
from tests.content_runtime_utils import use_fixture_content_pack
from tests.fixture_metadata import ACTIVE_COURSE_SLUG


@pytest.fixture(autouse=True)
def _use_fixture_content_pack(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PERSONAL_LMS_ACTIVE_COURSE_SLUG", ACTIVE_COURSE_SLUG)
    get_settings.cache_clear()
    use_fixture_content_pack(monkeypatch)


DB_PATH = Path("instance/test_course_requests.db")


def _prepare_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    get_settings.cache_clear()
    get_engine.cache_clear()
    init_db()
    with Session(get_engine()) as session:
        session.exec(delete(CourseRequest))
        session.exec(delete(User))
        session.commit()
        session.add(
            User(
                username="admin-cr",
                display_name="Admin",
                password_hash=hash_password("adm-pass"),
                role="admin",
                is_active=True,
            ),
        )
        session.add(
            User(
                username="learner-a",
                display_name="Learner A",
                password_hash=hash_password("a-pass"),
                role="learner",
                is_active=True,
            ),
        )
        session.add(
            User(
                username="learner-b",
                display_name="Learner B",
                password_hash=hash_password("b-pass"),
                role="learner",
                is_active=True,
            ),
        )
        session.commit()


def _login(client: TestClient, *, username: str, password: str) -> None:
    r = client.post("/login", data={"username": username, "password": password}, follow_redirects=False)
    assert r.status_code == 303


def test_create_defaults_submitted_service() -> None:
    _prepare_db()
    with Session(get_engine()) as session:
        row = create_course_request(
            session,
            user_id=1,
            title="Kubernetes для backend",
            goal="Эксплуатация продакшен кластера",
            current_level="middle python",
            duration_weeks=6,
            preferred_format="текст+лабы",
            required_topics_text="- helm\n",
            excluded_topics_text="",
            expected_artifacts_text="- helm chart\n",
        )
        session.commit()
        assert row.status == "submitted"
        assert row.id is not None


def test_list_scoped_to_owner() -> None:
    _prepare_db()
    with Session(get_engine()) as session:
        create_course_request(
            session,
            user_id=2,
            title="A",
            goal="ga",
            current_level="l1",
            duration_weeks=2,
            preferred_format="t",
            required_topics_text="",
            excluded_topics_text="",
            expected_artifacts_text="",
        )
        create_course_request(
            session,
            user_id=3,
            title="B",
            goal="gb",
            current_level="l2",
            duration_weeks=3,
            preferred_format="t",
            required_topics_text="",
            excluded_topics_text="",
            expected_artifacts_text="",
        )
        session.commit()
        a_rows = list_course_requests(session, user_id=2, for_admin=False)
        admin_rows = list_course_requests(session, user_id=None, for_admin=True)
    assert len(a_rows) == 1 and a_rows[0].title == "A"
    assert len(admin_rows) == 2


def test_status_and_notes_updates() -> None:
    _prepare_db()
    with Session(get_engine()) as session:
        row = create_course_request(
            session,
            user_id=2,
            title="Title",
            goal="Goal here",
            current_level="beginner",
            duration_weeks=4,
            preferred_format="async",
            required_topics_text="pip",
            excluded_topics_text="",
            expected_artifacts_text="",
        )
        session.commit()
        rid = row.id

    with Session(get_engine()) as session:
        loaded = session.get(CourseRequest, rid)
        assert loaded is not None
        update_course_request_status(session, row=loaded, new_status="reviewing")
        update_course_request_admin_notes(session, row=loaded, notes="ждём согласование")
        session.commit()

    with Session(get_engine()) as session:
        again = session.get(CourseRequest, rid)
        assert again is not None
        assert again.status == "reviewing"
        assert again.admin_notes == "ждём согласование"


def test_rejected_terminal_transition() -> None:
    _prepare_db()
    with Session(get_engine()) as session:
        row = create_course_request(
            session,
            user_id=2,
            title="Title",
            goal="Goal here",
            current_level="beginner",
            duration_weeks=4,
            preferred_format="async",
            required_topics_text="",
            excluded_topics_text="",
            expected_artifacts_text="",
        )
        session.commit()
        update_course_request_status(session, row=row, new_status="rejected")
        session.commit()
        with pytest.raises(ValueError):
            update_course_request_status(session, row=row, new_status="submitted")


def test_prompt_contains_contract_and_codex_requires() -> None:
    row = CourseRequest(
        id=99,
        user_id=7,
        title="TestCourse",
        goal="Учимся делать надёжные API.",
        current_level="junior backend",
        duration_weeks=8,
        preferred_format="текст + чек листы",
        required_topics_json='["sqlalchemy","jwt"]',
        excluded_topics_json='["bitcoin"]',
        expected_artifacts_json='["openapi.yaml"]',
        status="accepted",
        admin_notes="",
        created_at=datetime(2026, 1, 15, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 15, tzinfo=timezone.utc),
    )
    chat = build_chatgpt_course_generation_prompt(row)
    codex = build_codex_cursor_import_prompt(row)
    assert "COURSE_PACK_CONTRACT.md" in chat
    assert "Учимся делать надёжные API" in chat
    assert "8" in chat
    assert "sqlalchemy" in chat.lower()
    assert "bitcoin" in chat.lower()

    assert "Codex/Cursor" in codex
    assert "Не генерируй курс заново" in codex
    assert "Не переписывай runtime-платформу" in codex
    assert "Нет GitHub API" in codex


@pytest.mark.parametrize(
    "path",
    ["/course-requests", "/course-requests/new"],
)
def test_anonymous_redirects_course_request_pages(path: str) -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        r = client.get(path, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers.get("location") == "/login"


def test_learner_cannot_admin_list() -> None:
    """Learner без прав админа получает HTTP 403 на список админки."""
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client, username="learner-a", password="a-pass")
        r = client.get("/admin/course-requests", follow_redirects=False)
    assert r.status_code == 403
    assert r.json().get("detail")


def test_learner_cannot_view_foreign_request_detail() -> None:
    _prepare_db()
    with Session(get_engine()) as session:
        row = create_course_request(
            session,
            user_id=2,
            title="PRIVATE",
            goal="Goal",
            current_level="l",
            duration_weeks=2,
            preferred_format="f",
            required_topics_text="",
            excluded_topics_text="",
            expected_artifacts_text="",
        )
        session.commit()
        rid = row.id
    with TestClient(create_app()) as client:
        _login(client, username="learner-b", password="b-pass")
        r = client.get(f"/course-requests/{rid}", follow_redirects=False)
    assert r.status_code == 404


def test_create_and_list_via_http_flow() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client, username="learner-a", password="a-pass")
        new_page = client.get("/course-requests/new")
        assert new_page.status_code == 200
        post_r = client.post(
            "/course-requests",
            data={
                "title": "Rust async",
                "goal": "Сделать понятный onboarding",
                "current_level": "junior",
                "duration_weeks": "5",
                "preferred_format": "только текст",
                "required_topics_text": "- ownership\n",
                "excluded_topics_text": "- blockchain\n",
                "expected_artifacts_text": "- мини crates\n",
            },
            follow_redirects=False,
        )
        assert post_r.status_code == 303
        loc = post_r.headers.get("location", "")
        assert loc.startswith("/course-requests/")
        lst = client.get("/course-requests")
        assert lst.status_code == 200
        assert "Rust async" in lst.text


def test_admin_status_post_roundtrip() -> None:
    _prepare_db()
    rid: int | None = None
    with Session(get_engine()) as session:
        row = create_course_request(
            session,
            user_id=2,
            title="ADMINFLOW",
            goal="Goal",
            current_level="l",
            duration_weeks=3,
            preferred_format="f",
            required_topics_text="",
            excluded_topics_text="",
            expected_artifacts_text="",
        )
        session.commit()
        rid = row.id
    assert rid is not None
    with TestClient(create_app()) as client:
        _login(client, username="admin-cr", password="adm-pass")
        resp = client.post(
            f"/admin/course-requests/{rid}/status",
            data={"status": "reviewing"},
            follow_redirects=False,
        )
        assert resp.status_code == 303

    with Session(get_engine()) as session:
        row_check = session.get(CourseRequest, rid)
        assert row_check is not None
        assert row_check.status == "reviewing"


def test_admin_notes_post_roundtrip() -> None:
    _prepare_db()
    rid: int | None = None
    with Session(get_engine()) as session:
        row = create_course_request(
            session,
            user_id=2,
            title="NOTES",
            goal="Goal",
            current_level="l",
            duration_weeks=2,
            preferred_format="f",
            required_topics_text="",
            excluded_topics_text="",
            expected_artifacts_text="",
        )
        session.commit()
        rid = row.id
    assert rid is not None
    with TestClient(create_app()) as client:
        _login(client, username="admin-cr", password="adm-pass")
        resp = client.post(
            f"/admin/course-requests/{rid}/notes",
            data={"admin_notes": "ответ от админа"},
            follow_redirects=False,
        )
        assert resp.status_code == 303

    with Session(get_engine()) as session:
        loaded = session.get(CourseRequest, rid)
        assert loaded is not None
        assert loaded.admin_notes == "ответ от админа"


def test_admin_list_page_renders_when_logged_in() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client, username="admin-cr", password="adm-pass")
        r = client.get("/admin/course-requests")
    assert r.status_code == 200
    assert "Все заявки" in r.text


