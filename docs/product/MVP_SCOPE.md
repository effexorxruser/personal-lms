# MVP Scope

## Назначение документа

Документ фиксирует границы MVP и явно разделяет:

- что уже реализовано в репозитории;
- что остается целевым направлением, но еще не сделано.

Актуализация: 18 апреля 2026.

## Принцип MVP

MVP должен быть small and sharp.

Цель: доказать, что personal source-backed LMS помогает регулярно выполнять практические шаги в направлении Python backend + AI, а не просто потреблять контент.

## Формат продукта

- web-first приложение;
- локальный запуск как основной режим MVP;
- UI и пользовательский слой — на русском;
- без mobile/desktop app как отдельного продукта.

## Зафиксированный стек MVP

- FastAPI
- Jinja2
- SQLite
- SQLModel
- Vanilla CSS + Vanilla JS

`alembic` присутствует как зависимость, но migration scaffold пока не создан.

## Что уже входит в MVP (и реализовано)

- login/logout и сессионная авторизация;
- dashboard;
- карта курса;
- страница урока;
- progress по урокам/курсу;
- task layer;
- submissions + review state;
- checkpoint submissions + checkpoint review state;
- stuck flow;
- weekly recap;
- lesson-scoped terminal execution surface;
- lesson-scoped AI helper (Lain v0);
- file-based authoring model: курс/модуль/урок/task/checkpoint.

## Что в MVP пока не реализовано

- production-ready migration workflow (Alembic scaffold);
- multi-course масштабирование beyond текущего content snapshot.

Эти пункты не должны реализовываться ad-hoc: только через отдельные решения с проверкой scope.

## Минимальный встроенный терминал

Терминал в MVP — это учебный execution layer, а не полноценный shell.

Границы текущей реализации:

- lesson-scoped sandbox;
- whitelist команд на уровне task;
- grammar ограничена поддерживаемыми командами;
- возможен режим только preset-команд (без manual input);
- timeout и ограничение вывода;
- history сохраняется в `TerminalRun`.

## Что не входит в MVP

- multi-tenant architecture;
- сложная multi-user/social модель;
- публичный marketplace курсов;
- browser IDE и замена VS Code;
- split frontend/backend архитектура;
- сложная role-based enterprise модель;
- AI autopilot, который ломает фиксированную структуру курса.

## Anti-scope правила

Идея не должна попадать в MVP, если она:

- не усиливает execution и следующую учебную итерацию;
- требует существенной platform complexity;
- превращает проект в generic LMS;
- размывает фиксированный маршрут;
- требует архитектурного разворота без прямой пользы для learner workflow.

## Что может быть позже

- Alembic migrations как обязательный путь schema changes;
- AI layer для lesson/runtime assist;
- дополнительные курсы и треки;
- production-like deployment profile.
