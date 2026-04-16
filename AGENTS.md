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

## Codex environment policy

### Разрешённые интеграции

- GitHub plugin
- OpenAI Developer Docs MCP

### Правила использования MCP

- Использовать Docs MCP только когда задача связана с:
  - OpenAI / Codex integration
  - MCP / config / plugin behavior
  - будущим AI layer проекта
- Не использовать MCP для расползания scope.
- Не добавлять новые плагины или MCP без явного запроса.

## Codex environment policy

### Разрешённые интеграции

- GitHub plugin
- OpenAI Developer Docs MCP

### Правила использования MCP

- Использовать Docs MCP только когда задача связана с:
  - OpenAI / Codex integration
  - MCP / config / plugin behavior
  - будущим AI layer проекта
- Не использовать MCP для расползания scope.
- Не добавлять новые плагины или MCP без явного запроса.

### Правила выполнения задач

- Предпочитать локальную логику репозитория внешним источникам.
- Не менять архитектуру без явного указания.
- Не добавлять новые зависимости без необходимости.
