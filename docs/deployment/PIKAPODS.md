# PikaPods deployment (MVP)

PikaPods — простой managed-хостинг для self-hosted приложений в Docker-контейнерах. Для `personal-lms` в MVP достаточно одного контейнера с volume для `instance/`.

## Что деплоим

- FastAPI + Jinja2 SSR
- SQLite (файл БД в `instance/`)
- один контейнер, без PostgreSQL

## ENV переменные

Обязательный минимум:

- `PERSONAL_LMS_SESSION_SECRET_KEY`

AI helper переменные:

- `PERSONAL_LMS_AI_HELPER_ENABLED`
- `PERSONAL_LMS_OPENAI_API_KEY`
- `PERSONAL_LMS_AI_HELPER_MODEL`
- `PERSONAL_LMS_AI_HELPER_TIMEOUT_SECONDS`

Важно: `PERSONAL_LMS_OPENAI_API_KEY` не обязателен, если `PERSONAL_LMS_AI_HELPER_ENABLED=false`.

## Локальная проверка через Docker

```bash
docker compose up --build
```

Проверка health:

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:

```json
{"status":"ok"}
```

## Инициализация БД и создание пользователя (первый запуск)

После старта контейнера выполните команды внутри проекта/контейнера:

```bash
python scripts/init_db.py
python scripts/create_user.py
```

Важно:

- пользователь не создаётся автоматически;
- логин/пароль не хардкодятся в коде.

## Проверка mobile UI

Быстрая проверка mobile read-only режима:

- `http://localhost:8000/dashboard?mobile=1`
- `http://localhost:8000/courses/python-backend-ai-foundation?mobile=1`
- `http://localhost:8000/lessons/foundation-real-workspace?mobile=1`

Также можно открыть обычный `/dashboard` и проверить адаптацию через browser devtools (`max-width: 768px`).

## Примечание про SQLite volume

Для сохранения runtime state между рестартами контейнера обязательно монтировать volume/папку в `/app/instance`.

## Deployable image

- Deployable Docker-образ собирается через GitHub Actions workflow `.github/workflows/container.yml`.
- Workflow публикует образ в GitHub Container Registry (GHCR):
  - `ghcr.io/effexorxruser/personal-lms:latest`
  - `ghcr.io/effexorxruser/personal-lms:<short-sha>`
- Для PikaPods предпочтителен Docker/container deployment path с использованием опубликованного образа, если такой путь доступен в текущем тарифе/интерфейсе.
- Если прямой pull из GHCR недоступен, использовать manual Docker/SFTP/documented update path (ручное обновление контейнерного артефакта по documented процессу).
