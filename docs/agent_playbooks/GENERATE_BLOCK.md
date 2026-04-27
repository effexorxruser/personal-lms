# GENERATE_BLOCK

## Цель
Сгенерировать только один block из blueprint.

## Процесс
1. Взять block из `content/blueprints/backend_developer_6_months.yml`.
2. Создать/обновить ровно один module и его lessons/tasks/checkpoint.
3. Подтвердить формат lesson (`Action`, `Definition of Done`, `Technical English`).
4. Прогнать `python scripts/validate_content.py` и `python scripts/report_curriculum.py`.

## Ограничения
- Не менять другие блоки.
- Не расширять source stack.
