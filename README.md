# personal-lms

Self-hosted LMS-платформа для обучения Python backend и AI application foundations.

Phase 1 фиксирует только основу приложения: FastAPI bootstrap, Jinja2 templates, SQLite/SQLModel wiring, static assets, placeholder dashboard и smoke tests.

## Стек

- FastAPI
- Jinja2 templates
- SQLite
- SQLModel
- Alembic
- Alpine.js-ready static structure

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

## Запуск приложения

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

Откройте http://127.0.0.1:8000/dashboard.

## Инициализация базы данных

```bash
source .venv/bin/activate
python3 scripts/init_db.py
```

Команда создает SQLite database в `instance/` через текущую SQLModel metadata. В Phase 1 модели базы данных не добавляются.

## Запуск тестов

```bash
source .venv/bin/activate
pytest
```

## Конфигурация

Скопируйте `.env.example` в `.env`, если нужны локальные переопределения.

```bash
cp .env.example .env
```
