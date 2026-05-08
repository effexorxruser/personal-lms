# Course Pack Contract

Стабильный file-based контракт для переносимого учебного пакета в `personal-lms`. Runtime не привязан к конкретному курсу: новый курс — это дерево файлов под `content/courses/<course-slug>/`, прошедшее `python scripts/validate_content.py`.

## Версия схемы

- Поле `schema_version: 1` допускается во всех манифестах (см. ниже). Если поле отсутствует, считается `1`.
- Поддерживается только объявленный набор версий; неизвестное значение — ошибка валидации.
- Ветвление логики приложения по `schema_version` не выполняется (foundation only).

## Правила slug и имён

- Формат: lower-kebab-case, латиница, цифры, дефисы (`^[a-z0-9]+(?:-[a-z0-9]+)*$`).
- `course.slug` **должен** совпадать с именем каталога курса: `content/courses/<course-slug>/`.
- `module.yml`: поле `slug` **должно** совпадать с именем родительской папки `modules/<module-slug>/`.
- Урок: в front matter поле `key` совпадает с идентификатором урока в `module.lessons` и с путём на диске (см. layout).
- Задача в глобальном каталоге: файл `content/tasks/<slug>.yml`, внутри `slug` тот же.
- Задача в пакете: файл `.../lessons/<lesson-slug>/tasks/<slug>.task.yml`, внутри `slug` тот же.
- Чекпоинт глобально: `content/checkpoints/<slug>.yml`.
- Чекпоинт в пакете: `.../modules/<module-slug>/checkpoints/<slug>.checkpoint.yml`.

## Каноническая структура каталога

```text
content/
  courses/
    <course-slug>/
      course.yml
      modules/
        <module-slug>/
          module.yml
          checkpoints/
            <checkpoint-slug>.checkpoint.yml   # опционально; альтернатива — глобальный checkpoints/
          lessons/
            <lesson-slug>/
              lesson.md                      # предпочтительно (новые пакеты)
              tasks/
                <task-slug>.task.yml         # опционально; альтернатива — глобальный tasks/
```

**Legacy (поддерживается без миграции):**

- Урок как файл `lessons/<lesson-slug>.md` (без вложенной папки).
- Задачи только в `content/tasks/*.yml`, чекпоинты в `content/checkpoints/*.yml`.

Оба варианта могут сосуществовать; дубликат `slug` задачи или чекпоинта между любыми путями — ошибка.

## Обязательные манифесты

### `course.yml`

- `slug`, `title`, `description`, `modules` (непустой список slug модулей).
- `version` (строка), при необходимости `status` (`available` | `draft` | `archived`), `level`, `tags`, `outcomes`, `prerequisites`.
- Длительность: `duration_weeks` и/или `estimated_weeks` (1..260). Для `status: available` должна быть задана хотя бы одна из оценок (недель > 0).

### `module.yml`

- `slug`, `title`, `description`, `block` (0..6), `objectives` (непустой список строк), `lessons` (непустой список ключей уроков), `checkpoint` (slug существующего чекпоинта).
- Минимум два урока в списке (текущий baseline LMS).

### Урок (`lesson.md` + front matter)

YAML между `---`:

- Обязательно: `key`, `title`, `summary`, `objectives` (минимум одна непустая строка), `source_ids` (минимум один id из `content/sources/source_registry.yml`).
- Опционально: `checklist`, `task_slug` (ссылка на задачу по slug).

Тело Markdown не пустое.

**Baseline-секции (ошибка валидации, для существующего контента):** заголовки второго уровня:

- `Why this matters (RU)`
- `What to read (EN source)`
- `What to skip`
- `Action`
- `Definition of Done`
- `Technical English`

**Контрактные секции на русском (мягкая проверка — предупреждение, не провал валидации):**

- `Зачем это нужно`
- `Объяснение`
- `Практика`
- `Definition of Done`

Рекомендуется со временем привести новые курсы к русским секциям; старые курсы остаются на baseline-заголовках.

### Задача (`.yml` или `.task.yml`)

- `slug`, `title`, `summary`, `instructions`, `submission_type` (`text` | `link` | `command_output`), `definition_of_done`, `review_mode` (`deterministic` | `manual`), опционально `hints`, `terminal`.

### Чекпоинт (`.yml` или `.checkpoint.yml`)

- `slug`, `title`, `summary`, `module_slug`, `description`, `definition_of_done`, `submission_type`, и поля portfolio/deliverables по текущей схеме LMS.

## Детерминированный импорт

1. Положить дерево под `content/courses/<slug>/` (и при необходимости глобальные `tasks` / `checkpoints`).
2. Запустить `python scripts/validate_content.py`.
3. Исправить все `[ERROR]`; просмотреть `[WARN]`.
4. Не требуется правка Python-роутеров или регистрации курса в коде: каталог курсов обнаруживается по `course.yml`.

## Поведение валидатора (кратко)

- Ошибки: нарушение схем, дубликаты slug, сироты, битые ссылки, несовпадение путей и slug.
- Предупреждения: отсутствие русскоязычных секций урока (см. выше).
- Выход CLI: код 1 при любой ошибке, код 0 при отсутствии ошибок (в т.ч. при наличии только предупреждений).

Подробнее о запуске и разработке пакета: [COURSE_AUTHORING_GUIDE.md](COURSE_AUTHORING_GUIDE.md).
