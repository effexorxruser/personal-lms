# Personal LMS General Audit — 2026-04

## 1. Executive summary

**Что уже хорошо**

- Чёткий **file-based content pipeline** с жёсткой graph-валидацией (`app/content_pipeline.py`, `scripts/validate_content.py`): курс ↔ модули ↔ уроки ↔ задачи ↔ checkpoint ↔ `source_registry`, плюс обязательные секции урока и проверка blueprint-файла.
- **Runtime** предсказуем: FastAPI + Jinja2, прогресс и сабмиты в SQLite через SQLModel, без лишнего split frontend/backend.
- **Lain Helper** изолирован: отдельный router, сервис с guardrails, провайдер OpenAI Responses API, история в `LainHelperInteraction`, фронт на `data-ai-*` в `base.html` + `app/static/js/app.js`.
- **Терминал** ограничен sandbox и whitelist команд (`app/services/terminal_service.py`, `app/routers/terminal.py`).
- **Тесты** покрывают контент-граф, Lain (с моками провайдера), smoke по страницам и терминалу.

**Что мешает дальнейшему развитию**

- **UI**: моноширинный глобальный шрифт, многослойные фоны (`page-bg__*`), glass/blur, `text-shadow` на заголовках — атмосфера сильнее, чем **читабельность длинного урока** и визуальный отдых.
- **Курс vs blueprint**: активный маршрут (`python-backend-ai-foundation`) включает **три модуля**, где третий (`foundation-real`, `block: 1`) семантически дублирует block 0 и расходится с **block 1** шестимесячного blueprint (ожидаются другие `module slug` и наборы задач). Часть `expected_tasks` в blueprint не совпадает с фактическими task slug (например `foundation-python-cli-smoke` vs `block-0-python-cli-smoke` для CLI-урока onboarding).
- **Source registry**: только идентификаторы и политика (`id`, `type`, `language`, `allowed_usage`) — **нет URL, секций, кэша, fetch-слоя**; воспроизводимое «прямое» извлечение из web/MCP в коде не реализовано.
- **Runtime-модель контента**: в `app/content_loader.py` у `CheckpointContent` и `LessonContent` не все поля из YAML попадают в объект (см. раздел 5) — часть схемы «только для файлов/валидации».

**Что нельзя ломать в первом refactor**

- Контракты **POST `/api/ai/helper`**, **GET `/api/ai/helper/history`** и JSON-поля, ожидаемые `setupAIHelper()` в `app/static/js/app.js`.
- Атрибуты в разметке Lain: `data-ai-helper`, `data-ai-endpoint`, `data-ai-history-endpoint`, `data-ai-lesson`, `data-ai-mode`, классы `lain-helper*`, `lain-chat*`.
- **Маршруты** SSR: `/dashboard`, `/courses/{slug}`, `/lessons/{key}`, формы complete/submissions/stuck/checkpoints.
- **Graph validation** в `load_content_bundle()` — менять только осознанно, иначе сломается CI и загрузка индекса.

**Что делать первым**

1. Зафиксировать **«focus / readability» UI-тему** (типографика и фон) без перестройки роутов и без изменения контрактов Lain/terminal API.  
2. Параллельно решить **продуктово**: единый «канонический» block 0 (onboarding + learning loop) vs судьба **`foundation-real`** (слияние, архив как эталон структуры или вынос в черновик).  
3. Расширить **метаданные source registry** и off-repo политику кэша **до** массовой перезагрузки контента.

---

## 2. Current architecture map

### Backend

- **Stack**: FastAPI, Jinja2, SQLModel/SQLite, Pydantic v2 (в pipeline), `httpx` для Lain, `markdown` для HTML тела урока.
- **Точка входа**: `app/main.py` — монтирует `/static`, `configure_middleware`, подключает routers: `auth`, `content`, `dashboard`, `terminal`, `ai_helper`; `/health`, редирект `/` → `/dashboard`.

### Routing (файлы)

| Область | Router | Основные пути |
|--------|--------|----------------|
| Auth | `app/routers/auth.py` | `GET/POST /login`, `POST /logout` |
| Контент / обучение | `app/routers/content.py` | `GET /courses/{course_slug}`, `GET /lessons/{lesson_key}`, `POST` complete, submissions, stuck, checkpoint submissions |
| Дашборд / recap | `app/routers/dashboard.py` | `GET /dashboard`, `GET /recap` |
| Terminal API | `app/routers/terminal.py` | `GET/POST /api/terminal/lessons/{lesson_key}/history|run` |
| Lain API | `app/routers/ai_helper.py` | `POST /api/ai/helper`, `GET /api/ai/helper/history` |

### Frontend (SSR)

- Шаблоны: `app/templates/*.html` (отдельных partials нет — всё в шести файлах).
- Стили/скрипты: `app/static/css/app.css`, `app/static/js/app.js`.

### Content

- Курсы: `content/courses/<course>/course.yml` + `modules/<module>/module.yml` + `lessons/*.md`.
- Задачи: `content/tasks/*.yml`. Checkpoint: `content/checkpoints/*.yml`. Источники: `content/sources/source_registry.yml`. Blueprint: `content/blueprints/backend_developer_6_months.yml`.
- Загрузка: `load_content_bundle()` → `load_content_index()` → `get_content_registry()` (`app/content_registry.py`, кэш `@lru_cache`).

### Persistence (progress state)

- **Курс/урок**: `CourseProgress`, `LessonProgress` в `app/models.py`; логика статусов и «следующий урок» — `app/services/progress_service.py`.
- **Задачи**: `TaskSubmission`, `ReviewResult` — `app/services/submission_service.py`, `app/services/review_service.py`.
- **Checkpoint**: `CheckpointSubmission`, `CheckpointReview` — `app/services/checkpoint_service.py`.
- **Stuck**: `StuckEvent` — `app/services/stuck_service.py`.
- **Terminal**: `TerminalRun` — `app/services/terminal_service.py`.
- **Lain**: `LainHelperInteraction` — `app/services/ai_helper_service.py`.

### Lesson / task / checkpoint logic

- Резолв урока и соседей: `app/services/content_service.py` (`get_lesson_or_404`, `lesson_neighbors`, `get_course_or_404`).
- Задача урока: `app/services/task_service.py` (`resolve_lesson_task`).
- Доступность завершения урока и контекст выполнения: `app/services/execution_service.py` (`get_lesson_execution_context`, `can_complete_lesson`).

### AI helper (Lain)

- Режимы: `LainHelperMode` в `app/services/ai_helper_modes.py`.
- Бизнес-логика и промпты: `app/services/ai_helper_service.py` (`assist_with_lain`, `list_lain_history`, `_build_context_text`, guardrails).
- HTTP к OpenAI: `app/services/lain_provider.py` (`request_lain_reply` → `v1/responses`).
- Контекст для шаблонов: `app/services/ai_helper_view.py` (`build_ai_helper_view_context`).
- Конфиг: `app/config.py` (`ai_helper_enabled`, `openai_api_key`, `ai_helper_model`, `ai_helper_timeout_seconds`).

### Terminal / execution

- Ограничение команд, sandbox под `instance/terminal/`, запись `TerminalRun`: `app/services/terminal_service.py`.
- API и привязка к уроку/задаче с `terminal.enabled`: `app/routers/terminal.py`.

### Scripts

- `scripts/validate_content.py`, `scripts/check_text_integrity.py`, scaffold/report утилиты, `scripts/init_db.py`, user admin scripts.

### Tests

- `tests/test_content_validation.py`, `test_content_integrity.py`, `test_app_smoke.py`, `test_ai_helper.py`, `test_ai_helper_ui.py`, др.

### Устойчивые слои (не трогать в первом refactor без задачи)

- `app/content_pipeline.py` (правила графа и схемы).
- Модели таблиц прогресса/сабмитов и ключевые инварианты `progress_service` / `execution_service`.
- Контракты JSON API Lain и Terminal.
- Семантика `LessonFrontMatterSchema` + обязательные секции markdown урока (иначе валидатор и авторский контракт ломаются).

---

## 3. UI/UX findings

### 3.1 Main readability problems

- **Глобальный моношрифт для всего UI** (`body` в `app/static/css/app.css`: JetBrains Mono / Ubuntu Mono / …) — для **длинного прозаического текста урока** это повышает утомляемость; контент конкурирует с «терминальной» эстетикой.
- **Размеры основного текста урока**: `--font-size-md` / `--font-size-lg` ≈ 0.9–0.96rem на фоне плотной тёмной палитры — для extended reading часто хотят чуть крупнее базовый кегль и **пропорциональный** (не моно) шрифт для `.markdown-body`.
- **Двухколоночный layout урока** (`.lesson-page__layout` / `.lesson-page__main` + `.lesson-page__rail` в `app/static/css/app.css`): на широком экране основная колонка может ощущаться уже относительно «шумного» фона; на узком — см. 3.4.

Файлы: `app/static/css/app.css` (`body`, `.markdown-body`, блок `.lesson-page--simple` ~стр. 2917+), `app/templates/lesson.html` (`lesson-page__main`, `markdown-body lesson-page__body`).

### 3.2 Overloaded visual effects

- **Фон страницы**: `.page-bg__image` с `--bg-image-shell` и фильтрами `--bg-image-filter`; `--overlay-page-glow`; сетка `.page-bg__noise` / `--overlay-grid`.
- **Glass / blur**: `--blur-glass`, `backdrop-filter` на `.section-nav`, `.topbar`, карточках, Lain-панели; многослойные `--glass-inner`, `--glass-specular`, `--glass-corner-light`.
- **Текст**: `--text-shadow-crisp` массово на `.lesson-card h2`, `.compact-details summary`, hero-элементах — усиливает «glow/cyber» и снижает спокойную иерархию.
- **Lain**: плавающая кнопка `.lain-helper__launcher` с тенями и «сигналом» `.lain-helper__signal` — узнаваемо, но в связке с общим шумом фона добавляет визуальную нагрузку.

### 3.3 Typography problems

- Моношрифт на `body` (см. выше).
- Мелкие размеры для вторичного текста: `--font-size-xs` / `--font-size-sm` в чипах, Lain quick actions, навигации.
- В `.markdown-body p, li` задан `line-height: var(--line-reading)` (1.68) — это хорошо для чтения, но **семейство шрифта** остаётся моноширинным.

### 3.4 Layout problems

- **Правая колонка** (`lesson-page__rail`, `lesson-side`): несколько `details` + `lesson-nav-panel` — логично по структуре, но визуально много «карточек» с тем же glass-языком, что и тело урока.
- **Task panel** под основным текстом (`lesson-page__task-stack`, `task-panel`): длинный урок → много скролла до задачи; якоря `#task`, `#stuck`, `#next-action` с `scroll-margin-top` помогают, но иерархия «чтение vs действие» всё равно конкурирует с декором.
- **Mobile** (`@media` для `.lesson-page__layout`, `720px` для Lain): в шаблоне явно отключаются отправки и часть действий (`mobile_view` в `lesson.html`, `dashboard.html`) — UX согласован, но Lain-панель на маленьком экране занимает значимую высоту (`max-height` / quick actions в колонку).

### 3.5 Components to preserve

- Навигация **breadcrumbs** (`lesson.html`, `course_map.html`, `recap.html`).
- **Статусы** (`meta-pill`, `status-chip`) — ясная семантика прогресса.
- **Lain** как паттерн: launcher + панель + quick actions + история (и привязка к `lesson_key`).
- **Терминал**: `terminal-panel`, presets, `data-terminal-*` — рабочий execution surface.
- **Карта курса** с модулями-details и checkpoint-панелью — хорошая структурная модель.

### 3.6 Components to redesign first

- Глобальные **page background** слои и интенсивность **hero** / `course-summary-strip` / `recap-summary-strip` (классы `bg-course`, `bg-dashboard`, `hero__visual`, `overlay-dark`).
- **Topbar** с мировыми часами (`topbar-clock`) — можно упростить или спрятать за прогрессивным disclosure.
- **Кнопки** `.btn`, `.btn--primary`, `.btn--ghost` — много слоёв теней/бликов; для focus-theme достаточно плоских состояний с чётким контрастом.
- **`.markdown-body`**: визуально отделить «зону чтения» (меньше декоративных теней, спокойный фон).

### Критические vs декоративные CSS-классы (кратко)

| Критичные для layout / поведения | Декоративные / легко переработать |
|----------------------------------|-----------------------------------|
| `page-shell`, `page-stack`, `lesson-page__layout`, `lesson-page__main`, `lesson-page__rail`, `workspace-shell`, `workspace-grid` | `--glass-*`, `--overlay-*`, `--hero-layer`, `text-shadow: var(--text-shadow-crisp)`, фоновые `--bg-image-*` |
| `data-ai-*`, `lain-helper*`, `data-terminal-*` | `topbar-clock`, усиленные тени карточек |
| `markdown-body` (семантика зоны контента) | глобальный `body` font-family как «тема» |

---

## 4. Lain Helper findings

### Current implementation

- **Backend**: `app/routers/ai_helper.py` — `AIHelperRequest` (`lesson_key`, `mode`, `message`, `submission_draft`), ответ с `assistant_message`, `interaction_id`.
- **Provider**: `app/services/lain_provider.py` — OpenAI **Responses** API, разбор `output_text` / `output`.
- **Service**: `app/services/ai_helper_service.py` — загрузка урока и `get_lesson_execution_context`, сборка контекста (`_build_context_text`: урок с клипом body до ~2600 символов, задача, submission/review, stuck), системный промпт с запретами, **scope refusal** по паттернам и эвристике якорей, сохранение каждого вызова в `LainHelperInteraction`.
- **Frontend**: `app/templates/base.html` — блок `.lain-helper` с `data-ai-endpoint`, `data-ai-history-endpoint`, `data-ai-lesson`; `app/static/js/app.js` — `setupAIHelper()` (история, quick actions, `free_question`, чтение черновика из `#content_text` / `#content_link`, stuck note для `stuck_help`).

### Quick actions (режимы)

Соответствие UI ↔ `LainHelperMode`: `explain_lesson`, `help_start`, `stuck_help`, `submission_hint`; свободный ввод — `free_question` через форму.

### Lesson context

Передаётся на сервере в промпт: заголовок, summary, objectives, checklist, укороченный markdown тела, поля задачи, состояние submission, последний review feedback, активный stuck.

### History

- БД: `LainHelperInteraction` (`app/models.py`).
- API: `GET /api/ai/helper/history?lesson_key=&limit=`; клиент кэширует загрузку по `lesson_key` (`loadedHistoryForLesson` в `app.js`).

### Guardrails

- Выключатель `ai_helper_enabled`, отсутствие ключа, `LainProviderError`.
- Явные запреты в system prompt; паттерны «сделай за меня» и т.д.; эвристика ухода темы от якорей урока/задачи.

### Strengths

- Lesson-scoped по дизайну; хорошо стыкуется с execution-first.
- История и режимы покрыты тестами (`tests/test_ai_helper.py`, `test_ai_helper_ui.py`).

### Risks при UI refactor

- Сломать **селекторы** в `app.js`: `#content_text`, `#content_link`, `#stuck_note` — для `submission_hint` и `stuck_help`.
- Переименовать/убрать `data-ai-*` или вложить root так, что `querySelector("[data-ai-helper]")` не найдёт узел.
- Скрыть панель иначе чем через `[hidden]` — проверить `setupAIHelper` (ожидает `panel.hidden`).
- Обломать **сессию** (401 на API) при смене layout auth — маловероятно, если middleware не трогать.

### Extension path к «workflow assistant курса»

- Сейчас контекст **жёстко lesson-bound**; универсальный ассистент по всему курсу потребует новых режимов, политики scope и, вероятно, отдельных endpoint или явного `course_slug` + guardrails против ухода в «сделай курс за меня».
- Минимальный безопасный шаг: расширить контекст **соседними уроками / module summary** из registry, не меняя базовый контракт POST (опциональные поля в JSON).

---

## 5. Content model findings

### Current schemas (файлы)

- **Course**: `CourseSchema` — `slug`, `title`, `description`, `version`, `duration_weeks` | `estimated_weeks`, `modules[]`, `prerequisites`.
- **Module**: `ModuleSchema` — `slug`, `title`, `description`, `block`, `objectives`, `lessons[]`, `checkpoint`.
- **Lesson** (front matter): `LessonFrontMatterSchema` — `key`, `title`, `summary`, `objectives`, `checklist`, `task_slug?`, `source_ids[]`.
- **Task**: `TaskSchema` — в т.ч. `terminal` (`TerminalConfigSchema`).
- **Checkpoint**: `CheckpointSchema` — в т.ч. `project_description`, `deliverables`, `evaluation_criteria`, `requirements`, `portfolio_expectations`, …
- **Source registry entry**: `SourceRegistryEntrySchema` — только `id`, `type`, `language`, `allowed_usage`.

### Validation model (`load_content_bundle`)

- Один глобальный порядок уроков; уникальность `lesson.key`, соответствие файлов `module.lessons`, ссылки на task/checkpoint/source id.
- Урок: минимум один `source_id` из registry; обязательные markdown-секции (Why / What to read / … / Technical English); проверка `## Action`.
- Orphan tasks / orphan checkpoints запрещены.
- Файл `content/blueprints/backend_developer_6_months.yml` должен существовать и иметь `blocks` (структурная проверка без полной схемы blueprint).

### Source registry state

- `content/sources/source_registry.yml` — **список slug-id записей без URL и без секций**; валидация урока проверяет только наличие id в этом списке.

### Runtime vs schema gaps

- **`LessonContent`** (`app/content_loader.py`): в runtime **нет** `source_ids` — они только в pipeline/файлах; Lain контекст берётся из тела урока и задачи, не из registry напрямую.
- **`CheckpointContent`**: в runtime объекте **отсутствуют** `project_description`, `deliverables`, `evaluation_criteria` (есть в YAML и `CheckpointSchema`, шаблон `course_map.html` для части полей использует только то, что есть в dataclass — фактически `requirements`, `portfolio_expectations`, `title`, `summary`, `description`, …). Итог: **расширенные поля checkpoint в UI не полностью проводятся из схемы в объект** (стоит явно сверить при следующем изменении шаблонов).

### Связь 3-week course и 6-month blueprint

- Активный курс: `content/courses/python-backend-ai-foundation/course.yml` — **3 модуля**, `estimated_weeks: 3`.
- Blueprint: `content/blueprints/backend_developer_6_months.yml` — блоки 0–6 с **другими** модулями начиная с block 1 (`block-1-python-core`, …).
- Валидатор требует наличия blueprint-файла, но **не сверяет** slug модулей активного курса с blueprint (только structural presence). Расхождение — **продуктовое/авторское**, не автоматически блокируемое.

---

## 6. Course structure findings

### Активный курс `python-backend-ai-foundation`

| Module slug | Block (module.yml) | Lessons | Checkpoint | Примечание |
|-------------|-------------------|---------|------------|------------|
| `block-0-onboarding-workspace` | 0 | `block-0-workspace-baseline`, `block-0-python-cli-smoke`, `block-0-git-github-cycle` | `block-0-workspace-checkpoint` | Согласуется с blueprint block 0 первым модулем по смыслу и slug. |
| `block-0-learning-loop` | 0 | `block-0-learning-loop-setup`, `block-0-study-log-baseline` | `block-0-learning-checkpoint` | Согласуется со вторым модулем blueprint block 0. |
| `foundation-real` | **1** | `foundation-real-workspace`, `foundation-real-cli-python`, `foundation-real-git-loop` | `foundation-real-start-pack` | Контент пересекается с block 0; `block: 1` не совпадает с blueprint block 1 (`block-1-python-core` и др.). Два урока **без `task_slug`** в front matter (только `foundation-real-cli-python` с задачей). |

**Tasks в репозитории (6 файлов):**  
`foundation-workspace-ready`, `block-0-python-cli-smoke`, `foundation-git-github-cycle`, `onboarding-learning-loop-ready`, `onboarding-study-log-baseline`, `foundation-python-cli-smoke`.

**Blueprint block 0 ожидал для onboarding:** в т.ч. `foundation-python-cli-smoke` в `expected_tasks` первого модуля; фактически урок `block-0-python-cli-smoke` ссылается на task **`block-0-python-cli-smoke`** — отдельный task-файл, не тот slug, что в blueprint.

**Второй курс в индексе:** `course-factory-reference` — reference fixtures для authoring (`course.yml` явно говорит, что не активный runtime-трек); в `dashboard` зашит только `python-backend-ai-foundation`.

### keep

- Модули **`block-0-onboarding-workspace`**, **`block-0-learning-loop`** как основа **Block 0** (slug и структура близки blueprint).
- Набор **валидаторов** и обязательных секций урока.
- **Checkpoint** `block-0-workspace-checkpoint`, `block-0-learning-checkpoint` как артефактные ворота block 0.
- Уроки и задачи, уже согласованные с blueprint по смыслу: `foundation-workspace-ready`, `foundation-git-github-cycle`, `onboarding-learning-loop-ready`, `onboarding-study-log-baseline`.

### rewrite

- Контент/структура модуля **`foundation-real`** относительно канонического маршрута (слияние с block 0, или перенос в block 1 по blueprint с новыми уроками/задачами).
- Согласование **task slug** для CLI onboarding с blueprint (`block-0-python-cli-smoke` vs ожидаемый `foundation-python-cli-smoke`) — продуктовое решение + правки YAML.
- Уроки **`foundation-real-workspace`**, **`foundation-real-git-loop`**: явно задать `task_slug` или осознанно оставить «без задачи» (сейчас выполнение/recap может быть асимметричным).

### archive

- **`course-factory-reference`** — не «архив» в смысле удаления, а **изолированный эталон** для фабрики контента; держать отдельно от learner path.
- **`foundation-real`** (как целостный модуль) — кандидат в **архив эталона** «как оформлять foundation real pass», если основной маршрут схлопнут в block 0.

### delete_candidate

- **Нет обязательных delete-кандидатов** по коду: всё участвует в валидном графе. Условные кандидаты после редакции структуры: дублирующий модуль **`foundation-real`** или отдельный task **`block-0-python-cli-smoke`**, если решите унифицировать на один CLI task slug (только после контент-решения; **в аудите не удаляем**).

---

## 7. Source-backed pipeline findings

### What exists

- **`source_registry.yml`** с id и политикой usage.
- **Урок**: список `source_ids` + обязательные секции «What to read (EN source)» и т.д.
- **Валидация**: каждый `source_id` должен существовать в registry.
- **Blueprint**: текстовые `required_source_ids` на уровне модулей в YAML (не исполняется runtime).

### What is missing

- **URL**, version/pin, конкретные **section anchors** в registry.
- **Fetch/cache layer**, HTTP/MCP клиент, артефакты «что было скачано и когда».
- **Prompt templates / content builder** как отдельный конвейер генерации draft уроков.
- **Скрипты** «собрать урок из источника» (кроме общих scaffold — они создают каркас, не тянут web).
- **Валидация «ответа агента против source id»** — только статическая привязка id.

### Recommended minimal design (direct web/MCP → воспроизводимость)

1. **Расширить `source_registry.yml`** (или параллельный `sources/*.yml`): `canonical_url`, `retrieval_profile` (web vs mcp vs manual), опционально `preferred_sections[]`, `license_notes`.
2. **`source_fetcher`**: абстракция «получить текст по (source_id, section_query)» с таймаутом и явным user-agent/policy.
3. **`source_cache`**: на диске под `content/` или отдельный `var/` — сырой текст + hash + timestamp + `retrieval_log` (URL, HTTP статус, выбранные фрагменты).
4. **`content_builder`**: шаблоны промптов (вне prod runtime или отдельная CLI команда) → draft `.md` / `.yml`.
5. **`validate_content`** — как сейчас; опционально проверка «указанные section id существуют в cache manifest».
6. **Human review** — PR в git; **publish** — уже существующий merge в `content/`.

**Метаданные для воспроизводимости:** `fetch_run_id`, дата, точные URL, версия страницы (если доступна), hash тела, краткий `retrieval_notes` (что именно взяли).

---

## 8. Test and quality gate findings

### Current tests (что держит core behavior)

- **Контент-граф**: `tests/test_content_validation.py`, `test_content_integrity.py` — орфаны, дубликаты, ссылки task/source, snapshot «текущий контент валиден».
- **Приложение**: `tests/test_app_smoke.py` — auth, dashboard, lessons, terminal, stuck, checkpoint, markdown render.
- **Lain**: `tests/test_ai_helper.py` (логика, guardrails, история), `tests/test_ai_helper_ui.py` (наличие блока Lain на страницах с консистентным `lesson_key`).
- **Scaffold**: `test_content_scaffold.py`.

### CI (`.github/workflows/ci.yml`)

- `ruff check .`
- `python scripts/check_text_integrity.py`
- `python scripts/validate_content.py`
- `python -m pytest`
- Отдельно: docker build + compose smoke (с `PERSONAL_LMS_AI_HELPER_ENABLED=false`).

### Commands checked (фактический прогон аудита)

Окружение: репозиторий с активированным `.venv`, зависимости `pip install -e .`.

| Команда | Результат |
|---------|-----------|
| `python scripts/validate_content.py` | **OK** — Courses: 2, Modules: 4, Lessons: 11, Tasks: 6, Checkpoints: 4; ошибок нет. |
| `python -m pytest` | **62 passed** (~48s). |
| `python -m ruff check .` | В **чистом** `.venv` пакет **ruff не установлен** (`No module named ruff`). После **`pip install ruff`** в том же venv: **All checks passed!** В `pyproject.toml` ruff не объявлен как dependency — как в CI, его нужно ставить отдельно. |

### Рекомендуемые тесты перед UI refactor

- Снимок **критичных селекторов**: тест, что `lesson.html` содержит `id="content_text"` / `id="content_link"` / `id="stuck_note"` при соответствующих условиях (или обновить контракт осознанно).
- Лёгкий **visual regression** опционально вне MVP; минимум — сохранить `test_ai_helper_ui` и расширить при смене классов Lain.
- **A11y smoke** (контраст, focus) — по желанию, не в коде сейчас.

### Перед content reload

- Уже есть `test_current_content_snapshot_is_valid`; добавить тесты на **согласованность с blueprint** (если появится машинная матрица соответствия).
- Проверка **orphan / duplicate** остаётся обязательной.

### Как убедиться, что Lain не сломалась

- `python -m pytest tests/test_ai_helper.py tests/test_ai_helper_ui.py`
- Ручной smoke: открыть урок, quick action, история, свободный вопрос (при включённом helper и ключе).

### Как убедиться, что content graph цел

- `python scripts/validate_content.py`
- `python -m pytest tests/test_content_validation.py tests/test_content_integrity.py`

---

## 9. Recommended staged plan

### 1. Audit stabilization

- **Goal**: зафиксировать продуктовые решения по `foundation-real` vs block 0 и по task slug CLI; завести задачи на расширение registry metadata.
- **Files likely affected**: только docs / задачи трекера; код опционально — не в этом этапе.
- **Risk**: низкий.
- **Validation**: `python scripts/validate_content.py`, `python -m pytest`.

### 2. UI Focus Theme

- **Goal**: читабельность урока, снижение шума фона, иерархия; сохранить Lain/terminal UX-паттерны.
- **Files likely affected**: `app/static/css/app.css`, возможно минимально `app/templates/*.html` (классы обёрток).
- **Risk**: средний (регресс селекторов Lain).
- **Validation**: `python -m pytest`, ручной проход lesson/dashboard; `tests/test_ai_helper_ui.py`.

### 3. Course structure cleanup

- **Goal**: один канонический маршрут block 0 + решение по `foundation-real`; синхронизация с blueprint на уровне slug/task.
- **Files likely affected**: `content/courses/...`, `content/tasks/`, возможно `content/checkpoints/`.
- **Risk**: высокий для прогресса пользователей (ключи уроков).
- **Validation**: `python scripts/validate_content.py`, полный `pytest`, ручная проверка прогресса на тестовой БД.

### 4. Source-backed builder

- **Goal**: metadata + cache + fetcher CLI; без изменения prod LMS runtime при необходимости.
- **Files likely affected**: новые scripts / `content/sources/*`, возможно `docs/product/*` (по отдельной задаче на доки).
- **Risk**: средний (объём данных, лицензии).
- **Validation**: unit tests на fetch/cache; `validate_content` на существующем дереве.

### 5. Lain workflow formalization

- **Goal**: явные режимы для «следующий урок / карта модуля» при сохранении lesson-bound guardrails; опционально расширенный контекст из registry cache.
- **Files likely affected**: `app/services/ai_helper_service.py`, `ai_helper_modes.py`, `routers/ai_helper.py`, `app.js`.
- **Risk**: средний (промпты, стоимость токенов).
- **Validation**: `tests/test_ai_helper.py`, ручной smoke.

### 6. Course V2 reload

- **Goal**: новый контент по согласованному blueprint с воспроизводимыми source traces.
- **Files likely affected**: преимущественно `content/`.
- **Risk**: высокий.
- **Validation**: полный CI pipeline + выборочный UAT.

---

## 10. Do-not-touch list for first refactor

Без отдельной задачи и осознанного контракта не менять:

- `app/routers/ai_helper.py` (формы JSON), `app/services/lain_provider.py`, `app/services/ai_helper_service.py` (кроме согласованных правок промптов).
- `app/static/js/app.js` — блок `setupAIHelper` и селекторы к полям форм.
- `app/templates/base.html` — атрибуты `data-ai-*` и структура корня `.lain-helper`.
- `app/routers/terminal.py`, ядро `terminal_service` (sandbox, whitelist).
- `app/content_pipeline.py` — правила графа.
- SQLModel-таблицы в `app/models.py` и миграционная политика.
- Публичные пути SSR перечисленных роутов.

---

## 11. Open questions

1. **Продуктовый приоритет**: оставляем ли `foundation-real` в активном маршруте как «второй проход» или схлопываем в block 0-only (и как мигрировать прогресс пользователей с `lesson_key`)?
2. **Канонический task slug для CLI onboarding**: blueprint-имя `foundation-python-cli-smoke` или текущий `block-0-python-cli-smoke`?
3. **Нужны ли в UI поля checkpoint** `project_description` / `deliverables` / `evaluation_criteria` — и тогда расширять `CheckpointContent` или упрощать YAML?
4. **Должен ли валидатор** в будущем **жёстко сверять** `course.modules` с blueprint block N (и как трактовать `estimated_weeks` vs 6 месяцев)?
5. **Политика внешнего fetch**: допустимые источники только из `SOURCE_STACK.md` / registry — кто утверждает pin URL и хранение кэша (git vs локальный `var/`)?

---

## Validation log (аудит)

Команды из корня репозитория после `pip install -e .` в `.venv`:

```text
python scripts/validate_content.py
→ OK (0 errors). Stats: 2 courses, 4 modules, 11 lessons, 6 tasks, 4 checkpoints.

python -m pytest
→ 62 passed in ~48s.

python -m ruff check .
→ В базовом editable install ruff отсутствует; после pip install ruff: All checks passed!
```

Примечание: в `pyproject.toml` **ruff не указан** в `dependencies`; локально его нужно устанавливать отдельно (как в CI).
