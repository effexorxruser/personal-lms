# AGENTS.md

## Цель проекта

Self-hosted LMS-like платформа для обучения Python backend + AI.

## Режим работы

- Работаем маленькими проверяемыми шагами.
- Не расширять scope без явного запроса.
- Предпочитать простые и явные решения.
- Контент хранить в файлах.
- Runtime state хранить в БД.
- UI и пользовательский слой — на русском.
- README в MVP — на русском.
- Исключения: env vars, file names, команды, технические идентификаторы.

## Стек

- FastAPI
- Jinja2
- SQLite
- SQLModel
- Alembic
- Alpine.js
- Tailwind позже
- Linux-only trusted runner for MVP

## Ограничения

- No React/Next.js
- No split frontend/backend
- No browser IDE
- No multi-tenant architecture

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
  - будущим AI layer проекта

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
- Для curriculum/content задач использовать локальные документы проекта как primary source of truth:
  - `docs/product/PRODUCT_VISION.md`
  - `docs/product/MVP_SCOPE.md`
  - `docs/product/LEARNING_MODEL.md`
  - `docs/product/CONTENT_STRATEGY.md`
  - `docs/product/SOURCE_STACK.md`
  - `docs/product/AUTHORING_MODEL.md`
- Для source-backed curriculum задач:
  - сначала читать локальные product docs;
  - затем через `context7` находить конкретные официальные sections/pages внутри допустимых источников;
  - после этого собирать lessons/tasks/checkpoints в `content/`.
- Не менять архитектуру без явного указания.
- Не добавлять новые зависимости без необходимости.

### Ограничения изменений

- Не добавлять `.cursor/rules`.
- Не менять `CONTRIBUTING.md`.
- Не менять `README.md`.
- Не удалять существующие стековые решения.
- Не переписывать весь файл без необходимости.
- Не менять продуктовые guardrails.
