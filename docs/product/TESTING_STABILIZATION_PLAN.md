# Стабилизация testing и runtime fixtures (Stage 6)

Цель этапа: **pytest воспроизводим локально/в CI/в окружениях агентов без неявной зависимости от полного репозиторного `content/`**, при этом **`python scripts/validate_content.py` по-прежнему проверяет реальный file-based контент** репозитория.

## Классификация текущего набора `tests/test_*.py`

| Файл | Что делает контентно | Тип после этапа | Примечание |
|------|----------------------|-----------------|------------|
| `test_app_smoke.py` | HTTP + прогресс + terminal + checkpoints | Интеграция на **`tests/fixtures/content_pack`** | `autouse` патч корней `content_pipeline` + `PERSONAL_LMS_ACTIVE_COURSE_SLUG=test-python-course` |
| `test_ai_helper.py` | Пути страниц `/lessons/...`, `/courses/...` | Интеграция на том же фикспаке | тот же `autouse` |
| `test_ai_helper_ui.py` | Dashboard | Интеграция на том же фикспаке | тот же `autouse` |
| `test_course_requests.py` | Роуты заявок, без привязки к урокам | Интеграция + изолированный registry | патч корней чтобы навигация не тянула production catalog |
| `test_friend_only_auth.py` | Только login / feature gates | Преимущественно unit | терминальный 403 через путь **`__noop__`**, без урока в registry |
| `test_catalog_service.py` | Синтетический `ContentIndex` | Юнит | без диска |
| `test_content_validation.py` | `tmp_path`, `validate_content`, `load_content_bundle` | Юнит на tmp | удалены проверки **production snapshot/registry** (`python-backend-ai-foundation`, block-0 slugs и т.п.) |
| `test_content_integrity.py` | tmp деревья | Юнит | без prod |
| `test_content_prompt_pack.py` | Тексты промптов | Юнит | без prod |
| `test_fixture_content_pack.py` | Фикспак через `validate_content` | Контракт регрессия | гарантия committed pack |
| `test_content_registry_isolation.py` | Смена roots | Изоляция кэша | |
| `test_empty_content_routes.py` | Пустой catalog | Регрессия empty-state | временный каталог без `course.yml` + копия `source_registry.yml` из фикспака |
| `test_content_scaffold.py` | Subprocess scaffold + validate | Интеграция | `--source-root` → `tests/fixtures/content_pack/sources` (в т.ч. id `python-docs` для scaffold) |
| `test_source_fetcher.py` | Обход сетевых интерфейсов | Изолировано | без course registry |

### Удалённые из pytest «production snapshot» зависимости

- **`test_current_content_snapshot_is_valid`** — дублировала CI-шаг `python scripts/validate_content.py`.
- **`test_active_course_includes_block0...`**, **`test_block0_cli_lesson...`**, **`test_foundation_real_module...`** — требовали конкретного curriculum в живом каталоге; инварианты curriculum остаются на **контентном префлайте** и код-ревью, не на агентном pytest без контента.

## Что проверяет `validate_content.py` (оставить отдельно)

- Реальный `content/courses`, `content/tasks`, `content/checkpoints`, `content/sources` на checkout’е где они есть.
- В CI перед pytest (см. `.github/workflows/ci.yml`).

## Исправление скрытых технических проблем

1. **`load_content_bundle`** в [`app/content_pipeline.py`](../../app/content_pipeline.py): аргументы `content_root` / `task_root` / `checkpoint_root` / `source_root` с `None` читаются как **текущие** глобальные пути модуля — monkeypatch корней перед `get_content_registry()` становится возможен без захваченных на этапе `def` объектов по умолчанию.
2. **`load_content_index`** в [`app/content_loader.py`](../../app/content_loader.py): пробрасывает `None`, чтобы использовать те же живые globals.
3. **Nested `lessons/<key>/lesson.md`**: парсинг урока сравнивает **имя каталога** с `key`, а не stem `lesson` ([`content_pipeline.py`](../../app/content_pipeline.py)) — scaffold и контракт согласованы.
4. **`Settings.active_course_slug`** (`PERSONAL_LMS_ACTIVE_COURSE_SLUG`): preferred course для dashboard/recap/active path в [`app/services/content_service.py`](../../app/services/content_service.py), [`app/routers/dashboard.py`](../../app/routers/dashboard.py), [`app/services/ai_helper_service.py`](../../app/services/ai_helper_service.py); dashboard использует **`first_lesson_key_for_course(course.slug)`** вместо несостыковки с активным slug.
5. **Кэш registry**: явный **`get_content_registry.cache_clear()`** в [`tests/content_runtime_utils.py`](../../tests/content_runtime_utils.py) при каждой смене корней.

## Детерминированный контент-пак для pytest

Дерево: [`tests/fixtures/content_pack/`](../../tests/fixtures/content_pack/) — два курса (`test-python-course` **available**, `test-draft-module-course` **draft**), задачи с terminal для CLI-урока, checkpoint на draft-модуле.

Константы ключей для тестов: [`tests/fixture_metadata.py`](../../tests/fixture_metadata.py).

## Ограничения (explicit)

- **Полностью удалить blueprint / source registry** из репозитория нельзя: runtime-пайплайн по-прежнему требует `content/blueprints/...` и валидный `source_registry` при загрузке (для pytest пустого каталога курсов мы копируем минимальный registry из фикспака во временную директорию).
- `README.md` проекта по guardrails репозитория не изменяется; краткая инструкция вынесена в [`docs/local/TESTING.md`](../local/TESTING.md).

## Связанные команды проверки (PR)

См. [`docs/local/TESTING.md`](../local/TESTING.md).
