# personal-lms

Personal learning OS для Python backend + AI.

## Что это

`personal-lms` — это не обычный LMS и не курс.

Это personal learning system, которая:
- строит маршрут обучения;
- связывает источники с практикой;
- заставляет выполнять задачи, а не просто читать;
- фиксирует progress, submissions и review.

## Почему это существует

Проблема:
- слишком много материалов;
- нет понятного next step;
- легко попасть в tutorial hell.

Решение:
- фиксированный маршрут;
- execution-first подход;
- система progress + review.

Self-hosted LMS-платформа для обучения Python backend и AI application foundations.

Phase 3 добавляет file-based загрузку контента: карта курса и страницы уроков из `content/`.

## Текущее продуктовое направление

Проект развивается как execution-driven, source-backed LMS с целевой траекторией:

**Python backend + AI practical builder path**

Приоритет текущего этапа — довести платформу до устойчивого authoring/runtime состояния перед массовым curriculum onboarding.

## Канонический продуктовый контекст

Базовые source-of-truth документы проекта находятся в `docs/product/`:

- [`PRODUCT_VISION.md`](docs/product/PRODUCT_VISION.md) — продуктовый смысл и проблема, которую решает `personal-lms`.
- [`MVP_SCOPE.md`](docs/product/MVP_SCOPE.md) — границы MVP, стек и anti-scope правила.
- [`CONTENT_STRATEGY.md`](docs/product/CONTENT_STRATEGY.md) — source-backed curriculum и curation внешних источников.
- [`LEARNING_MODEL.md`](docs/product/LEARNING_MODEL.md) — маршрут, progress, tasks, submissions, review и stuck flow.
- [`ARCHITECTURE_OVERVIEW.md`](docs/product/ARCHITECTURE_OVERVIEW.md) — web-first архитектура MVP.
- [`CURRICULUM_ARCHITECTURE.md`](docs/product/CURRICULUM_ARCHITECTURE.md) — целевая архитектура 6-месячного курса.
- [`SOURCE_STACK.md`](docs/product/SOURCE_STACK.md) — канонический source-backed стек.
- [`MONETIZATION_PATH.md`](docs/product/MONETIZATION_PATH.md) — ранние monetizable outcomes и прикладной путь.
- [`PLATFORM_FIRST_ROADMAP.md`](docs/product/PLATFORM_FIRST_ROADMAP.md) — порядок docs freeze → hardening → onboarding.
- [`AUTHORING_MODEL.md`](docs/product/AUTHORING_MODEL.md) — модель authoring и lifecycle учебного контента.
- [`UI_DIRECTION.md`](docs/product/UI_DIRECTION.md) — linux-like / anime Lain / hacker-workstation UX-направление.
- [`UI_BASELINE.md`](docs/product/UI_BASELINE.md) — принятый dark matte glass UI baseline для будущих UI-изменений.
- [`PROJECT_GUARDRAILS.md`](docs/product/PROJECT_GUARDRAILS.md) — ограничения, которые защищают проект от scope creep.

## Статус проекта

MVP в активной разработке.

Текущая цель — проверить:
- может ли personal LMS вести обучение лучше, чем хаотичный self-study;
- может ли execution-first модель снижать tutorial hell.

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
