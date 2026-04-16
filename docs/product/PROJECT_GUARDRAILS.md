# Project Guardrails

## Назначение документа

Документ фиксирует ограничения проекта. Его задача — защищать `personal-lms` от scope creep, platform-building hell и решений, которые не усиливают обучение.

## Главный guardrail

Проект должен оставаться personal research-driven LMS для Python backend + AI in real products.

Новая идея допустима только если она усиливает:

- маршрут;
- execution;
- progress;
- tasks;
- submissions;
- review;
- stuck flow;
- weekly recap;
- выпуск маленьких рабочих артефактов.

## Что проект не должен делать

Проект не должен становиться:

- generic LMS;
- enterprise LMS;
- marketplace курсов;
- social platform;
- browser IDE;
- AI autopilot без фиксированного курса;
- multi-tenant SaaS;
- системой управления учебным заведением.

## Что нельзя quietly протаскивать

Нельзя без отдельного решения добавлять:

- сложную multi-user architecture;
- роли и permissions сверх MVP;
- React/Next.js frontend split;
- desktop app;
- mobile app;
- PostgreSQL / Supabase как обязательную MVP-базу;
- внешнюю managed-инфраструктуру как условие запуска;
- социальные функции;
- публичный профиль/лидерборды;
- AI-функции, которые заменяют маршрут вместо поддержки обучения.

## Признаки platform-building hell

Проект уходит в platform-building hell, если:

- больше времени уходит на framework/platform abstractions, чем на learning flow;
- появляются сущности, не связанные с обучением;
- MVP требует сложного деплоя;
- auth/model complexity растет быстрее, чем курс;
- roadmap наполняется enterprise-функциями;
- пользовательские сценарии становятся вторичными;
- простые задачи требуют архитектурных церемоний.

## Проверка новой идеи

Перед добавлением идеи нужно ответить:

1. Какой учебный friction она снижает?
2. Какой next step она делает понятнее?
3. Какой execution она усиливает?
4. Как она влияет на progress/review/stuck flow?
5. Можно ли сделать это проще?
6. Нужно ли это именно в MVP?
7. Не превращает ли это проект в generic LMS или platform-building?

Если ответы неубедительны, идею нужно отложить.

## Контентные guardrails

Контентная стратегия должна оставаться source-backed.

Нельзя:

- писать полный курс с нуля без отдельного решения;
- превращать платформу в список ссылок;
- добавлять источники без curation;
- добавлять темы, которые не ведут к Python backend + AI product skills;
- раздувать уроки без практического результата.

## UX guardrails

UI должен оставаться функциональным и читаемым.

Нельзя:

- жертвовать readability ради mood;
- перегружать markdown body декоративными слоями;
- превращать Lain в центральный баннер;
- делать generic neutral LMS без характера;
- делать визуальные эффекты, которые мешают next step.

## AI guardrails

AI может помогать обучению, но не должен размывать маршрут.

Допустимо:

- review support;
- stuck flow support;
- объяснения по текущему lesson context;
- recap support.

Недопустимо:

- бесконтрольный autopilot;
- генерация случайного курса вместо curated path;
- замена execution на “AI сделал за пользователя”;
- скрытое расширение scope под видом AI layer.

## Не зафиксировано

- Полная политика безопасности terminal-like execution surface.
- Детальный governance для будущих AI-assisted функций.
- Финальный формат review pipeline.
