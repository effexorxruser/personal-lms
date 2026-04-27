---
key: block-1-workspace-baseline
title: "Block 1 · Workspace baseline"
summary: Настраиваем рабочую папку и проверяем минимальный CLI-цикл.
objectives:
  - Зафиксировать стабильную рабочую директорию.
  - Подтвердить базовую работоспособность python и git.
checklist:
  - Создана учебная папка.
  - Выполнены команды проверки окружения.
  - Лог сохранен в notes/foundation-log.txt.
task_slug: foundation-workspace-ready
source_ids:
  - python-docs
  - git-docs
---
# Block 1 · Workspace baseline

## Why this matters (RU)
Стабильный workspace убирает хаос на старте и делает каждое следующее действие повторяемым.

## What to read (EN source)
- Python docs: https://docs.python.org/3/tutorial/interpreter.html
- Git docs: https://git-scm.com/docs/git-init

## What to skip
Пропусти глубокие детали про внутренности интерпретатора и расширенные git-конфиги.

## Action
Создай папку `foundation-workspace`, выполни `pwd`, `python --version`, `git --version`, результат сохрани в `notes/foundation-log.txt`.

## Definition of Done
- Указан абсолютный путь к workspace.
- В лог добавлен вывод всех команд.
- Есть короткая заметка, что делать следующим шагом.

## Technical English
- working directory
- interpreter
- command output
- initialize repository
