---
key: foundation-real-cli-python
title: "Урок 2: Базовый Python execution loop"
summary: Перейти от REPL к маленькому CLI-скрипту и запуску с аргументами.
objectives:
  - Написать маленький скрипт с `argparse`.
  - Прогнать скрипт в нескольких CLI-сценариях.
checklist:
  - Пройти секции Python Tutorial и Argparse Tutorial в заданном объёме.
  - Создать скрипт и проверить run/help/output.
  - Отправить в submission конкретный вывод команд.
task_slug: foundation-python-cli-smoke
source_ids:
  - python-docs
---
# Foundation Real · Python CLI

## Why this matters (RU)
Foundation должен приводить к выполнению: `написал файл -> запустил командой -> получил наблюдаемый вывод`.

## What to read (EN source)
- Python Docs: https://docs.python.org/3/tutorial/interpreter.html
- Python Docs: https://docs.python.org/3.9/howto/argparse.html

## What to skip
Не уходи в сложные subcommands и продвинутые парсеры аргументов.

## Action
Сделай `scripts/hello_cli.py` с аргументом `--name`, проверь три запуска (два значения имени + `--help`) и добавь вывод в run-log.

## Definition of Done
- Скрипт запускается из терминала без ручных правок между запусками.
- Есть валидный вывод для двух значений `--name`.
- Есть вывод help, подтверждающий CLI-интерфейс.

## Technical English
- command-line argument
- optional argument
- usage
- output
