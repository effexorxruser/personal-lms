# GENERATE_BLUEPRINT

## Цель
Собрать `content/blueprints/backend_developer_6_months.yml` до генерации любого блока.

## Шаги
1. Прочитать `docs/product/*` (vision/scope/learning/content/source).
2. Заполнить блоки 0..6, модули, lessons/tasks/checkpoints.
3. Проверить, что все source id существуют в `content/sources/source_registry.yml`.
4. Запустить `python scripts/validate_content.py`.
5. Только после review переходить к `GENERATE_BLOCK.md`.

## Запреты
- Не создавать lessons/modules без blueprint.
- Не добавлять источники мимо registry.
