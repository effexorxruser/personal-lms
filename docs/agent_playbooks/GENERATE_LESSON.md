# GENERATE_LESSON

## Source-backed порядок
1. Выбрать source_id из `content/sources/source_registry.yml`.
2. Взять только официальный EN source.
3. Написать русский wrapper без полного перевода.

## Обязательная структура lesson.md
- `## Why this matters (RU)`
- `## What to read (EN source)`
- `## What to skip`
- `## Action`
- `## Definition of Done`
- `## Technical English`

## Front matter
- `key`, `title`, `summary`
- `source_ids`
- `task_slug` (если есть task)

## Критерий качества
Action должен быть выполнимым и проверяемым за один учебный шаг.
