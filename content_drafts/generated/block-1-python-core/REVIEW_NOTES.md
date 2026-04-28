# REVIEW NOTES — block-1-python-core draft

## Что сгенерировано

- `module.yml` для `block-1-python-core`
- 4 lesson drafts:
  - `01-python-values-and-control-flow.md`
  - `02-functions-and-modules.md`
  - `03-files-errors-and-debugging.md`
  - `04-small-cli-utility.md`
- 4 task drafts:
  - `foundation-python-types-and-flow.yml`
  - `foundation-functions-and-modules.yml`
  - `foundation-files-and-errors.yml`
  - `foundation-small-cli-utility.yml`
- `checkpoint.yml` (`block-1-python-core-checkpoint`)

## Assumptions

- Для controlled draft generation выбран 4-lesson формат (в blueprint диапазон 4-6).
- Добавлена 4-я задача `foundation-small-cli-utility` как интеграционный step перед checkpoint.
- `task_slug` указан у каждого урока для execution-first консистентности.

## Known gaps

- Это draft-уровень: нет фактического код-артефакта, только authoring content.
- Не выполнялась автоматическая проверка этих файлов через runtime graph, потому что draft лежит вне `content/`.
- Для source-backed глубины не привязаны конкретные цитаты/фрагменты snapshot-файлов (manifest отсутствует).

## Decisions to review before publishing

- Extra task policy (зафиксировано): `foundation-small-cli-utility` остаётся в draft как optional/stretch и НЕ входит в обязательный first publish pass.
- Урок `04-small-cli-utility` трактуется как checkpoint-prep шаг без обязательного task import в первой публикации.
- Нужен ли `terminal` блок в `foundation-small-cli-utility.yml` на этом этапе публикации.
- Финальные формулировки `summary`/`instructions` под тональность курса.

## Validation risks

- Перед переносом в `content/` нужно повторно прогнать schema/graph checks для активного дерева.
- Риск несоответствия ожидаемой сложности learner level при первом проходе блока.
- Риск дублирования с будущими модулями block-2, если scope задач расширится.

## Task slug match vs blueprint expected tasks

Blueprint expected tasks для `block-1-python-core`:
- `foundation-python-types-and-flow` -> **matched**
- `foundation-functions-and-modules` -> **matched**
- `foundation-files-and-errors` -> **matched**

Дополнительно в draft:
- `foundation-small-cli-utility` -> **extra draft task (optional/stretch, not mandatory for first import)**
