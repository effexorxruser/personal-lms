# Адаптация Next.js 15 LMS под Personal/Friends AI-LMS

## Назначение документа

Master-документ целевой full-stack архитектуры. Описывает, как коммерческая модель LMS (оплаты, marketplace, video-first, Vercel-only) адаптируется под **self-hosted AI-assisted private learning platform** для маленькой группы (себя и друзей).

Связанные документы:

- [DATABASE_MODEL.md](DATABASE_MODEL.md)
- [AUTH_AND_ROLES.md](AUTH_AND_ROLES.md)
- [COURSE_CONTENT_MODEL.md](COURSE_CONTENT_MODEL.md)
- [AI_LAYER.md](AI_LAYER.md)
- [DEPLOYMENT_MODEL.md](DEPLOYMENT_MODEL.md)
- [MVP_ROADMAP.md](MVP_ROADMAP.md)
- [COURSE_KNOWLEDGE_GRAPH.md](COURSE_KNOWLEDGE_GRAPH.md)

Предыдущая runtime-архитектура (FastAPI + file-based content): [docs/product/ARCHITECTURE_OVERVIEW.md](../product/ARCHITECTURE_OVERVIEW.md).

---

## Определение продукта

> Self-hosted AI-assisted private learning platform для маленькой группы.

Ключевая ценность:

- фиксированный learning path;
- маленький следующий шаг;
- задания и submissions;
- детерминированный прогресс;
- AI hints (без управления прогрессом);
- stuck-flow;
- weekly review;
- создание курсов через сайт;
- импорт/экспорт курсов.

Это **не** marketplace, не enterprise LMS и не multi-tenant SaaS.

---

## Исключено из исходной commercial LMS-модели

| Область | Статус |
|---------|--------|
| Stripe / платежи | Полностью исключено |
| Подписки и billing | Исключено |
| Marketplace курсов | Исключено |
| Public commercial checkout | Исключено |
| Sales analytics | Исключено |
| Public self-signup по умолчанию | Исключено |
| Video-first архитектура | Не ядро; видео — опциональное вложение |
| Vercel как единственный deploy target | Исключено; optional cloud path |
| Browser IDE | Исключено из MVP |
| Multi-tenant SaaS | Исключено |
| AI autopilot прогресса | Исключено |

---

## Добавлено под нашу модель

| Область | Описание |
|---------|----------|
| Access model | Admin создаёт пользователей; enrollment вместо оплаты |
| Роли | `admin`, `author`, `learner` |
| Course Builder | Главный экран продукта, не landing |
| DB as source of truth | Postgres хранит структуру и контент курсов |
| Import/Export | JSON/ZIP как переносимый формат, не runtime SoT |
| Course access modes | `private`, `platform_users`, `assigned_users` |
| AI modes | `disabled`, `external`, `api` |
| Self-hosted deploy | Docker Compose на VPS/VM — primary path |
| Audit log | Для admin-действий |
| Weekly review | Отдельная сущность и UI |
| Stuck flow | `StuckRequest` + AI assist (read-only context) |

---

## Previous runtime vs Target runtime

| Аспект | Previous (текущий репозиторий) | Target |
|--------|-------------------------------|--------|
| Web framework | FastAPI + Jinja2 SSR | Next.js 15 App Router + RSC |
| Мутации | Form POST + Python handlers | Server Actions + Route Handlers |
| БД | SQLite + SQLModel | PostgreSQL + Prisma |
| Контент SoT | Файлы в `content/` | Postgres (`Lesson.bodyMarkdown`, …) |
| Auth | Session cookie + `User.role` string | Better-Auth |
| AI | Lain helper (httpx → external) | `AI_MODE` + `AIRequest` log |
| Terminal/runner | In-process lesson sandbox | MVP-safe tasks; worker sandbox позже |
| Deploy | uvicorn / простой Docker | Compose: next-app, postgres, redis, caddy, worker |

### Mapping сущностей (current → target)

| Current (`app/models.py`) | Target (Prisma) |
|---------------------------|-----------------|
| `User` + `role: str` | `User` + `Role` enum |
| file registry (`content/courses/`) | `Course`, `Module`, `Lesson`, `Task`, `Resource` |
| — | `Enrollment`, `CourseAccess` |
| `CourseProgress` | `Enrollment` + агрегированный progress |
| `LessonProgress` | `LessonProgress` |
| `TaskSubmission` | `TaskSubmission` |
| `ReviewResult` | `ReviewResult` |
| `CheckpointSubmission` | `CheckpointSubmission` |
| `CheckpointReview` | `CheckpointReview` |
| `StuckEvent` | `StuckRequest` |
| recap UI state | `WeeklyReview` |
| `AIHelperMessage` | `AIRequest` |
| `TerminalRun` | Phase 2+ / `worker/` (не в Next process) |

Детали схемы: [DATABASE_MODEL.md](DATABASE_MODEL.md).

---

## Целевой стек

### Frontend / Full-stack

- Next.js 15, App Router, Server Components, Server Actions
- TypeScript
- Tailwind CSS
- shadcn/ui

### Database

- PostgreSQL
- Prisma ORM
- Prisma Migrate — единственный путь изменения схемы
- Dev: local Postgres через Docker Compose

### Auth

- Better-Auth
- Email/password или email OTP
- GitHub OAuth — optional
- Self-signup выключен; пользователей создаёт admin

### Security (optional)

- Arcjet: rate limiting, bot protection, login abuse — **не замена** RBAC и архитектурной безопасности

### File storage

- MVP: local volume через Docker
- Production: S3-compatible + presigned URLs + validation

### AI

- `AI_MODE=disabled | external | api`
- MVP: `external` (prompt-pack)
- Позже: OpenAI API mode

### Deploy

- Primary: Docker Compose на VPS/VM/Proxmox
- Optional: Vercel + Neon + S3

---

## Структура репозитория (target)

```text
repo/
  app/                          # Next.js App Router (заменяет Python app/)
    (auth)/
    (learner)/
    (admin)/
    api/
  components/
    ui/ layout/ course/ lesson/ admin/ ai/ progress/
  features/
    auth/ users/ courses/ lessons/ tasks/ progress/
    enrollments/ ai/ uploads/ weekly-review/
  lib/
    auth/ db/ prisma/ storage/ ai/ security/ validation/ permissions/
  prisma/
    schema.prisma
    migrations/
    seed.ts
  content-import/
    schemas/
    importers/
    exporters/
  worker/
    runner/
    jobs/
  infra/
    docker-compose.yml
    Caddyfile
    scripts/
  legacy/
    fastapi-app/                # архив previous runtime (после cutover Phase 1)
  docs/
    architecture/               # этот набор документов
    product/
    course_authoring/           # authoring guidelines (не runtime SoT)
  content/                      # archive/reference (fresh start при cutover)
```

### Cutover каталога `app/`

Сейчас `app/` — Python-пакет FastAPI. Перед Phase 1:

1. Создать git tag `pre-next-cutover` (или аналог).
2. Перенести Python runtime в `legacy/fastapi-app/`.
3. Инициализировать Next.js в `app/`.

Без этого шага имена каталогов конфликтуют.

---

## Принципы UI (приоритет экранов)

Landing page — вторична. Главные экраны:

1. Dashboard (learner)
2. Course catalog
3. Course player / lesson reader
4. Admin course editor
5. Lesson editor (Markdown)
6. Progress
7. Weekly review
8. Course knowledge graph (дополнительная навигация, не замена reader)

Admin: users, courses, access, import, uploads, graph editor.

Маршруты (target):

| Группа | Пути |
|--------|------|
| Public/Auth | `/login` |
| Learner | `/dashboard`, `/courses`, `/courses/[courseId]`, `/courses/[courseId]/graph`, `/learn/[courseId]/[lessonId]`, `/weekly-review` |
| Admin | `/admin`, `/admin/users`, `/admin/courses`, `/admin/courses/new`, `/admin/courses/[courseId]/edit`, `/admin/courses/[courseId]/modules`, `/admin/courses/[courseId]/lessons/[lessonId]`, `/admin/courses/[courseId]/graph`, `/admin/courses/[courseId]/access`, `/admin/import`, `/admin/uploads` |

---

## Server Actions vs Route Handlers

### Server Actions

- формы create/update/delete (course, module, lesson);
- publish/unpublish;
- mark lesson complete;
- enroll;
- assign course access;
- weekly review submit;
- admin user CRUD.

### Route Handlers (`app/api/...`)

- file uploads;
- AI endpoints (`/api/ai/*`);
- import/export;
- presigned URLs;
- future runner API (`/api/runner/*`).

Правило: если нужен streaming, binary, webhook или внешний клиент — Route Handler; если HTML form mutation от своего UI — Server Action.

---

## Оплаты заменены enrollment / access control

Вместо Stripe/checkout:

- admin создаёт пользователей;
- admin/author публикует курсы;
- learner записывается на доступные курсы;
- `assigned_users` — курс виден только назначенным;
- `platform_users` — всем залогиненным;
- `private` — только admin/author.

См. [AUTH_AND_ROLES.md](AUTH_AND_ROLES.md), [DATABASE_MODEL.md](DATABASE_MODEL.md).

---

## AI не управляет прогрессом

AI **может**: объяснять урок, давать hint, помогать в stuck, review submission (assist), draft lesson для автора, weekly recap.

AI **не может**: открывать модули, выставлять completion, менять pass/fail, писать в `LessonProgress` / `Enrollment`.

См. [AI_LAYER.md](AI_LAYER.md).

---

## Runner (кратко)

| Режим | Когда |
|-------|-------|
| MVP-safe | quiz, text, manual review — без произвольного кода |
| Trusted | subprocess только для admin/trusted |
| Production | отдельный `worker/`, Docker sandbox, limits |

Untrusted code **не** запускается внутри Next.js process.

См. [DEPLOYMENT_MODEL.md](DEPLOYMENT_MODEL.md).

---

## Fresh start контента

При cutover существующие `content/` и blueprints **не** импортируются автоматически. Они остаются reference/archive. Новые курсы создаются через Course Builder или import JSON/ZIP.

Старый file-based pipeline: [docs/course_authoring/COURSE_PACK_CONTRACT.md](../course_authoring/COURSE_PACK_CONTRACT.md) — authoring guidelines для import format, не runtime layout.

---

## Guardrails (синхронизировано с target)

Обновлено для Phase 1:

- [AGENTS.md](../../AGENTS.md) — target stack (Next.js 15 full-stack), legacy FastAPI, ограничения runner/AI/payments;
- [docs/product/PROJECT_GUARDRAILS.md](../product/PROJECT_GUARDRAILS.md) — архитектурный pivot, enrollment вместо payments, runner/AI deny list.

Phase 0 зафиксировал целевую архитектуру; guardrails приведены в соответствие перед cutover.

---

## Связь с продуктовыми документами

Без изменения смысла сохраняются:

- [PRODUCT_VISION.md](../product/PRODUCT_VISION.md)
- [LEARNING_MODEL.md](../product/LEARNING_MODEL.md)
- [MVP_SCOPE.md](../product/MVP_SCOPE.md) — как описание **previous** MVP; новые границы — [MVP_ROADMAP.md](MVP_ROADMAP.md)
