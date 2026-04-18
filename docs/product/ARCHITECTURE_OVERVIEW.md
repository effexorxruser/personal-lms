# Architecture Overview

## Назначение документа

Документ фиксирует фактическую архитектуру MVP в текущем репозитории и объясняет, почему она выбрана для execution-first обучения.

Актуализация: 18 апреля 2026.

## Архитектурный формат

`personal-lms` — web-first server-rendered приложение.

- основной режим: локальный запуск;
- без split frontend/backend;
- без multi-service инфраструктуры для MVP;
- UI и пользовательский слой — на русском.

## Фактический стек

### Backend

- FastAPI
- Jinja2 templates
- SQLite
- SQLModel

### Frontend

- HTML templates (SSR)
- кастомный CSS (`app/static/css/app.css`)
- ванильный JS (`app/static/js/app.js`)

### Content layer

- Markdown + YAML
- file-based registry через `app/content_loader.py`

### Важно про Tailwind/Alpine

В текущей runtime-реализации Tailwind CSS и Alpine.js не используются.
Они могут быть добавлены позже только отдельным решением, если это даст прямую пользу learning flow.

## Почему FastAPI + Jinja2

- быстрый Python-first backend для маршрутов и form actions;
- простой SSR-слой без SPA-complexity;
- достаточно для MVP-цикла: урок -> задача -> выполнение -> фиксация результата.

## Почему SQLite + SQLModel

- минимальный операционный overhead в локальном режиме;
- достаточно для single-user trusted MVP;
- хорошо подходит под runtime state (progress, submissions, stuck, terminal runs).

## Контент и runtime state

Базовый принцип проекта соблюдается в коде:

- контент хранится в файлах (`content/`);
- runtime state хранится в БД (`instance/personal_lms.db`).

Это разделение позволяет:

- версионировать учебный материал через git;
- отдельно эволюционировать runtime-модели.

## Текущие runtime сущности (SQLModel)

В БД уже есть ключевые таблицы:

- `User`
- `CourseProgress`
- `LessonProgress`
- `TaskSubmission`
- `ReviewResult`
- `CheckpointSubmission`
- `CheckpointReview`
- `StuckEvent`
- `TerminalRun`
- `LainHelperInteraction`

Checkpoint уже реализован как отдельная runtime-сущность, а не только как идея на будущее.

## Миграции БД

В зависимостях проекта есть `alembic`, но Alembic scaffold пока не заведен.

Текущий режим:

- схема создается через `SQLModel.metadata.create_all()` (`scripts/init_db.py`);
- это допустимо для локального MVP;
- полноценные versioned migrations нужны до production-like этапа.

## Terminal architecture (MVP)

Учебный терминал реализован как lesson-scoped execution service:

- API: `/api/terminal/lessons/{lesson_key}/history` и `/run`;
- sandbox: `instance/terminal/{user_id}/{lesson_key}`;
- whitelist-грамматика и `allowed_commands` на уровне task;
- timeout и ограничение объема вывода;
- результат каждого запуска пишется в `TerminalRun`.

Это execution surface для обучения, а не универсальный shell и не browser IDE.

## AI helper architecture (Lain v0)

Lain встроена как lesson-scoped tutor channel, а не как отдельный generic chatbot.

- UI: floating launcher + mini-chat panel в базовом layout;
- API: `POST /api/ai/helper`;
- service: `app/services/ai_helper_service.py`;
- runtime log: `LainHelperInteraction`;
- guardrails на уровне prompt + scope/refusal logic;
- режимы: `explain_lesson`, `help_start`, `stuck_help`, `submission_hint`, `free_question`.

Ключевое ограничение: Lain не завершает уроки автоматически, не обходит review/pipeline и не выдает autopilot-решения вместо пользователя.

## Архитектурные границы MVP

В MVP не закладываются:

- React/Next.js фронтенд
- split frontend/backend
- browser IDE
- multi-tenant архитектура
- enterprise complexity

Любое усложнение допустимо только если напрямую улучшает learning flow и execution.
