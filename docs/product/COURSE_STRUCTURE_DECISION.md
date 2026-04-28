# Course Structure Decision

Документ фиксирует решения по зачистке структуры активного курса (v1), согласование с `backend_developer_6_months.yml` и минимальные сопутствующие изменения runtime. Дата: 2026-04.

## Current problem

- Активный курс `python-backend-ai-foundation` совмещал **два Block 0 модуля** и **модуль `foundation-real`** с полем `block: 1`, при этом содержание `foundation-real` семантически дублировало Block 0 (workspace / CLI / git).
- В blueprint для первого модуля Block 0 в `expected_tasks` указан **`foundation-python-cli-smoke`**, а урок `block-0-python-cli-smoke` ссылался на **отдельный** task `block-0-python-cli-smoke` (другой YAML, без terminal и с типом submission `text`).
- Глобальный порядок уроков в индексе строился по всем курсам; кнопки «следующий/предыдущий урок» теоретически могли вести между разными курсами.
- Итог: смешение «3-week active route» и черновика будущего Block 1 без явного разделения в манифестах.

## Active course target

- **`python-backend-ai-foundation`** = только **Block 0**: onboarding/workspace + learning loop (два модуля, как в blueprint block 0).
- Заголовок и описание курса отражают Block 0; `estimated_weeks` снижен до **2** (узкий фокус маршрута).
- Расширенный pass **`foundation-real`** не входит в активный learner path dashboard/recap по умолчанию, но остаётся в репозитории как **draft Block 1**.

## Current active course map

После применения решения v1:

```text
course:
  slug: python-backend-ai-foundation
  title: Python Backend + AI — Block 0 (Onboarding & Learning Loop)
  estimated_weeks: 2
  modules:
    - slug: block-0-onboarding-workspace
      block: 0
      lessons:
        - block-0-workspace-baseline     → task_slug: foundation-workspace-ready
        - block-0-python-cli-smoke         → task_slug: foundation-python-cli-smoke  (канон slug)
        - block-0-git-github-cycle       → task_slug: foundation-git-github-cycle
      checkpoint: block-0-workspace-checkpoint

    - slug: block-0-learning-loop
      block: 0
      lessons:
        - block-0-learning-loop-setup    → task_slug: onboarding-learning-loop-ready
        - block-0-study-log-baseline     → task_slug: onboarding-study-log-baseline
      checkpoint: block-0-learning-checkpoint
```

Отдельный курс-черновик:

```text
course:
  slug: python-backend-ai-foundation-block1-draft
  modules:
    - slug: foundation-real
      block: 1
      lessons:
        - foundation-real-workspace      (без task_slug в YAML)
        - foundation-real-cli-python     → task_slug: foundation-python-cli-smoke
        - foundation-real-git-loop       (без task_slug)
      checkpoint: foundation-real-start-pack
```

## Blueprint comparison

| Область | Blueprint (`backend_developer_6_months.yml`) | Было (кратко) | Стало |
|--------|-----------------------------------------------|----------------|-------|
| Block 0 модуль 1 slug | `block-0-onboarding-workspace` | совпадало | совпадает |
| Block 0 модуль 2 slug | `block-0-learning-loop` | совпадало | совпадает |
| CLI task первого модуля | `foundation-python-cli-smoke` | урок использовал `block-0-python-cli-smoke` | урок → `foundation-python-cli-smoke`, файл `block-0-python-cli-smoke.yml` удалён |
| `foundation-real` в активном маршруте | ожидается в **Block 1** (`block-1-python-core`, …), не как третий модуль в Block 0 | висел в активном `course.yml` с `block: 1` | вынесен в draft-курс |
| Checkpoint foundation | не в том же «active slug», что Block 0-only | `foundation-real-start-pack` на карте активного курса | checkpoint остаётся в графе; UI карты — на `/courses/python-backend-ai-foundation-block1-draft` |

**Нормальные временные отклонения**

- Полное содержание Block 1–6 в YAML по-прежнему только в blueprint, не развёрнуто в `content/courses/`.
- `course-factory-reference` остаётся reference-fixture курсом.

**Что создавало путаницу**

- Три модуля под одним «foundation» заголовком курса при том, что третий помечен `block: 1`.
- Два разных CLI task slug для одной и той же роли в Block 0.

## Decision about foundation-real

**Выбран вариант A + D (комбинация):**

- **A:** модуль **убран из активного** `python-backend-ai-foundation/course.yml` (не удаляются файлы уроков).
- **D:** содержимое сохранено как **черновик будущего Block 1** в отдельном манифесте `content/courses/python-backend-ai-foundation-block1-draft/course.yml`, модуль физически перенесён в `modules/foundation-real/` под этим курсом.

**Обоснование:** валидатор запрещает «осиротевшие» модули и дубли `module.slug` между курсами; отдельный курс — легальный способ убрать модуль из active route без удаления контента. `block: 1` в `module.yml` сохранён как сигнал к blueprint.

## Decision about CLI task slug

**Канонический slug: `foundation-python-cli-smoke`** (как в blueprint).

- Урок `block-0-python-cli-smoke.md`: `task_slug` изменён на `foundation-python-cli-smoke`.
- Файл `content/tasks/block-0-python-cli-smoke.yml` **удалён** (после переназначения урока он стал бы orphan task).
- Поведение урока **меняется** на определение из `foundation-python-cli-smoke.yml`: `submission_type: command_output`, включён **terminal** (как у урока `foundation-real-cli-python`).

**Риск прогресса:** строки `TaskSubmission` с `task_slug=block-0-python-cli-smoke` перестают отображаться для этого урока (поиск идёт по текущему slug). См. раздел ниже.

**Альтернатива отклонена:** оставить `block-0-python-cli-smoke` — расхождение с blueprint оставалось бы без явной пользы.

## Migration / progress risk

| Изменение | Риск |
|-----------|------|
| Удаление модуля из активного курса | `LessonProgress` / `CourseProgress` по **активному** slug пересчитываются только по 5 урокам Block 0; прогресс по `foundation-real-*` остаётся в БД, но не входит в процент активного курса. |
| Смена `task_slug` у `block-0-python-cli-smoke` | Старые submission с `task_slug=block-0-python-cli-smoke` не подхватываются `get_submission_snapshot` для этого урока; при необходимости — разовая SQL-миграция или повторная отправка (вне этой задачи). |
| Checkpoint `foundation-real-start-pack` | `CheckpointSubmission.course_slug` определяется курсом, в котором есть модуль `foundation-real` → теперь **`python-backend-ai-foundation-block1-draft`**. |
| Навигация prev/next | Реализована **в границах `lesson.course_slug`**, чтобы не уходить на другой курс с кнопки «следующий урок». |

**DB migration в этой задаче не выполнялась.**

## Runtime changes (не контент)

Согласованы с целью «не ломать learner UX» при нескольких курсах в индексе:

1. **`app/content_registry.py`** — `get_next_lesson_key` / `get_prev_lesson_key` опираются на порядок уроков **только внутри курса текущего урока**.
2. **`app/services/recap_service.py`** — список блокеров за неделю и **активный блокер** на dashboard/recap учитывают события по **всем** `course_slug` пользователя (иначе блокер с урока draft-курса не попадал бы в сводку активного курса).

Не затронуты: маршруты, шаблоны, Lain, terminal sandbox, схемы БД.

## What is intentionally not changed yet

- Тексты тел уроков, blueprint, source registry.
- Полное развёртывание Block 1–6 из blueprint в отдельные модули.
- SQL-скрипты переноса старых `TaskSubmission.task_slug`.
- Отдельный dashboard для draft-курса (доступ по прямой ссылке на карту курса и уроки).

## Validation commands

```bash
python scripts/validate_content.py
python -m pytest
python -m ruff check .
```

Ожидаемо после v1: **3** курса в отчёте валидации, **5** task-файлов.
