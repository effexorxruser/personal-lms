# MVP Scope

## Назначение документа

Документ фиксирует границы MVP: что входит, что не входит, какой стек используется и какие anti-scope правила защищают проект от расползания.

## Принцип MVP

MVP должен быть small and sharp. Его задача — доказать, что personal source-backed LMS может вести пользователя по маршруту Python backend + AI in real products лучше, чем хаотичный серфинг по интернету.

MVP не должен становиться giant LMS, платформой для всех пользователей или enterprise-системой.

## Формат продукта

MVP — web-first приложение.

Основной режим использования:

- браузер;
- локальный запуск на старте;
- пользовательский и информационный слой на русском языке.

Mobile-first, desktop-first и browser IDE не являются целями MVP.

## Зафиксированный стек MVP

- FastAPI;
- Jinja2;
- SQLite;
- Tailwind CSS;
- Alpine.js.

SQLite является базой MVP. PostgreSQL / Supabase могут быть рассмотрены позже, но не являются стартовой базой.

## Что входит в MVP

Минимально нужные продуктовые части:

- вход в приложение;
- dashboard с текущим состоянием обучения;
- карта курса;
- страница урока;
- progress по урокам/курсу;
- task layer;
- submissions;
- review;
- stuck flow;
- weekly recap;
- минимальный встроенный терминал / terminal-like execution surface;
- lesson-scoped AI helper;
- authoring-ready структура curriculum сущностей.

Минимально нужные сущности:

- пользователь;
- курс;
- модуль;
- урок;
- статус урока;
- задача;
- submission;
- review result;
- progress state.

Точные поля сущностей могут уточняться по мере реализации.

## Authoring/runtime readiness до массового curriculum onboarding

До массовой загрузки реального курса MVP должен достигнуть authoring/runtime readiness.

Минимально обязательные закрытия до real curriculum onboarding:

- stuck flow;
- weekly recap;
- minimal terminal-like execution surface;
- lesson-scoped AI helper;
- authoring-ready curriculum structure.

Эти пункты не расширяют MVP в сторону giant LMS, а фиксируют минимальную устойчивость выполнения и загрузки контента.

## Что не входит в MVP

В MVP не входят:

- multi-tenant architecture;
- сложная multi-user модель;
- социальные функции;
- публичный marketplace курсов;
- полноценная IDE в браузере;
- замена VS Code;
- mobile app;
- desktop app;
- сложная role-based access model;
- enterprise-функции;
- AI autopilot, который меняет фиксированную структуру курса;
- сложная VPS/multi-service инфраструктура как обязательное условие запуска.

## Минимальный встроенный терминал

В MVP согласован минимальный встроенный терминал / terminal-like execution surface.

Это не полноценная IDE и не универсальный remote shell. Его роль:

- дать учебный execution layer;
- поддержать terminal literacy;
- связать задание с выполнением;
- усилить ощущение dev environment.

Границы безопасности и точная реализация могут быть уточнены позже.

## Anti-scope правила

Новая идея не должна попадать в MVP, если она:

- не помогает пользователю сделать следующий учебный шаг;
- не усиливает execution;
- требует сложной платформенной инфраструктуры;
- добавляет социальную/enterprise сложность;
- превращает проект в generic LMS;
- размывает фиксированный маршрут;
- требует переписывания архитектуры без прямой пользы для обучения.

## Что может быть позже

Позже могут быть рассмотрены:

- PostgreSQL / Supabase;
- деплой за пределами локального режима;
- расширенные review сценарии;
- дополнительные курсы и треки;
- более глубокие AI-assisted функции.

Это не часть жесткого MVP, пока не зафиксировано отдельным решением.
