# Project Guardrails

## Назначение документа

Документ фиксирует ограничения проекта. Его задача — защищать `personal-lms` от scope creep, platform-building hell и решений, которые не усиливают обучение.

Целевая full-stack архитектура: [docs/architecture/NEXT_FULLSTACK_ADAPTATION.md](../architecture/NEXT_FULLSTACK_ADAPTATION.md). Roadmap: [MVP_ROADMAP.md](../architecture/MVP_ROADMAP.md). Previous runtime (FastAPI): [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md).

## Главный guardrail

Проект должен оставаться personal research-driven LMS для Python backend + AI in real products — **private learning platform для маленькой группы**, не commercial SaaS.

Новая идея допустима только если она усиливает:

- маршрут;
- execution;
- progress;
- tasks;
- submissions;
- review;
- stuck flow;
- weekly recap;
- выпуск маленьких рабочих артефактов;
- создание/редактирование курсов через сайт (Course Builder);
- ориентацию в курсе через knowledge graph (**дополнение**, не замена reader).

## Архитектурный pivot (зафиксировано)

| Решение | Статус |
|---------|--------|
| Next.js 15 full-stack (UI + API в одном app) | Target |
| PostgreSQL + Prisma | Target persistence / SoT |
| Better-Auth, роли `admin` / `author` / `learner` | Target |
| FastAPI + SQLite в `legacy/fastapi-app/` | Legacy; не удалять без плана |
| File-based `content/` как runtime SoT | Legacy; archive/reference + import |
| Course Knowledge Graph | Архитектура: [COURSE_KNOWLEDGE_GRAPH.md](../architecture/COURSE_KNOWLEDGE_GRAPH.md); **implementation Phase 2b** |
| React Flow (`@xyflow/react`) | **Только Phase 2b+**; не в Phase 1/2 |
| Obsidian / Obsidian plugins | **Не использовать** как runtime |
| Sigma.js (large graph) | Future; не в MVP |
| Stripe / payments / marketplace | **Вне scope** |
| Public self-signup | **Выключен** до отдельного решения |
| AI управляет прогрессом / pass-fail | **Запрещено** |
| Untrusted code в web/Next process | **Запрещено** |
| Code runner в Next.js process | **Запрещено**; только `worker/` или MVP-safe tasks |

Детали: [AUTH_AND_ROLES.md](../architecture/AUTH_AND_ROLES.md), [AI_LAYER.md](../architecture/AI_LAYER.md), [DEPLOYMENT_MODEL.md](../architecture/DEPLOYMENT_MODEL.md), [DATABASE_MODEL.md](../architecture/DATABASE_MODEL.md).

## Фазы MVP (кратко)

| Phase | Фокус | Не тащить раньше времени |
|-------|--------|---------------------------|
| 1 | Next, Prisma, Auth, layouts | graph UI, `@xyflow/react` |
| 2 | Catalog, lesson reader, progress | graph page, concept editor |
| **2b** | Learner graph (read-only), `Concept`/`ContentRelation` | admin graph editor, Sigma.js |
| 3 | Course Builder + admin graph editor | — |

Phase 1 и 2 **не требуют** graph-зависимостей и не конфликтуют с target Next.js stack.

## Что проект не должен делать

Проект не должен становиться:

- generic LMS;
- enterprise LMS;
- marketplace курсов;
- billing / subscription product;
- social platform;
- browser IDE;
- Obsidian-клон с плагинами;
- AI autopilot без фиксированного курса;
- multi-tenant SaaS;
- системой управления учебным заведением.

## Что нельзя quietly протаскивать

Нельзя без отдельного решения добавлять:

- enterprise RBAC и org-hierarchy;
- public signup и open registration;
- Stripe, checkout, subscriptions, sales analytics;
- marketplace, course sales, creator payouts;
- Obsidian, obsidian-export, embedded Obsidian iframe;
- `@xyflow/react`, `sigma`, graph layout libs — **до Phase 2b**;
- Course Knowledge Graph как **единственный** способ навигации по курсу;
- desktop app;
- mobile app;
- managed cloud как **единственный** путь деплоя (self-hosted Compose — primary);
- социальные функции, лидерборды, публичные профили;
- AI-функции, которые открывают уроки, меняют completion или pass/fail;
- произвольный code execution в Next.js или без sandbox worker;
- удаление legacy FastAPI runtime «заодно» с unrelated задачей.

Допустимо в target (не противоречит guardrails):

- Next.js monolith (не «split frontend/backend» в смысле отдельного SPA-репозитория);
- PostgreSQL для маленькой группы пользователей;
- admin-created users и enrollment вместо оплаты;
- import/export курсов (JSON/ZIP) как переносимый формат, не runtime SoT;
- read-only course graph для learner (после Phase 2b).

## Course Knowledge Graph guardrails

По [COURSE_KNOWLEDGE_GRAPH.md](../architecture/COURSE_KNOWLEDGE_GRAPH.md):

**Допустимо (Phase 2b+):**

- `Concept`, `ContentRelation` в Prisma;
- `/courses/[courseId]/graph` read-only для learner;
- local subgraph на странице урока (depth 1/2/3);
- structural `contains` edges из иерархии курса;
- клик по узлу → lesson / task / concept / resource.

**Недопустимо:**

- Obsidian как dependency или runtime;
- граф вместо catalog + lesson reader + progress;
- learner редактирует связи (только author/admin, Phase 3+);
- `unlocks`/`blocks` в графе автоматически меняют `LessonProgress` без отдельного решения;
- добавление `@xyflow/react` вне задачи Phase 2b.

## Признаки platform-building hell

Проект уходит в platform-building hell, если:

- больше времени уходит на framework/platform abstractions, чем на learning flow;
- появляются сущности, не связанные с обучением;
- MVP требует сложного деплоя без Compose-пути;
- auth/model complexity растет быстрее, чем курс;
- roadmap наполняется enterprise-функциями или commercial LMS features;
- пользовательские сценарии становятся вторичными;
- простые задачи требуют архитектурных церемоний;
- агент смешивает legacy FastAPI правила с target Next.js без явной задачи;
- graph/visualization libraries добавляются до Phase 2b «на будущее».

## Проверка новой идеи

Перед добавлением идеи нужно ответить:

1. Какой учебный friction она снижает?
2. Какой next step она делает понятнее?
3. Какой execution она усиливает?
4. Как она влияет на progress/review/stuck flow?
5. Согласуется ли с `docs/architecture/` и **какой фазе** MVP_ROADMAP?
6. Можно ли сделать это проще?
7. Нужно ли это именно сейчас, а не в Phase 2b/3/…?
8. Не превращает ли это проект в generic LMS, marketplace или platform-building?

Если ответы неубедительны, идею нужно отложить.

## Контентные guardrails

Контентная стратегия остаётся source-backed.

Target: курсы в БД через Course Builder; `content/` — reference, blueprints, import source — не автоматический runtime SoT после cutover.

Нельзя:

- писать полный курс с нуля без отдельного решения;
- превращать платформу в список ссылок;
- добавлять источники без curation;
- добавлять темы, которые не ведут к Python backend + AI product skills;
- раздувать уроки без практического результата;
- тихо вернуть file-only runtime как primary без решения.

## UX guardrails

UI должен оставаться функциональным и читаемым. Landing — вторична; приоритет — dashboard, course player, admin course editor; graph — **дополнительный** экран (см. [NEXT_FULLSTACK_ADAPTATION.md](../architecture/NEXT_FULLSTACK_ADAPTATION.md)).

Нельзя:

- жертвовать readability ради mood;
- перегружать markdown body декоративными слоями;
- делать AI-панель или graph canvas центральным баннером вместо next step;
- делать generic neutral LMS без характера;
- делать визуальные эффекты, которые мешают next step.

## AI guardrails

AI — вспомогательный слой ([AI_LAYER.md](../architecture/AI_LAYER.md)), не владелец прогресса.

Допустимо:

- review support (assist);
- stuck flow support;
- объяснения по текущему lesson context;
- weekly recap;
- author draft (для автора, не для learner progress).

Недопустимо:

- открытие модулей/уроков, выставление completion, изменение pass/fail через AI tools;
- запись AI в `LessonProgress`, `Enrollment`, submission verdict;
- бесконтрольный autopilot;
- генерация случайного курса вместо curated path;
- замена execution на «AI сделал за пользователя»;
- скрытое расширение scope под видом AI layer.

## Execution / runner guardrails

| Режим | Когда |
|-------|-------|
| MVP-safe | quiz, text, manual review — без произвольного кода |
| Trusted | subprocess только для admin/trusted, вне web request path |
| Production | `worker/` + Docker sandbox, limits |

Untrusted user code **не** исполняется в Next.js process и не в синхронном Server Action path.

## Не зафиксировано (отдельные решения позже)

- Полная политика sandbox для production runner (Phase 2+).
- Детальный governance для API-mode AI (`AI_MODE=api`).
- Финальный формат automated review pipeline.
- Включение public signup.
- Sigma.js вместо React Flow для large graphs.
- Auto-generate graph edges из markdown wikilinks.
