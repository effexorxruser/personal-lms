# AGENTS.md

## Цель проекта

Self-hosted LMS-like платформа для обучения Python backend + AI.

## Архитектура (target vs legacy)

**Target architecture** — Next.js 15 full-stack (App Router, Server Components, Server Actions). Frontend и backend живут в Next.js app, если задача явно не указывает иное.

**Legacy / previous architecture** — FastAPI + Jinja2 + SQLite + SQLModel в текущем `app/` (Python). Это reference и runtime до cutover; **не удалять** старый код до явного cutover и переноса в `legacy/fastapi-app/`.

Любые изменения под target stack должны соответствовать `docs/architecture/` (master: [NEXT_FULLSTACK_ADAPTATION.md](docs/architecture/NEXT_FULLSTACK_ADAPTATION.md)).

## Режим работы

- Работаем маленькими проверяемыми шагами.
- Не расширять scope без явного запроса.
- Предпочитать простые и явные решения.
- Target: контент и структура курса — в PostgreSQL (Course Builder); `content/` — archive/reference до и после cutover.
- Legacy: контент в файлах (`content/`) — только для previous runtime и import/reference.
- Runtime state (progress, submissions, enrollments) — в БД; AI **не** пишет в progress state напрямую.
- UI и пользовательский слой — на русском.
- README в MVP — на русском.
- Исключения: env vars, file names, команды, технические идентификаторы.

## Стек (target)

- Next.js 15 (App Router, RSC, Server Actions, Route Handlers)
- TypeScript
- Tailwind CSS, shadcn/ui
- PostgreSQL + Prisma (+ Prisma Migrate)
- Better-Auth (self-signup выключен; пользователей создаёт admin)
- Redis — sessions/rate limits/jobs (по [DEPLOYMENT_MODEL.md](docs/architecture/DEPLOYMENT_MODEL.md))
- Docker Compose deploy (primary)
- `worker/` — code runner и async jobs **вне** Next.js process
- AI: `AI_MODE` (`disabled` | `external` | `api`); см. [AI_LAYER.md](docs/architecture/AI_LAYER.md)

## Стек (legacy — не расширять)

- FastAPI, Jinja2, SQLite, SQLModel, Alembic, Alpine.js
- In-process lesson sandbox — только в legacy; в target не переносить as-is

## Ограничения

- No browser IDE
- No multi-tenant / marketplace / SaaS
- No Stripe, billing, subscriptions, commercial checkout
- No public self-signup (до отдельного продуктового решения)
- No untrusted code execution в Next.js / web process
- No runner внутри Next.js process — только `worker/` или MVP-safe tasks (quiz, text, manual review)
- Не удалять legacy FastAPI без cutover-плана из [NEXT_FULLSTACK_ADAPTATION.md](docs/architecture/NEXT_FULLSTACK_ADAPTATION.md)

## Workflow

Primary workflow:

1. ChatGPT Project chat:
   - формулировка идей, задач и требований;
   - review репозитория;
   - UI/product review;
   - сбор и анализ источников;
   - подготовка задачи на исполнение.

2. Cursor Agent for Windows / Cursor Web Agent:
   - основной агент исполнения;
   - выполняет сформулированные задачи;
   - работает малыми проверяемыми изменениями;
   - возвращает summary, changed files, validation.

3. ChatGPT Project chat:
   - review результата;
   - анализ diff/summary;
   - уточнение следующей итерации.

4. User:
   - финальный approve.

Codex IDE / Codex Web remains optional secondary executor for isolated tasks or alternative implementation passes.

## Agent execution policy

### Разрешённые интеграции

- GitHub plugin
- OpenAI Developer Docs MCP
- context7

### Правила использования MCP

- Использовать OpenAI Developer Docs MCP только когда задача связана с:
  - OpenAI / AI-agent integration
  - MCP / config / plugin behavior
  - AI layer проекта ([AI_LAYER.md](docs/architecture/AI_LAYER.md))

- Использовать `context7` только когда задача связана с:
  - source-backed curriculum authoring
  - выбором конкретных официальных sections/pages внутри уже утверждённых источников
  - загрузкой реального контента на основе `docs/product/SOURCE_STACK.md`
  - проверкой актуальных официальных developer/docs sources для foundation/backend/reliability/AI blocks

- Не использовать `context7` для свободного расширения source stack.
- Не использовать внешние источники как backbone, если они не согласуются с `docs/product/SOURCE_STACK.md`.
- Любой supplement source добавлять только при явной необходимости и с обоснованием в итоговом отчёте.
- Не использовать MCP для расползания scope.
- Не добавлять новые плагины или MCP без явного запроса.

### Правила выполнения задач

- Предпочитать локальную логику репозитория внешним источникам.
- Для implementation под target stack — `docs/architecture/` как source of truth для стека, auth, БД, AI, deploy.
- Для curriculum/content задач использовать локальные документы проекта:
  - `docs/product/PRODUCT_VISION.md`
  - `docs/product/MVP_SCOPE.md` (previous MVP; границы cutover — [MVP_ROADMAP.md](docs/architecture/MVP_ROADMAP.md))
  - `docs/product/LEARNING_MODEL.md`
  - `docs/product/CONTENT_STRATEGY.md`
  - `docs/product/SOURCE_STACK.md`
  - `docs/product/AUTHORING_MODEL.md`
- Для source-backed curriculum задач:
  - сначала читать локальные product docs;
  - затем через `context7` находить конкретные официальные sections/pages внутри допустимых источников;
  - затем контент в target — через Course Builder / import; legacy — в `content/` только по явной задаче.
- Не менять target-архитектуру без явного указания.
- Не добавлять новые зависимости без необходимости.
- Не реализовывать фичи из excluded commercial LMS (payments, marketplace) «на будущее».

### Ограничения изменений

- Не добавлять `.cursor/rules`.
- Не менять `CONTRIBUTING.md`.
- Не менять `README.md`.
- Не удалять legacy runtime до cutover без задачи на cutover.
- Не переписывать весь файл без необходимости.
- Не менять продуктовые guardrails без явного запроса ([PROJECT_GUARDRAILS.md](docs/product/PROJECT_GUARDRAILS.md)).
