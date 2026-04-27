---
key: block-1-git-loop
title: "Block 1 · Git loop"
summary: Подтверждаем минимальный цикл git add/commit для учебного артефакта.
objectives:
  - Закрепить базовый workflow фиксации результата.
  - Добавить доказуемость прогресса через commit history.
checklist:
  - Инициализирован репозиторий.
  - Добавлены файлы и сделан commit.
  - Проверен лог коммитов.
task_slug: foundation-git-github-cycle
source_ids:
  - git-docs
---
# Block 1 · Git loop

## Why this matters (RU)
Без фиксируемого git-цикла сложно проверять прогресс и возвращаться к рабочей версии артефакта.

## What to read (EN source)
- Git docs: https://git-scm.com/docs/git-add
- Git docs: https://git-scm.com/docs/git-commit

## What to skip
Не изучай rebase/cherry-pick на этом этапе.

## Action
Сделай `git init`, `git add .`, `git commit -m "block-1-start"`, затем зафиксируй `git log --oneline` в notes.

## Definition of Done
- Есть commit с понятным сообщением.
- В run-log сохранен вывод `git log --oneline`.
- Изменения соответствуют только scope блока 1.

## Technical English
- staging area
- commit message
- working tree
- commit history
