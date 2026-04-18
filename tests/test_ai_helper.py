import os
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session, delete, select

os.environ["PERSONAL_LMS_DATABASE_URL"] = "sqlite:///./instance/test_ai_helper.db"
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
import app.services.ai_helper_service as ai_helper_service
from app.services.lain_provider import LainProviderError

DB_PATH = Path("instance/test_ai_helper.db")


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
        session.add(
            User(
                username="other",
                display_name="Другой пользователь",
                password_hash=hash_password("other-pass"),
                role="learner",
                is_active=True,
            )
        )
        session.commit()


def _configure_ai_helper(enabled: bool, api_key: str | None) -> None:
    os.environ["PERSONAL_LMS_AI_HELPER_ENABLED"] = "true" if enabled else "false"
    if api_key is None:
        os.environ["PERSONAL_LMS_OPENAI_API_KEY"] = ""
    else:
        os.environ["PERSONAL_LMS_OPENAI_API_KEY"] = api_key
    get_settings.cache_clear()


def _login(client: TestClient, username: str = "admin", password: str = "admin-pass") -> None:
    response = client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_ai_helper_endpoint_requires_auth() -> None:
    _configure_ai_helper(enabled=True, api_key="test-key")
    _prepare_db()

    with TestClient(create_app()) as client:
        post_response = client.post(
            "/api/ai/helper",
            json={
                "lesson_key": "backend-structure",
                "mode": "explain_lesson",
                "message": "Объясни текущий шаг",
            },
        )
        history_response = client.get("/api/ai/helper/history?lesson_key=backend-structure")

    assert post_response.status_code == 401
    assert history_response.status_code == 401


def test_ai_helper_accepts_valid_request_and_returns_provider_reply(monkeypatch) -> None:
    _configure_ai_helper(enabled=True, api_key="test-key")
    _prepare_db()

    monkeypatch.setattr(
        ai_helper_service,
        "request_lain_reply",
        lambda request: "Сначала открой router, затем проверь content loader и service progress.",
    )

    with TestClient(create_app()) as client:
        _login(client)
        response = client.post(
            "/api/ai/helper",
            json={
                "lesson_key": "backend-structure",
                "mode": "explain_lesson",
                "message": "Что важно?",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["mode"] == "explain_lesson"
    assert "router" in payload["assistant_message"].lower()


def test_ai_helper_rejects_unsupported_mode() -> None:
    _configure_ai_helper(enabled=True, api_key="test-key")
    _prepare_db()

    with TestClient(create_app()) as client:
        _login(client)
        response = client.post(
            "/api/ai/helper",
            json={
                "lesson_key": "backend-structure",
                "mode": "unsupported",
                "message": "что делать",
            },
        )

    assert response.status_code == 422


def test_ai_helper_feature_flag_disabled_returns_graceful_response() -> None:
    _configure_ai_helper(enabled=False, api_key="test-key")
    _prepare_db()

    with TestClient(create_app()) as client:
        _login(client)
        response = client.post(
            "/api/ai/helper",
            json={
                "lesson_key": "backend-structure",
                "mode": "explain_lesson",
                "message": "Объясни урок",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "disabled"
    assert "отключена" in payload["assistant_message"]


def test_ai_helper_missing_api_key_returns_graceful_response() -> None:
    _configure_ai_helper(enabled=True, api_key=None)
    _prepare_db()

    with TestClient(create_app()) as client:
        _login(client)
        response = client.post(
            "/api/ai/helper",
            json={
                "lesson_key": "backend-structure",
                "mode": "help_start",
                "message": "Помоги начать",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "missing_key"
    assert "не задан API ключ" in payload["assistant_message"]


def test_ai_helper_provider_error_returns_graceful_fallback(monkeypatch) -> None:
    _configure_ai_helper(enabled=True, api_key="test-key")
    _prepare_db()

    def _failing_provider(_request):
        raise LainProviderError("provider down")

    monkeypatch.setattr(ai_helper_service, "request_lain_reply", _failing_provider)

    with TestClient(create_app()) as client:
        _login(client)
        response = client.post(
            "/api/ai/helper",
            json={
                "lesson_key": "backend-structure",
                "mode": "free_question",
                "message": "Какой шаг сделать дальше?",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "provider_error"
    assert "Не удалось получить ответ Lain" in payload["assistant_message"]


def test_ai_helper_uses_lesson_context_when_calling_provider(monkeypatch) -> None:
    _configure_ai_helper(enabled=True, api_key="test-key")
    _prepare_db()
    captured: dict[str, str] = {}

    def _fake_provider(request):
        captured["system_prompt"] = request.system_prompt
        captured["user_prompt"] = request.user_prompt
        return "Сфокусируйся на router и loader, затем проверь progress service."

    monkeypatch.setattr(ai_helper_service, "request_lain_reply", _fake_provider)

    with TestClient(create_app()) as client:
        _login(client)
        response = client.post(
            "/api/ai/helper",
            json={
                "lesson_key": "backend-structure",
                "mode": "explain_lesson",
                "message": "Что здесь главное?",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "Урок 2: Структура backend" in captured["user_prompt"]
    assert "Task title: Проверить структуру приложения" in captured["user_prompt"]


def test_ai_helper_works_without_task_context(monkeypatch) -> None:
    _configure_ai_helper(enabled=True, api_key="test-key")
    _prepare_db()

    monkeypatch.setattr(
        ai_helper_service,
        "request_lain_reply",
        lambda _request: "Начни с целей урока и сверяйся с чеклистом после каждого шага.",
    )

    with TestClient(create_app()) as client:
        _login(client)
        response = client.post(
            "/api/ai/helper",
            json={
                "lesson_key": "foundation-intro",
                "mode": "help_start",
                "message": "С чего стартовать?",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "чеклист" in payload["assistant_message"].lower()


def test_ai_helper_limits_out_of_scope_or_autopilot_requests(monkeypatch) -> None:
    _configure_ai_helper(enabled=True, api_key="test-key")
    _prepare_db()

    def _must_not_call_provider(_request):
        raise AssertionError("Provider should not be called for scope-refusal request")

    monkeypatch.setattr(ai_helper_service, "request_lain_reply", _must_not_call_provider)

    with TestClient(create_app()) as client:
        _login(client)
        response = client.post(
            "/api/ai/helper",
            json={
                "lesson_key": "backend-structure",
                "mode": "free_question",
                "message": "Сделай за меня весь submission и закрой урок автоматически.",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "guardrail"
    assert "выходит за рамки текущего шага" in payload["assistant_message"]


def test_ai_helper_interaction_log_is_persisted(monkeypatch) -> None:
    _configure_ai_helper(enabled=True, api_key="test-key")
    _prepare_db()

    monkeypatch.setattr(
        ai_helper_service,
        "request_lain_reply",
        lambda _request: "Сделай один шаг: открой router и сопоставь его с lesson flow.",
    )

    with TestClient(create_app()) as client:
        _login(client)
        response = client.post(
            "/api/ai/helper",
            json={
                "lesson_key": "backend-structure",
                "mode": "stuck_help",
                "message": "Я запутался в структуре.",
            },
        )
        assert response.status_code == 200

    with Session(get_engine()) as session:
        interaction = session.exec(select(LainHelperInteraction).order_by(LainHelperInteraction.created_at.desc())).first()
        user = session.exec(select(User).where(User.username == "admin")).first()

    assert interaction is not None
    assert user is not None
    assert interaction.user_id == user.id
    assert interaction.lesson_key == "backend-structure"
    assert interaction.mode == "stuck_help"
    assert "запутался" in interaction.user_message
    assert "router" in interaction.assistant_message.lower()


def test_ai_helper_history_endpoint_filters_by_user_lesson_and_limit() -> None:
    _configure_ai_helper(enabled=True, api_key="test-key")
    _prepare_db()

    with Session(get_engine()) as session:
        admin = session.exec(select(User).where(User.username == "admin")).first()
        other = session.exec(select(User).where(User.username == "other")).first()
        assert admin is not None
        assert other is not None

        for index in range(4):
            session.add(
                LainHelperInteraction(
                    user_id=admin.id,
                    lesson_key="backend-structure",
                    mode="help_start",
                    user_message=f"admin message {index}",
                    assistant_message=f"admin reply {index}",
                )
            )

        session.add(
            LainHelperInteraction(
                user_id=admin.id,
                lesson_key="foundation-intro",
                mode="help_start",
                user_message="wrong lesson",
                assistant_message="wrong lesson",
            )
        )
        session.add(
            LainHelperInteraction(
                user_id=other.id,
                lesson_key="backend-structure",
                mode="help_start",
                user_message="other user",
                assistant_message="other user",
            )
        )
        session.commit()

    with TestClient(create_app()) as client:
        _login(client)
        response = client.get("/api/ai/helper/history?lesson_key=backend-structure&limit=2")

    assert response.status_code == 200
    payload = response.json()
    assert payload["lesson_key"] == "backend-structure"
    assert len(payload["items"]) == 2

    rendered_messages = [item["user_message"] for item in payload["items"]]
    assert rendered_messages == ["admin message 2", "admin message 3"]
    assert all(item["lesson_key"] == "backend-structure" for item in payload["items"])
    assert "other user" not in rendered_messages
