# REVIEW_BLOCK

## Checklist review
- Структура файлов соответствует canonical schema.
- Нет orphan tasks/checkpoints/lessons.
- Все source_ids валидны и есть в registry.
- Каждый lesson содержит Action + DoD + Technical English.
- Есть checkpoint и минимум 2 lessons в модуле.

## Команды
- `python scripts/validate_content.py`
- `python scripts/report_curriculum.py`
