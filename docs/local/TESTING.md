# Локальные проверки (testing)

Полный пайплайн перед PR (как в CI):

```bash
python scripts/check_text_integrity.py
ruff check .
python scripts/validate_content.py
python -m pytest
python scripts/check_course_pack.py --pack-root tests/fixtures/content_pack
```

Опционально (если доступен Docker): `docker build -t personal-lms:ci .`.

## Что есть что

- **`scripts/validate_content.py`** — проверяет **реальный** дерево каталогов `content/` в текущем checkout (courses / tasks / checkpoints / sources по умолчанию). Обязательно для PR с изменениями в контенте.
- **`scripts/check_course_pack.py`** — preflight для **переносимого** course pack под одним корнём (`courses/` обязательны; см. закоммиченный fixture `tests/fixtures/content_pack`). Проверяет граф через тот же пайплайн, что и `validate_content.py`, и опциональные конфликты импорта с целевыми каталогами. Не заменяет `validate_content.py` для основного монорепо `content/` в корне checkout.
- **`python -m pytest`** — использует **изолированные** деревья там, где нужен registry: закоммиченный [`tests/fixtures/content_pack/`](../../tests/fixtures/content_pack), временные `tmp_path` через `tests/content_runtime_utils.py` и утилиты в `tests/content_test_utils.py`. Не нужно иметь учебный catalog в репозитории, чтобы зелёнил smoke-слой.
- Внешние сервисы для полного набора по умолчанию не нужны (`PERSONAL_LMS_OPENAI_API_KEY` пустой допустим в AI-helper тестах с оффлайн-моками).

Подробнее: [`docs/product/TESTING_STABILIZATION_PLAN.md`](../product/TESTING_STABILIZATION_PLAN.md).
