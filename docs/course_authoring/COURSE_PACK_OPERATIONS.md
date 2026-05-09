# Course pack: операции (export / preflight)

Опциональный файл `pack.manifest.yml` рядом с каталогом `courses/` задаёт человекочитаемые метаданные экспорта. **Приложение (runtime LMS) его не загружает** — только скрипты `scripts/check_course_pack.py`, `scripts/review_course_pack.py` и утилиты в `app/course_pack/`.

Граф курсов, задач и чекпоинтов всегда проверяется тем же пайплайном, что и `python scripts/validate_content.py`: `load_content_bundle` в `app/content_pipeline.py`.

## Структура переносимого пака (рекомендуемый layout)

Типичное дерево под одним корнем:

```text
exports/<label>/
  pack.manifest.yml     # необязательно
  courses/              # один или несколько slug-каталогов с course.yml и modules/
  tasks/                # опционально: глобальные *.yml, если экспорт включает их отдельно
  checkpoints/          # или legacy имя checkpoints-global/ в fixture-паках; опционально
  sources/              # опционально: хотя бы source_registry.yml
```

При **отсутствии** локальных каталогов `tasks/` или `checkpoints/` внутри пака preflight временно использует пустые временные директории, чтобы случайно не смешать граф с production `content/tasks` и `content/checkpoints` репозитория.

Если в паке **нет** `sources/source_registry.yml`, при валидации для реестра источников берётся `content/sources` текущего checkout (поведение `resolve_pack_source_root`).

Конфликты между **паком** и целевыми деревьями импорта (дубликаты `course.slug` по каталогам, совпадающие `lesson.key`, пересечения глобальных `tasks/*.yml` и `checkpoints/*.yml`) добавляются в отчёт **без** автоматического разрешения. В сложных сценах встраиваемых в курс задач/чекпоинтов в MVP упор для конфликтов делается на **глобальные** задачи по имени файла в каталоге `tasks/` цели; встроенные `*.task.yml` в дереве урока копируются вместе с курсом и не переименовываются при экспорте.

## Граница человеческого утверждения

Этот этап **не выполняет** автоматический merge файлов в `content/` приложения и не меняет БД или runtime. Одобрённый человеком пак нужно принять процедурно (pull request или копирование файлов) — здесь доступны только `export`, превью/отчёт и ручной review по гайду.

## Скрипты

- `scripts/export_course_pack.py` — read-only загрузка графа из текущего `content/`, затем копирование выбранных курсов в `exports/` (и опционально referenced global tasks/checkpoints/sources, zip).
- `scripts/check_course_pack.py --pack-root <корень>` — анализ пака так же как для импортного превью; коды возврата `0` / `1` по наличию ERROR.
- `scripts/review_course_pack.py` — краткая сводка + ссылка на чеклист.
- `scripts/diff_course_pack.py` — грубый diff двух деревьев (инвентарь размеров + top-level ключи в `courses/*/course.yml`).

Подробнее о контракте файлов см. [`COURSE_PACK_CONTRACT.md`](COURSE_PACK_CONTRACT.md).

См. также: [`docs/local/TESTING.md`](../local/TESTING.md) — полный локальный пайплайн включает `check_course_pack` на fixture-пакет.
