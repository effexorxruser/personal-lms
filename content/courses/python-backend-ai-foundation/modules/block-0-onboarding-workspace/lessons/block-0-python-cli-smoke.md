---
key: block-0-python-cli-smoke
title: "Урок 0.2: Первый Python CLI smoke cycle"
summary: Переходим от REPL к минимальному CLI-скрипту и фиксируем воспроизводимый запуск.
objectives:
  - Создать минимальный CLI-скрипт с аргументом имени.
  - Проверить повторяемость запусков через terminal commands.
checklist:
  - Создан файл `scripts/hello_cli.py`.
  - Выполнены минимум два запуска с разными `--name`.
  - В лог добавлен вывод `--help`.
task_slug: block-0-python-cli-smoke
source_ids:
  - python-mooc
  - automate-boring-stuff
---
# Block 0 · Python CLI smoke cycle

## Why this matters (RU)
Backend-разработка начинается не с теории, а с воспроизводимого цикла: написал файл, запустил, получил наблюдаемый результат. Этот паттерн будет повторяться весь курс.

## What to read (EN source)
- Python MOOC: раздел про запуск Python-файлов из терминала.
- Automate the Boring Stuff: Introduction + базовый пример скрипта с параметрами ввода/вывода.

## What to skip
Пропусти главы про GUI-автоматизацию, web scraping и сложные проекты. На этом шаге нужен только минимальный сценарий CLI-запуска.

## Action
Сделай `scripts/hello_cli.py`, который принимает `--name` и печатает приветствие. Выполни два запуска с разными именами и один запуск `--help`. Вывод добавь в `notes/foundation-log.txt`.

## Definition of Done
- Скрипт запускается командой из корня workspace.
- Есть минимум два валидных вывода с разными аргументами.
- В логе есть блок с `--help` и кратким пояснением назначения скрипта.

## Technical English
- command-line interface
- argument parsing
- script execution
- usage message
- standard output
- reproducible run
