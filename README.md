# personal-lms

Self-hosted LMS-like платформа для обучения Python backend + AI.

## Актуальный статус (на 18 апреля 2026)

Сейчас репозиторий содержит рабочий MVP с execution-first фокусом:

- аутентификация (login/logout) и защищенный dashboard;
- file-based контент из `content/` (курс -> модули -> уроки + tasks + checkpoints);
- страница курса (`/courses/{course_slug}`) с прогрессом и checkpoint-блоками;
- страница урока (`/lessons/{lesson_key}`): чтение, задача, submission, review, stuck flow;
- recap страница (`/recap`) с weekly summary;
- lesson-scoped учебный терминал через API (`/api/terminal/...`) с sandbox-ограничениями;
- встроенный Lain Helper v0: floating launcher + mini-chat lesson-aware AI-тьютора;
- persistence runtime state в SQLite через SQLModel.

## Что в проекте сейчас

### Backend

- FastAPI app (`app/main.py`)
- SSR шаблоны на Jinja2 (`app/templates/`)
- SQLModel модели (`app/models.py`)
- SQLite database (`instance/personal_lms.db`)
- инициализация схемы через `scripts/init_db.py`

### Frontend

- server-rendered страницы
- кастомные стили в `app/static/css/app.css`
- ванильный JS в `app/static/js/app.js`

Примечание: Tailwind/Alpine в текущей runtime-реализации не используются. Tailwind может быть добавлен позже отдельным решением.

### Контент

Контент хранится в файлах:

- `content/courses/` — курс, модули, уроки (Markdown + front matter)
- `content/tasks/` — task definitions (YAML)
- `content/checkpoints/` — checkpoint definitions (YAML)

Текущий content snapshot:

- 1 курс
- 2 модуля
- 3 урока
- 1 task
- 1 checkpoint

## Структура репозитория

```text
app/
  routers/        # auth/content/dashboard/terminal
  services/       # progress/execution/stuck/terminal/... 
  templates/      # base, dashboard, course_map, lesson, recap, login
  static/         # app.css, app.js
content/
  courses/
  tasks/
  checkpoints/
instance/
  personal_lms.db
  terminal/       # sandbox-данные учебного терминала
scripts/
  init_db.py
  create_user.py
  reset_password.py
docs/
  START_HERE.md
  product/
```

## Стек

- FastAPI
- Jinja2
- SQLite
- SQLModel
- Alembic (dependency only; scaffold пока не заведен)
- Vanilla CSS + Vanilla JS
- Markdown + YAML для file-based контента

## Быстрый старт

### 1. Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -e .
```

### 2. Конфигурация

```bash
cp .env.example .env
```

Обязательный минимум:

- `PERSONAL_LMS_SESSION_SECRET_KEY`

Для Lain Helper:

- `PERSONAL_LMS_AI_HELPER_ENABLED`
- `PERSONAL_LMS_OPENAI_API_KEY` (если helper включен)
- `PERSONAL_LMS_AI_HELPER_MODEL` (опционально)
- `PERSONAL_LMS_AI_HELPER_TIMEOUT_SECONDS` (опционально)

### 3. Инициализация БД

```bash
source .venv/bin/activate
python3 scripts/init_db.py
```

### 4. Создание администратора

```bash
source .venv/bin/activate
python3 scripts/create_user.py
```

### 5. Сброс пароля (опционально)

```bash
source .venv/bin/activate
python3 scripts/reset_password.py
```

### 6. Запуск

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

## Основные маршруты

- `GET /health`
- `GET /login`
- `POST /login`
- `POST /logout`
- `GET /dashboard`
- `GET /courses/{course_slug}`
- `GET /lessons/{lesson_key}`
- `POST /lessons/{lesson_key}/submissions`
- `POST /lessons/{lesson_key}/complete`
- `POST /lessons/{lesson_key}/stuck`
- `POST /checkpoints/{checkpoint_slug}/submissions`
- `POST /stuck/{event_id}/resolve`
- `GET /recap`
- `GET /api/terminal/lessons/{lesson_key}/history`
- `POST /api/terminal/lessons/{lesson_key}/run`
- `POST /api/ai/helper`

## Учебный терминал (MVP)

Терминал lesson-scoped и ограничен grammar/whitelist правилами:

- sandbox путь: `instance/terminal/{user_id}/{lesson_key}`
- команды валидируются по `allowed_commands` задачи
- может быть отключен manual input (только preset-команды)
- timeout команд: 5 секунд
- stdout/stderr обрезаются до 12_000 символов
- каждый запуск сохраняется как `TerminalRun`

## Lain Helper v0

Lain — встроенный lesson-scoped AI-тьютор внутри LMS:

- floating launcher внизу справа на внутренних страницах;
- mini-chat panel с quick actions (`Объясни текущий урок`, `Помоги начать`, `Я застрял`, `Проверь мой ответ`);
- endpoint: `POST /api/ai/helper`;
- ответы ограничены контекстом текущего урока и guardrails-логикой;
- interaction log сохраняется в `LainHelperInteraction`.

## Тесты

```bash
source .venv/bin/activate
pytest
```

Сейчас в репозитории базовый smoke test (`tests/test_app_smoke.py`).

## UI sandbox

Для локальных UI-экспериментов подключен Storybook:

```bash
npm run storybook
npm run build-storybook
```

## Документация продукта

Канонический продуктовый контекст: `docs/product/`.

Рекомендуемый вход:

1. `docs/START_HERE.md`
2. `docs/product/PRODUCT_VISION.md`
3. `docs/product/MVP_SCOPE.md`
4. `docs/product/ARCHITECTURE_OVERVIEW.md`

## Ограничения MVP

- без React/Next.js
- без split frontend/backend
- без browser IDE
- без multi-tenant архитектуры
- без расползания scope без явного решения
