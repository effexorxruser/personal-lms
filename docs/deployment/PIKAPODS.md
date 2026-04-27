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

## Примечание про SQLite volume

Для сохранения runtime state между рестартами контейнера обязательно монтировать volume/папку в `/app/instance`.

## Deployable image

- Релизный Docker-образ собирается через GitHub Actions workflow `.github/workflows/container.yml` (manual release).
- Workflow публикует образ в GitHub Container Registry (GHCR):
  - `ghcr.io/effexorxruser/personal-lms:latest`
  - `ghcr.io/effexorxruser/personal-lms:<short-sha>`
  - `ghcr.io/effexorxruser/personal-lms:<version>`

## Deployment checklist (PikaPods)

### 1) Backup перед обновлением

- Убедиться, что есть доступ к текущему контейнеру.
- Сделать копию runtime-данных (минимум `instance/lms.db`).
- Сохранить backup вне контейнера (локально или в безопасное хранилище).

Пример локального бэкапа:

```bash
cp instance/lms.db instance/lms.db.bak-$(date +%Y%m%d-%H%M%S)
```

### 2) Deploy новой версии

- Выбрать нужный релизный тег `vX.Y.Z`.
- В PikaPods обновить Docker image на:
  - `ghcr.io/effexorxruser/personal-lms:vX.Y.Z`
- Проверить, что volume по-прежнему смонтирован в `/app/instance`.
- Перезапустить контейнер.

### 3) Post-deploy health check

- Проверить endpoint:

```bash
curl -fsS https://<your-domain>/health
```

- Проверить логин админом и открытие dashboard.
- Проверить, что курсы и прогресс читаются из текущей БД.

### 4) Rollback procedure

Если после деплоя есть регресс:

1. В PikaPods вернуть предыдущий стабильный image tag (`vX.Y.Z` -> `vX.Y.(Z-1)` или конкретный `<short-sha>`).
2. Перезапустить контейнер.
3. Если проблема в данных, восстановить `instance/lms.db` из последнего backup.
4. Снова проверить `/health`, логин и основные user flows.

Rollback считается завершённым, когда healthcheck зелёный и ключевые пользовательские сценарии проходят.
