# Curriculum blueprints (previous architecture)

> **Previous architecture — не runtime source of truth.**

Файлы в этой директории (например, `backend_developer_6_months.yml`) — **curriculum blueprints**: долгосрочные планы модулей и задач для source-backed authoring. Они **не** читаются целевым Next.js runtime.

## Статус

| Аспект | Previous (сейчас) | Target |
|--------|-------------------|--------|
| SoT контента | `content/courses/` (файлы) | PostgreSQL |
| Blueprint | планирование curriculum | reference / import source |
| Валидация | `scripts/validate_content.py` | Prisma + Zod + import schema |

## Использование

- Как **reference** при ручном создании курсов в Course Builder.
- Как **источник** для будущего import mapper (`content-import/`), если нужно перенести структуру в БД.
- Не удалять: история curriculum decisions и slug-конвенции.

Целевая архитектура: [docs/architecture/COURSE_CONTENT_MODEL.md](../../docs/architecture/COURSE_CONTENT_MODEL.md).
