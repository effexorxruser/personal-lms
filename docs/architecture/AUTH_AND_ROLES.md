# Аутентификация и роли

## Назначение документа

Описывает модель входа, ролей и проверки прав для private friends-only LMS на Better-Auth.

Связанные документы: [DATABASE_MODEL.md](DATABASE_MODEL.md), [NEXT_FULLSTACK_ADAPTATION.md](NEXT_FULLSTACK_ADAPTATION.md).

---

## Better-Auth

### Режимы входа

| Режим | MVP | Примечание |
|-------|-----|------------|
| Email + password | Да | Основной для friends |
| Email OTP | Да | Альтернатива password |
| GitHub OAuth | Optional | Включается через env |

### Self-signup

**Выключен по умолчанию.** Регистрация только через admin (`/admin/users`).

Публичная страница `/register` отсутствует или возвращает 404.

### Seeded admin

`prisma/seed.ts` создаёт первого пользователя:

- `role: admin`
- email из `SEED_ADMIN_EMAIL`
- password из `SEED_ADMIN_PASSWORD` (только dev; в prod — смена при первом входе)

---

## Роли

```prisma
enum Role {
  admin
  author
  learner
}
```

| Роль | Назначение |
|------|------------|
| `admin` | Пользователи, доступы, все курсы, audit |
| `author` | Создание и публикация своих курсов, import/export |
| `learner` | Обучение: catalog, enroll, progress, AI assist |

Один пользователь — одна роль (MVP). Комбинированные роли — не в MVP.

---

## Матрица permissions

| Действие | admin | author | learner |
|----------|:-----:|:------:|:-------:|
| CRUD пользователей | ✓ | — | — |
| Список всех курсов (включая draft) | ✓ | own + assigned | published only |
| Создать курс | ✓ | ✓ | — |
| Редактировать курс | ✓ | own draft/published | — |
| Удалить курс | ✓ | own draft only | — |
| Publish / unpublish курс | ✓ | own | — |
| CRUD module / lesson | ✓ | own courses | — |
| Назначить course access (`assigned_users`) | ✓ | — | — |
| Import / export курс | ✓ | ✓ | — |
| Enroll на доступный курс | ✓ | ✓ | ✓ |
| Просмотр урока | ✓ | ✓ | ✓ (enrolled) |
| Mark lesson complete | ✓ | ✓ | ✓ (enrolled) |
| Task submission | ✓ | ✓ | ✓ |
| Stuck request | ✓ | ✓ | ✓ |
| Weekly review | ✓ | ✓ | ✓ |
| AI explain / hint / stuck | ✓ | ✓ | ✓ |
| Audit log read | ✓ | — | — |
| Uploads (admin assets) | ✓ | ✓ (own course) | submission only |

**MVP:** назначение `assigned_users` — только `admin`.

**Author «own»:** `Course.authorId === currentUser.id`.

---

## Course visibility (связь с auth)

Правила видимости курса в каталоге:

| `accessMode` | Кто видит в catalog |
|--------------|---------------------|
| `private` | admin, author курса |
| `platform_users` | все активные залогиненные |
| `assigned_users` | admin, author + пользователи из `CourseAccess` |

Learner enroll возможен только для `published` курсов, прошедших visibility check.

---

## Реализация проверок

### Слой `lib/permissions/`

```text
lib/permissions/
  roles.ts          # Role enum helpers
  course.ts         # canEditCourse, canViewCourse, canPublish
  enrollment.ts     # canEnroll
  admin.ts          # requireAdmin
```

### Server Actions / Route Handlers

Каждый mutation:

1. `auth()` — сессия существует;
2. `requireRole(...)` или domain check;
3. domain check (ownership, enrollment);
4. `auditLog.write(...)` для admin mutations.

Не полагаться только на скрытие кнопок в UI.

### Layout guards

```text
app/(admin)/admin/layout.tsx   → require admin | author (route-level)
app/(learner)/layout.tsx       → require session
app/(auth)/login/page.tsx      → redirect if already logged in
```

Admin-only routes (`/admin/users`, `/admin/import`) — `admin` only.

---

## Session security baseline

| Параметр | Dev | Production |
|----------|-----|------------|
| Cookie `httpOnly` | да | да |
| Cookie `secure` | нет (localhost) | да |
| Cookie `sameSite` | `lax` | `lax` |
| Session TTL | 7d | 7d (настраиваемо) |
| Rotation | Better-Auth defaults | включить refresh |

Секреты только в env (`BETTER_AUTH_SECRET`, `DATABASE_URL`). Не в репозитории, не во frontend bundle.

---

## CSRF

- **Server Actions:** Next.js + cookie session — встроенная защита origin для mutations.
- **Route Handlers:** для cookie-auth POST проверять `Origin` / `Referer` или использовать short-lived tokens для upload forms.
- **API keys** (future runner): отдельный bearer token, не cookie.

---

## Password hashing

Только через Better-Auth (bcrypt/scrypt — по конфигурации библиотеки). Custom hashers не использовать.

---

## Arcjet (optional)

Не заменяет RBAC. Допустимые use cases:

| Rule | Endpoint |
|------|----------|
| Rate limit login | `POST /api/auth/*` |
| Bot protection | public auth routes |
| Brute-force slowdown | failed login by IP + email |

Конфигурация через `ARCJET_KEY` в env. При отсутствии ключа — middleware no-op.

---

## Audit log

Admin mutations пишут в `AuditLog`:

- `user.create`, `user.deactivate`
- `course.publish`, `course.archive`
- `course.access.assign`, `course.access.revoke`
- `import.course`, `export.course`

Поля: `actorId`, `action`, `entityType`, `entityId`, `meta` (JSON).

---

## Env variables (auth)

```text
BETTER_AUTH_SECRET=
BETTER_AUTH_URL=https://lms.example.com
DATABASE_URL=
GITHUB_CLIENT_ID=          # optional
GITHUB_CLIENT_SECRET=      # optional
SEED_ADMIN_EMAIL=
SEED_ADMIN_PASSWORD=       # dev only
ARCJET_KEY=                # optional
```

Валидация через `lib/validation/env.ts` при старте приложения.

---

## Миграция с previous auth

Previous runtime: session cookie + `User.role` string (`admin` | `learner`).

Target: Better-Auth tables + `User.role` enum с добавлением `author`.

При fresh start пользователи не мигрируются из SQLite. Admin создаётся через seed.
