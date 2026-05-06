# Project Decomposition Plan

Дата аудита: 2026-05-06.

## Назначение

Документ фиксирует проверенное состояние `personal-lms` перед декомпозицией в универсальную персональную LMS с file-based курсами по контракту.

Scope этого шага: audit и stabilization. Здесь нет runtime-рефакторинга, новых routes, новых моделей БД или изменения guardrails.

## Проверенные факты

### Runtime stack

Проверено по `pyproject.toml`, `app/main.py`, `app/db.py`, `app/config.py`, `Dockerfile` и CI config.

- Python package требует `>=3.11`.
- FastAPI используется как основное приложение.
- Jinja2 используется для server-rendered templates.
- SQLite используется через SQLModel.
- Alembic есть в зависимостях, но scaffold миграций в репозитории не заведен.
- Tailwind и Alpine.js не используются в текущем runtime.
- React/Next.js runtime отсутствует.
- Dockerfile собирает приложение на `python:3.11-slim`.
- Docker compose монтирует `./instance` в `/app/instance`.

### Реальные routes

Проверено через `create_app().routes`.

Public / служебные:

- `GET /`
- `GET /health`
- `GET /login`
- `POST /login`
- `POST /logout`
- FastAPI docs routes (`/docs`, `/redoc`, `/openapi.json`) включены по умолчанию.
- static mounts: `/static`, `/assets`.

Learning UI:

- `GET /dashboard`
- `GET /recap`
- `GET /courses/{course_slug}`
- `GET /lessons/{lesson_key}`
- `POST /lessons/{lesson_key}/complete`
- `POST /lessons/{lesson_key}/submissions`
- `POST /checkpoints/{checkpoint_slug}/submissions`
- `POST /lessons/{lesson_key}/stuck`
- `POST /stuck/{event_id}/resolve`

AI helper API:

- `POST /api/ai-helper/history`
- `POST /api/ai-helper/chat`
- `POST /api/ai-helper/clear`

Terminal API:

- `GET /api/terminal/lessons/{lesson_key}/history`
- `POST /api/terminal/lessons/{lesson_key}/run`

Missing for target epic:

- `GET /courses` catalog page отсутствует.
- Course request routes отсутствуют.
- Admin routes отсутствуют.
- User/course assignment routes отсутствуют.

### Runtime DB models

Проверено по `app/models.py`.

Существуют:

- `User`
- `CourseProgress`
- `LessonProgress`
- `TaskSubmission`
- `ReviewResult`
- `CheckpointSubmission`
- `CheckpointReview`
- `StuckEvent`
- `TerminalRun`
- `AIHelperMessage`

Отсутствуют:

- `CourseRequest`
- явная модель membership/assignment пользователя к курсу;
- admin audit/status model для content validation;
- Alembic migrations.

### Content model

Проверено по `app/content_pipeline.py`, `app/content_loader.py`, `content/` и `scripts/validate_content.py`.

Сейчас content уже file-based:

- `content/courses/{course_slug}/course.yml`
- `content/courses/{course_slug}/modules/{module_slug}/module.yml`
- `content/courses/{course_slug}/modules/{module_slug}/lessons/*.md`
- shared tasks: `content/tasks/*.yml`
- shared checkpoints: `content/checkpoints/*.yml`
- shared source registry: `content/sources/source_registry.yml`

Текущее validation покрывает:

- pydantic schemas для course/module/lesson/task/checkpoint/source registry;
- duplicate course/module/lesson/task/checkpoint slugs;
- ссылки course -> modules;
- ссылки module -> lessons/checkpoint;
- ссылки lesson -> task;
- наличие `source_ids` в lesson;
- существование `source_id` в shared source registry;
- обязательные lesson sections в текущем англо-русском стандарте;
- orphan tasks;
- orphan checkpoints;
- непустые markdown bodies.

Разрыв с целевым Course Pack Contract:

- `course.yml` еще не требует `schema_version`, `level`, `language`, `status`, `tags`, `audience`, `outcomes`, `final_artifact`.
- `module.yml` еще использует `description` и `block`; целевой контракт ожидает `summary`, `order`, `objectives`, `lessons`, `checkpoint`.
- `lesson.md` еще использует `key`, `summary`, `checklist`, `task_slug`; целевой контракт ожидает `schema_version`, `slug`, `order`, `estimated_minutes`, `level`, `task_slugs`, `checkpoint_slug`.
- обязательные lesson sections сейчас: `Why this matters (RU)`, `What to read (EN source)`, `What to skip`, `Action`, `Definition of Done`, `Technical English`; целевые русские секции еще не включены как контракт.
- tasks/checkpoints сейчас глобальные (`content/tasks`, `content/checkpoints`), а не вложенные внутрь course pack.
- source registry сейчас глобальный (`content/sources/source_registry.yml`), а не course-local `sources.yml`.
- course status `draft / available / archived` не валидируется и не влияет на learner-visible catalog.

### Content inventory

Проверено командой `python scripts/validate_content.py`.

- Courses: 3
- Modules: 5
- Lessons: 15
- Tasks: 8
- Checkpoints: 5

Validation status: OK, ошибок не найдено.

### Auth state

Проверено по `app/routers/auth.py`, `scripts/create_user.py`, `scripts/reset_users.py`, `scripts/reset_password.py`, `app/security.py`.

Working:

- login/logout через session;
- password hashing через `pwdlib[argon2]`;
- `User.role` существует;
- `is_active` проверяется при login;
- seed/create/reset scripts есть.

Partial / missing:

- публичной регистрации нет — это соответствует целевому friends-only режиму;
- `scripts/create_user.py` сейчас создает пользователя с `role="admin"`;
- learner creation flow отдельным явным CLI не оформлен;
- role-based admin route protection пока не проверяется, потому что admin routes отсутствуют;
- user-course assignment отсутствует, learner после login видит hardcoded active course flow.

### Dashboard и single-course assumptions

Проверено по `app/routers/dashboard.py` и `app/content_registry.py`.

Текущий dashboard hardcoded на курс `python-backend-ai-foundation`.

Следствия:

- LMS не может быть пустой без дополнительных изменений dashboard flow;
- dashboard не является универсальным списком активных курсов пользователя;
- `/recap` также привязан к `python-backend-ai-foundation`.

### Catalog state

Проверено по `app/routers/content.py` и templates.

Working:

- есть страница конкретного курса `GET /courses/{course_slug}`;
- course page показывает карту модулей, уроки, checkpoints и progress для выбранного курса.

Missing:

- нет `GET /courses`;
- нет course cards;
- нет filtering по `status`;
- нет empty-state для пустой LMS;
- нет template courses catalog.

### Terminal / code execution surface

Проверено по `app/routers/terminal.py`, `app/services/terminal_service.py`, `app/models.py` и README.

Working:

- terminal API привязан к lesson/task;
- запуск доступен только после login;
- task должен явно включать terminal;
- есть whitelist/normalization allowed commands;
- результаты сохраняются в `TerminalRun`.

Risk / future hardening:

- это trusted/local learning runner, не полноценная security boundary;
- перед VPS/friends этапом нужен feature flag / deployment checklist, чтобы публичный untrusted code execution не был случайно включен.

### AI helper state

Проверено по `app/routers/ai_helper.py`, `app/services/ai_helper_service.py`, `app/models.py`.

Working:

- context-scoped helper API существует;
- history хранится в `AIHelperMessage`;
- helper требует login;
- есть feature flag `PERSONAL_LMS_AI_HELPER_ENABLED`.

Out of scope for this decomposition step:

- генерация полного курса внутри приложения;
- автозаливка course pack из UI.

### CI / checks

Проверено по `.github/workflows/ci.yml` и локальным командам.

CI включает:

- Python 3.11 setup;
- editable install;
- `ruff check .`;
- `python scripts/check_text_integrity.py`;
- `python scripts/validate_content.py`;
- `python -m pytest`;
- Docker build;
- Docker compose smoke health check.

Локально 2026-05-06:

- `python --version` вернул `Python 3.14.4`, то есть локальная среда не совпадает с CI Python 3.11.
- `python -m pytest` прошел: 70 tests passed.
- `python scripts/validate_content.py` прошел.
- `python scripts/check_text_integrity.py` прошел.
- `ruff check .` прошел.
- `docker build -t personal-lms:audit .` не выполнен, потому что `docker` отсутствует в текущей среде.

## Working / partial / missing по EPIC

### Working

- Закрытый login/logout без self-signup.
- File-based content loading из `content/`.
- Validation pipeline и CLI `scripts/validate_content.py`.
- Course detail page `/courses/{course_slug}`.
- Lesson page с task submission/review/stuck flow.
- Checkpoint submissions/review model.
- Progress runtime state.
- AI helper feature flag.
- Lesson-scoped terminal API для trusted/local MVP.
- Tests и CI workflow.

### Partial

- Multi-course content root есть, но learner flow все еще привязан к одному active course.
- Course schemas существуют, но не соответствуют целевому переносимому Course Pack Contract.
- Source validation есть, но source registry глобальный, а не course-local `sources.yml`.
- User roles есть, но admin UI/routes отсутствуют.
- Docker artifacts есть, но README говорит, что production deployment временно заморожен.
- Alembic dependency есть, но migrations scaffold отсутствует.

### Missing

- Universal course catalog `/courses`.
- Course status `draft / available / archived` в schema и UI.
- Empty LMS state.
- Course-local pack structure with `sources.yml`, nested tasks/checkpoints.
- Strict Course Pack Contract docs.
- Target validation tests: missing source, orphan lesson, invalid task, duplicate slug, invalid status under new contract.
- CourseRequest DB model.
- Learner course request form.
- Admin course request list/detail/status notes.
- Copyable ChatGPT prompt for course generation.
- Codex/Cursor course import handoff docs.
- Course assignment / learner-visible permissions.
- VPS/friends hardening checklist around terminal/code execution and docs exposure.

## Инкрементальный decomposition plan

### Этап 1 — Audit и stabilization

Status: начат этим документом.

Минимальные следующие шаги:

1. Держать этот документ как проверенную baseline-карту.
2. Не менять README до фактического изменения runtime.
3. Не начинать CourseRequest/Admin до того, как catalog перестанет быть hardcoded single-course.

### Этап 2 — Universal course catalog

Small safe implementation slice:

1. Добавить catalog service поверх существующего `ContentIndex` без изменения DB.
2. Расширить `CourseContent` минимальными optional metadata fields: `status`, `level`, `duration_weeks`, `tags`, `outcomes`.
3. Добавить backward-compatible defaults для существующих `course.yml`.
4. Добавить `GET /courses` и template с empty state.
5. Изменить dashboard так, чтобы он показывал список available courses и корректный empty-state, но не ломал текущий active course.
6. Draft/archived скрывать от learner в catalog.

Acceptance для slice:

- существующие tests проходят;
- `python scripts/validate_content.py` проходит;
- `/courses` доступен после login;
- текущий курс остается доступен по `/courses/python-backend-ai-foundation`;
- при пустом `content/courses` catalog service умеет вернуть empty list без exception.

### Этап 3 — Course Pack Contract hardening

Small safe implementation slice:

1. Создать `docs/course_authoring/COURSE_PACK_CONTRACT.md` как target contract.
2. Ввести schema_version/status как backward-compatible optional сначала, затем сделать required после миграции existing content.
3. Поддержать course-local `sources.yml` параллельно с global registry на transition period.
4. Поддержать nested course tasks/checkpoints параллельно с current shared directories.
5. Добавить tests для нового contract behavior.
6. Только после этого переносить существующий content pack к целевому layout.

### Этап 4 — Generated users auth model

Small safe implementation slice:

1. Добавить CLI опцию/скрипт для создания learner/admin без публичной регистрации.
2. Документировать user creation в отдельном docs файле, не меняя README до runtime подтверждения.
3. Добавить role helper/service для `is_admin`.
4. Подготовить future course assignment model, но не блокировать catalog на этом шаге.

### Этап 5 — Course Request feature

Small safe implementation slice:

1. Добавить `CourseRequest` SQLModel.
2. Добавить create/list/detail service.
3. Добавить learner route для формы заявки.
4. Добавить admin list/detail с ручной сменой status и notes.
5. Добавить copyable prompt text как deterministic server-side formatting.

### Этап 6 — Course import workflow

Small safe implementation slice:

1. Добавить docs/handoff prompt for ChatGPT.
2. Добавить docs/handoff prompt for Codex/Cursor.
3. Уточнить `scripts/scaffold_course.py` под target contract.
4. Добавить `scripts/validate_course_pack.py` для single pack validation.
5. Сохранить `scripts/validate_content.py` как full graph preflight.

### Этап 7 — VPS/friends hardening

Small safe implementation slice:

1. Добавить deployment checklist.
2. Проверить docs exposure in FastAPI for non-debug mode.
3. Добавить terminal/code runner feature flag или hard deployment warning.
4. Проверить `.env.example` на обязательные secrets и safe defaults.
5. Проверить Docker compose health path and volume behavior.

## Рекомендуемый следующий PR

Следующий PR должен быть ограничен Stage 2 slice:

- catalog service;
- `/courses` route;
- catalog template;
- backward-compatible course metadata;
- tests for catalog visibility and empty state.

Не включать в следующий PR:

- CourseRequest;
- admin UI;
- course pack migration;
- VPS hardening;
- AI course generation.
