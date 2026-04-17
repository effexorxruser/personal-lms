# personal-lms

Self-hosted LMS-платформа для обучения Python backend и AI application foundations.

Phase 3 добавляет file-based загрузку контента: карта курса и страницы уроков из `content/`.

## Канонический продуктовый контекст

Базовые source-of-truth документы проекта находятся в `docs/product/`:

- [`PRODUCT_VISION.md`](docs/product/PRODUCT_VISION.md) — продуктовый смысл и проблема, которую решает `personal-lms`.
- [`MVP_SCOPE.md`](docs/product/MVP_SCOPE.md) — границы MVP, стек и anti-scope правила.
- [`CONTENT_STRATEGY.md`](docs/product/CONTENT_STRATEGY.md) — source-backed curriculum и curation внешних источников.
- [`LEARNING_MODEL.md`](docs/product/LEARNING_MODEL.md) — маршрут, progress, tasks, submissions, review и stuck flow.
- [`UI_DIRECTION.md`](docs/product/UI_DIRECTION.md) — linux-like / anime Lain / hacker-workstation UX-направление.
- [`UI_BASELINE.md`](docs/product/UI_BASELINE.md) — принятый dark matte glass UI baseline для будущих UI-изменений.
- [`ARCHITECTURE_OVERVIEW.md`](docs/product/ARCHITECTURE_OVERVIEW.md) — web-first архитектура MVP.
- [`PROJECT_GUARDRAILS.md`](docs/product/PROJECT_GUARDRAILS.md) — ограничения, которые защищают проект от scope creep.

## Стек

- FastAPI
- Jinja2 templates
- SQLite
- SQLModel
- Alembic
- Tailwind CSS
- Alpine.js

## Языковая политика

- UI и пользовательский слой ведутся на русском языке.
- Документация MVP ведется на русском языке.
- Исключения: env vars, file names, route paths, команды, technical identifiers и имена зависимостей остаются на английском.
- Multi-language support и i18n не добавляются до отдельного решения.

## Установка зависимостей

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -e .
```

## Конфигурация

Скопируйте `.env.example` в `.env` и задайте `PERSONAL_LMS_SESSION_SECRET_KEY`.

```bash
cp .env.example .env
```

## Инициализация базы данных

```bash
source .venv/bin/activate
python3 scripts/init_db.py
```

## Создание администратора

```bash
source .venv/bin/activate
python3 scripts/create_user.py
```

## Сброс пароля

```bash
source .venv/bin/activate
python3 scripts/reset_password.py
```

## Запуск приложения

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

Основные страницы:
- `GET /login` — форма входа
- `GET /dashboard` — защищенная панель
- `GET /courses/python-backend-ai` — карта курса
- `GET /lessons/{lesson_key}` — страница урока

## Запуск тестов

```bash
source .venv/bin/activate
pytest
```
