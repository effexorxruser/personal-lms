---
key: block-0-workspace-baseline
title: "Урок 0.1: Подготовка учебного workspace"
summary: Собираем локальную рабочую папку и фиксируем стартовый run-log с проверкой окружения.
objectives:
  - Создать стабильную структуру учебной директории.
  - Проверить, что терминал и Python доступны из рабочего окружения.
checklist:
  - Создана папка `learning-workspace` с подпапками `notes/` и `scripts/`.
  - Выполнены команды `pwd`, `python --version`, `git --version`.
  - Результаты сохранены в `notes/foundation-log.txt`.
task_slug: foundation-workspace-ready
source_ids:
  - vscode-docs
  - terminal-reference
  - python-mooc
---
# Block 0 · Workspace baseline

## Why this matters (RU)
Если рабочая среда хаотична, обучение распадается на случайные шаги. Этот урок задаёт единый операционный базис, на котором будет строиться весь курс.

## What to read (EN source)
- VS Code Docs: Terminal basics (открытие и использование интегрированного терминала).
- Terminal Reference: команды `pwd`, `cd`, `mkdir` и навигация по директориям.
- Python MOOC: секция про запуск Python интерпретатора и проверку окружения.

## What to skip
Пропусти кастомизацию темы терминала, shell aliases, продвинутые настройки редактора и любые разделы про плагины вне базового запуска.

## Action
Создай `learning-workspace`, внутри сделай `notes/` и `scripts/`. Выполни `pwd`, `python --version`, `git --version`. Сохрани команды и вывод в `notes/foundation-log.txt`.

## Definition of Done
- В логе указан абсолютный путь к workspace.
- В логе есть вывод всех трёх команд проверки.
- В конце лога есть 1–2 предложения: какой следующий шаг делаешь в Block 0.

## Technical English
- working directory
- integrated terminal
- command output
- path
- environment check
- shell session
