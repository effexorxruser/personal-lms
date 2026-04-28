# personal-lms

Self-hosted LMS-like платформа для обучения Python backend + AI.

## Актуальный статус

Сейчас репозиторий содержит рабочий MVP с execution-first фокусом:

- аутентификация (login/logout) и защищенный dashboard;
- file-based контент из `content/` (курс -> модули -> уроки + tasks + checkpoints);
- страница курса (`/courses/{course_slug}`) с прогрессом и checkpoint-блоками;
- страница урока (`/lessons/{lesson_key}`): чтение, задача, submission, review, stuck flow;
- recap страница (`/recap`) с weekly summary;
- lesson-scoped учебный терминал через API (`/api/terminal/...`) с sandbox-ограничениями;
- встроенный Lain Helper v1.0: floating capsule launcher + context-scoped mini-chat AI-тьютора с history/clear/socratic toggle;
- content authoring pipeline: схемы, graph validation и scaffold scripts для новых курсов;
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
- 1 модуль
- 3 урока
- 3 tasks
- 1 checkpoint

Примечание: runtime переключён на реальный foundation-маршрут `python-backend-ai-foundation`; legacy transitional baseline удалён из пользовательского потока.

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

## Deployment

**Статус:** контур production-деплоя (PikaPods / VPS) **временно заморожен**. Актуальный режим использования — **локальный запуск из WSL/Linux** (`bash scripts/start_local.sh`). Docker-файлы и инструкции в `docs/deployment/` сохранены для будущего возобновления.

Ранее для MVP планировалось:

- PikaPods
- Docker
- SQLite (volume)
- без обязательного домена

## Локальный запуск через WSL

1. Откройте терминал WSL (или любой Linux shell в клоне репозитория).
2. Перейдите в корень репозитория `personal-lms`.
3. Запустите:

   ```bash
   bash scripts/start_local.sh
   ```

4. На **ноутбуке** откройте в браузере: `http://127.0.0.1:8000`
5. На **телефоне** (та же Wi‑Fi сеть): `http://<LAN_IP>:8000`, где `<LAN_IP>` — адрес ноутбука в Wi‑Fi (скрипт печатает best-effort значение; при проблемах см. `docs/local/PHONE_ACCESS.md`).

**Примечания:**

- Ноутбук и телефон должны быть в **одной Wi‑Fi** сети.
- Если с телефона сайт не открывается, проверьте **Windows Firewall** и антивирус.
- Для **WSL2** иногда нужен проброс порта на стороне Windows (`netsh interface portproxy`) — это troubleshooting, не обязательный шаг; см. `docs/local/PHONE_ACCESS.md`.

Проверка, что сервер поднят (в **другом** терминале):

```bash
bash scripts/health_local.sh
```

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

### 6. Сброс пользователей и runtime-данных (опционально)

```bash
source .venv/bin/activate
python3 scripts/reset_users.py
```

Для non-interactive запуска (без prompt подтверждения):

```bash
source .venv/bin/activate
python3 scripts/reset_users.py --yes
```

### 7. Запуск

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
- `POST /api/ai-helper/history`
- `POST /api/ai-helper/chat`
- `POST /api/ai-helper/clear`

## Учебный терминал (MVP)

Терминал lesson-scoped и ограничен grammar/whitelist правилами:

- sandbox путь: `instance/terminal/{user_id}/{lesson_key}`
- команды валидируются по `allowed_commands` задачи
- может быть отключен manual input (только preset-команды)
- timeout команд: 5 секунд
- stdout/stderr обрезаются до 12_000 символов
- каждый запуск сохраняется как `TerminalRun`

## Lain Helper v1.0

Lain — встроенный context-scoped AI-тьютор внутри LMS:

- floating launcher/capsule внизу справа на внутренних страницах;
- mini-chat panel с compact quick actions, `online/thinking` индикатором и отдельным toggle сократического режима;
- endpoint-ы: `POST /api/ai-helper/history`, `POST /api/ai-helper/chat`, `POST /api/ai-helper/clear`;
- ответы ограничены текущим учебным контекстом (урок/курс/страница) и guardrails-логикой;
- история чата хранится по `context_key` и очищается отдельно для текущего контекста;
- evidence-слой учитывает недавние lesson-scoped terminal runs, если они есть;
- interaction log сохраняется в `AIHelperMessage`.

## Content Pipeline (authoring readiness)

Контентная модель остается file-based, но теперь добавлен явный preflight:

- централизованные схемы: `app/content_pipeline.py`;
- graph integrity checks (references/duplicates/orphans);
- preflight скрипт: `python scripts/validate_content.py`;
- scaffold scripts:
  - `python scripts/scaffold_course.py`
  - `python scripts/scaffold_module.py`
  - `python scripts/scaffold_lesson.py`
  - `python scripts/scaffold_task.py`
  - `python scripts/scaffold_checkpoint.py`

Рекомендуемый локальный workflow перед commit:

```bash
source .venv/bin/activate
python scripts/validate_content.py
python -m pytest
```

## Тесты

```bash
source .venv/bin/activate
python -m pytest
```

## CI/CD

- CI запускается в GitHub Actions на `pull_request` и `push` в `master`/`main`.
- CI проверяет `ruff check .`, `python scripts/check_text_integrity.py`, `python scripts/validate_content.py`, `python -m pytest` и сборку Docker-образа.
- Отдельный release workflow запускается вручную (`workflow_dispatch`), публикует образ в GHCR и создает GitHub Release.
- Деплой в PikaPods пока выполняется вручную по инструкции: `docs/deployment/PIKAPODS.md`.

Ключевые наборы тестов:

- `tests/test_app_smoke.py` — базовый smoke/regression сценарий;
- `tests/test_ai_helper.py` — backend/guardrails/history тесты Lain helper;
- `tests/test_ai_helper_ui.py` — SSR/UI рендер helper на внутренних страницах.
- `tests/test_content_validation.py` — schema validation контента;
- `tests/test_content_integrity.py` — graph integrity checks;
- `tests/test_content_scaffold.py` — scaffold scripts + preflight.

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
- terminal execution surface не является полноценным shell
- sandbox/whitelist терминала не является полноценной security boundary для untrusted/public execution
- Lain Helper v1.0 не завершает задачи за пользователя и не выдает autopilot-решения
- MVP не является public-ready multi-user платформой
