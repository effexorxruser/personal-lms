# personal-lms

Personal learning OS для Python backend + AI.

## Что это

`personal-lms` — personal learning system, а не каталог ссылок и не "видеокурс".

Система:
- строит маршрут обучения;
- связывает внешние источники с практикой;
- требует execution, а не только consumption;
- фиксирует progress, submissions и review.

## Куда проект развивается сейчас

Текущий product direction:

- execution-driven, source-backed LMS;
- целевая траектория: **Python backend + AI practical builder path**;
- прикладная ветка текущего этапа: Telegram / automation / AI utility tools;
- приоритет: platform hardening и authoring/runtime readiness до массового curriculum onboarding.

## Что уже реализовано (текущее состояние)

- web-first MVP на FastAPI + Jinja2;
- аутентификация и защищенный dashboard;
- file-based карта курса и страницы уроков из `content/`;
- базовый learning flow (курс/уроки/progress/task/submission/review) в развитии.

## Канонический продуктовый контекст

Source-of-truth документы находятся в `docs/product/`.

Нейминг-канон для product docs в текущем репозитории: `UPPER_SNAKE_CASE.md`.

- [`PRODUCT_VISION.md`](docs/product/PRODUCT_VISION.md)
- [`MVP_SCOPE.md`](docs/product/MVP_SCOPE.md)
- [`CONTENT_STRATEGY.md`](docs/product/CONTENT_STRATEGY.md)
- [`LEARNING_MODEL.md`](docs/product/LEARNING_MODEL.md)
- [`ARCHITECTURE_OVERVIEW.md`](docs/product/ARCHITECTURE_OVERVIEW.md)
- [`CURRICULUM_ARCHITECTURE.md`](docs/product/CURRICULUM_ARCHITECTURE.md)
- [`SOURCE_STACK.md`](docs/product/SOURCE_STACK.md)
- [`MONETIZATION_PATH.md`](docs/product/MONETIZATION_PATH.md)
- [`PLATFORM_FIRST_ROADMAP.md`](docs/product/PLATFORM_FIRST_ROADMAP.md)
- [`AUTHORING_MODEL.md`](docs/product/AUTHORING_MODEL.md)
- [`UI_DIRECTION.md`](docs/product/UI_DIRECTION.md)
- [`UI_BASELINE.md`](docs/product/UI_BASELINE.md)
- [`PROJECT_GUARDRAILS.md`](docs/product/PROJECT_GUARDRAILS.md)

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

## Roadmap (high-level)

- documentation freeze продуктового контекста
- platform hardening (stuck/recap/terminal-like/lesson AI helper)
- authoring readiness и первый curriculum pass
- расширение контента (source-backed)

## Для разработчиков

Если вы хотите разобраться в проекте:

1. Начните с `docs/product/PRODUCT_VISION.md`
2. Затем `MVP_SCOPE.md`
3. Затем `ARCHITECTURE_OVERVIEW.md`

## Open Source

Проект готовится к постепенному открытию.

Перед добавлением изменений важно учитывать ограничения из:
- docs/product/PROJECT_GUARDRAILS.md
