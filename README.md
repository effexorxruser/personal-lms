# personal-lms

Self-hosted LMS-платформа для обучения Python backend и AI application foundations.

Phase 3 добавляет file-based загрузку контента: карта курса и страницы уроков из `content/`.

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
