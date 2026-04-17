import os
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session, delete, select

os.environ["PERSONAL_LMS_DATABASE_URL"] = "sqlite:///./instance/test_auth.db"
os.environ["PERSONAL_LMS_SESSION_SECRET_KEY"] = "test-session-secret"

from app.config import get_settings
from app.db import get_engine, init_db
from app.main import create_app
from app.content_registry import get_content_registry
from app.models import (
    CheckpointReview,
    CheckpointSubmission,
    CourseProgress,
    LessonProgress,
    ReviewResult,
    StuckEvent,
    TaskSubmission,
    User,
)
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


def test_task_content_is_loaded_from_file_registry() -> None:
    registry = get_content_registry()
    lesson = registry.lessons["backend-structure"]
    task = registry.tasks.get("inspect-app-layout")

    assert lesson.task_slug == "inspect-app-layout"
    assert task is not None
    assert task.title == "Проверить структуру приложения"
    assert task.submission_type == "text"
    assert "router" in " ".join(task.definition_of_done).lower()


def test_checkpoint_content_is_loaded_from_file_registry() -> None:
    registry = get_content_registry()
    checkpoint = registry.checkpoints.get("foundation-cli-pack")

    assert checkpoint is not None
    assert checkpoint.module_slug == "foundation"
    assert checkpoint.submission_type == "repository_link"
    assert "README" in " ".join(checkpoint.definition_of_done)


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


def test_task_lesson_requires_approved_submission_before_completion() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)

        lesson_response = client.get("/lessons/backend-structure")
        assert lesson_response.status_code == 200
        assert "Связанная задача" in lesson_response.text
        assert "Проверить структуру приложения" in lesson_response.text

        blocked_response = client.post("/lessons/backend-structure/complete", follow_redirects=False)
        assert blocked_response.status_code == 303
        assert "completion_blocked=review_required" in blocked_response.headers["location"]

    with Session(get_engine()) as session:
        user = session.exec(select(User).where(User.username == "admin")).first()
        assert user is not None
        progress = session.exec(
            select(LessonProgress).where(
                LessonProgress.user_id == user.id,
                LessonProgress.lesson_key == "backend-structure",
            )
        ).first()

    assert progress is not None
    assert progress.status == "in_progress"


def test_submission_creates_review_and_needs_revision_state() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)
        response = client.post(
            "/lessons/backend-structure/submissions",
            data={"submission_type": "text", "content_text": "ok"},
            follow_redirects=False,
        )
        assert response.status_code == 303

        lesson_response = client.get("/lessons/backend-structure")
        course_response = client.get("/courses/python-backend-ai")

    assert "Submission слишком короткий" in lesson_response.text
    assert "требует доработки" in lesson_response.text
    assert "Статус: требует доработки" in lesson_response.text
    assert "Статус: требует доработки" in course_response.text

    with Session(get_engine()) as session:
        submission = session.exec(select(TaskSubmission)).first()
        review = session.exec(select(ReviewResult)).first()

    assert submission is not None
    assert submission.status == "needs_revision"
    assert review is not None
    assert review.verdict == "needs_revision"


def test_approved_submission_allows_task_lesson_completion() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)
        response = client.post(
            "/lessons/backend-structure/submissions",
            data={
                "submission_type": "text",
                "content_text": (
                    "Router: app/routers/content.py. Loader: app/content_loader.py. "
                    "Runtime progress: app/services/progress_service.py."
                ),
            },
            follow_redirects=False,
        )
        assert response.status_code == 303

        lesson_response = client.get("/lessons/backend-structure")
        assert "Базовая проверка пройдена" in lesson_response.text
        assert "review пройден" in lesson_response.text
        assert "Отметить урок завершённым" in lesson_response.text

        complete_response = client.post("/lessons/backend-structure/complete", follow_redirects=False)
        assert complete_response.status_code == 303

    with Session(get_engine()) as session:
        user = session.exec(select(User).where(User.username == "admin")).first()
        assert user is not None
        progress = session.exec(
            select(LessonProgress).where(
                LessonProgress.user_id == user.id,
                LessonProgress.lesson_key == "backend-structure",
            )
        ).first()
        submission = session.exec(select(TaskSubmission)).first()
        review = session.exec(select(ReviewResult)).first()

    assert submission is not None
    assert submission.status == "approved"
    assert review is not None
    assert review.verdict == "approved"
    assert progress is not None
    assert progress.status == "completed"


def test_dashboard_shows_current_task_execution_state() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)
        client.post("/lessons/foundation-intro/complete", follow_redirects=False)
        dashboard_response = client.get("/dashboard")

    assert dashboard_response.status_code == 200
    assert "Выполнение" in dashboard_response.text
    assert "Проверить структуру приложения" in dashboard_response.text
    assert "ожидает submission" in dashboard_response.text


def test_course_map_displays_supported_execution_states() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)

        initial_course = client.get("/courses/python-backend-ai")
        assert "Статус: доступен" in initial_course.text

        client.post("/lessons/foundation-intro/complete", follow_redirects=False)
        client.get("/lessons/backend-structure")
        in_progress_course = client.get("/courses/python-backend-ai")
        assert "Урок 1: Введение в трек" in in_progress_course.text
        assert "Статус: завершён" in in_progress_course.text
        assert "Урок 2: Структура backend" in in_progress_course.text
        assert "Статус: в процессе" in in_progress_course.text

        client.post(
            "/lessons/backend-structure/submissions",
            data={"submission_type": "text", "content_text": "ok"},
            follow_redirects=False,
        )
        revision_course = client.get("/courses/python-backend-ai")
        assert "Статус: требует доработки" in revision_course.text

        client.post(
            "/lessons/backend-structure/submissions",
            data={
                "submission_type": "text",
                "content_text": (
                    "Router: app/routers/content.py. Loader: app/content_loader.py. "
                    "Runtime progress: app/services/progress_service.py."
                ),
            },
            follow_redirects=False,
        )
        approved_course = client.get("/courses/python-backend-ai")
        assert "Статус: review пройден" in approved_course.text

        client.post("/lessons/backend-structure/complete", follow_redirects=False)
        completed_course = client.get("/courses/python-backend-ai")
        assert "Статус: завершён" in completed_course.text


def test_checkpoint_submission_review_and_module_completion_semantics() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)
        client.post("/lessons/foundation-intro/complete", follow_redirects=False)
        client.post(
            "/lessons/backend-structure/submissions",
            data={
                "submission_type": "text",
                "content_text": (
                    "Router: app/routers/content.py. Loader: app/content_loader.py. "
                    "Runtime progress: app/services/progress_service.py."
                ),
            },
            follow_redirects=False,
        )
        client.post("/lessons/backend-structure/complete", follow_redirects=False)

        course_without_checkpoint = client.get("/courses/python-backend-ai")
        dashboard_without_checkpoint = client.get("/dashboard")

        assert "Checkpoint artifact" in course_without_checkpoint.text
        assert "checkpoint ожидает отправки" in course_without_checkpoint.text
        assert "Модуль: checkpoint ожидает отправки" in course_without_checkpoint.text
        assert "Foundation artifact: CLI utility pack" in dashboard_without_checkpoint.text

        bad_checkpoint = client.post(
            "/checkpoints/foundation-cli-pack/submissions",
            data={
                "submission_type": "repository_link",
                "content_link": "bad",
                "content_text": "ok",
            },
            follow_redirects=False,
        )
        assert bad_checkpoint.status_code == 303

        revision_course = client.get("/courses/python-backend-ai")
        assert "Ссылка на checkpoint должна начинаться" in revision_course.text
        assert "Модуль: требует доработки" in revision_course.text

        approved_checkpoint = client.post(
            "/checkpoints/foundation-cli-pack/submissions",
            data={
                "submission_type": "repository_link",
                "content_link": "https://github.com/example/foundation-cli-pack",
                "content_text": "README содержит запуск, demo path и проверяемый run scenario.",
            },
            follow_redirects=False,
        )
        assert approved_checkpoint.status_code == 303

        approved_course = client.get("/courses/python-backend-ai")

    assert "Checkpoint принят" in approved_course.text
    assert "checkpoint пройден" in approved_course.text
    assert "Модуль: завершён" in approved_course.text

    with Session(get_engine()) as session:
        checkpoint_submission = session.exec(
            select(CheckpointSubmission).order_by(CheckpointSubmission.updated_at.desc())
        ).first()
        checkpoint_review = session.exec(
            select(CheckpointReview).order_by(CheckpointReview.created_at.desc())
        ).first()

    assert checkpoint_submission is not None
    assert checkpoint_submission.status == "approved"
    assert checkpoint_review is not None
    assert checkpoint_review.verdict == "approved"


def test_clean_flow_keeps_dashboard_course_and_lesson_progress_consistent() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)

        client.get("/lessons/foundation-intro")
        client.post("/lessons/foundation-intro/complete", follow_redirects=False)
        client.get("/lessons/backend-structure")
        client.post(
            "/lessons/backend-structure/submissions",
            data={"submission_type": "text", "content_text": "bad"},
            follow_redirects=False,
        )

        dashboard_revision = client.get("/dashboard")
        course_revision = client.get("/courses/python-backend-ai")
        lesson_revision = client.get("/lessons/backend-structure")

        assert "требует доработки" in dashboard_revision.text
        assert "Статус: требует доработки" in course_revision.text
        assert "Статус: требует доработки" in lesson_revision.text

        client.post(
            "/lessons/backend-structure/submissions",
            data={
                "submission_type": "text",
                "content_text": (
                    "Router: app/routers/content.py. Loader: app/content_loader.py. "
                    "Runtime progress: app/services/progress_service.py."
                ),
            },
            follow_redirects=False,
        )

        dashboard_approved = client.get("/dashboard")
        course_approved = client.get("/courses/python-backend-ai")
        lesson_approved = client.get("/lessons/backend-structure")

        assert "review пройден" in dashboard_approved.text
        assert "Статус: review пройден" in course_approved.text
        assert "Статус: review пройден" in lesson_approved.text

        client.post("/lessons/backend-structure/complete", follow_redirects=False)
        client.get("/lessons/lesson-navigation")
        client.post("/lessons/lesson-navigation/complete", follow_redirects=False)

        final_dashboard = client.get("/dashboard")
        final_course = client.get("/courses/python-backend-ai")
        final_lesson = client.get("/lessons/backend-structure")

    assert "100% завершено (3/3 уроков)" in final_dashboard.text
    assert "Прогресс: 100%" in final_course.text
    assert "Статус: завершён" in final_lesson.text


def test_stuck_event_creation_and_recovery_path_rendering() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)
        response = client.post(
            "/lessons/backend-structure/stuck",
            data={"reason_code": "unclear_task", "note": "Не понимаю, где искать loader"},
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/lessons/backend-structure#stuck"

        lesson_response = client.get("/lessons/backend-structure")

    assert "Активный блокер: Не понимаю задачу" in lesson_response.text
    assert "Не понимаю, где искать loader" in lesson_response.text
    assert "План возврата" in lesson_response.text

    with Session(get_engine()) as session:
        event = session.exec(select(StuckEvent)).first()

    assert event is not None
    assert event.status == "open"
    assert event.lesson_key == "backend-structure"
    assert event.task_slug == "inspect-app-layout"


def test_stuck_event_resolution() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)
        client.post(
            "/lessons/backend-structure/stuck",
            data={"reason_code": "blocked_by_error", "note": "Ошибка в локальном запуске"},
            follow_redirects=False,
        )

    with Session(get_engine()) as session:
        event = session.exec(select(StuckEvent)).first()
        assert event is not None
        event_id = event.id

    assert event_id is not None
    with TestClient(create_app()) as client:
        _login(client)
        response = client.post(f"/stuck/{event_id}/resolve", follow_redirects=False)
        assert response.status_code == 303

    with Session(get_engine()) as session:
        resolved = session.get(StuckEvent, event_id)

    assert resolved is not None
    assert resolved.status == "resolved"
    assert resolved.resolved_at is not None


def test_dashboard_active_friction_and_weekly_recap_rendering() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)
        client.post("/lessons/foundation-intro/complete", follow_redirects=False)
        client.post(
            "/lessons/backend-structure/stuck",
            data={"reason_code": "review_confusion", "note": "Не понимаю feedback"},
            follow_redirects=False,
        )
        dashboard_response = client.get("/dashboard")

    assert dashboard_response.status_code == 200
    assert "Блокер" in dashboard_response.text
    assert "Не понимаю review" in dashboard_response.text
    assert "Не понимаю feedback" in dashboard_response.text
    assert "Итоги недели" in dashboard_response.text
    assert "1 уроков" in dashboard_response.text
    assert "блокеры: 1" in dashboard_response.text


def test_weekly_recap_page_aggregates_clean_flow_artifacts() -> None:
    _prepare_db()
    with TestClient(create_app()) as client:
        _login(client)
        client.post("/lessons/foundation-intro/complete", follow_redirects=False)
        client.post(
            "/lessons/backend-structure/stuck",
            data={"reason_code": "missing_context", "note": "Нужно вернуться к структуре проекта"},
            follow_redirects=False,
        )
        client.post(
            "/lessons/backend-structure/submissions",
            data={
                "submission_type": "text",
                "content_text": (
                    "Router: app/routers/content.py. Loader: app/content_loader.py. "
                    "Runtime progress: app/services/progress_service.py."
                ),
            },
            follow_redirects=False,
        )
        recap_response = client.get("/recap")

    assert recap_response.status_code == 200
    assert "Итоги последних 7 дней" in recap_response.text
    assert "Урок 1: Введение в трек" in recap_response.text
    assert "Проверить структуру приложения" in recap_response.text
    assert "review пройден" in recap_response.text
    assert "Не хватает контекста" in recap_response.text
    assert "Урок 2: Структура backend" in recap_response.text
