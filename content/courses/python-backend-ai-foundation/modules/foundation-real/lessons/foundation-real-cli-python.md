---
key: foundation-real-cli-python
title: "Урок 2: Базовый Python execution loop"
summary: Перейти от REPL к маленькому CLI-скрипту и запуску с аргументами.
objectives:
  - Написать маленький скрипт с `argparse`
  - Прогнать один и тот же скрипт в нескольких CLI-сценариях
checklist:
  - Пройти секции Python Tutorial и Argparse Tutorial в заданном объёме
  - Создать скрипт и проверить run/help/output
  - Отправить в submission конкретный вывод команд
task_slug: foundation-python-cli-smoke
---
# Зачем этот шаг в маршруте

Foundation должен приводить к выполнению. Этот урок закрывает минимальный паттерн: `написал файл -> запустил командой -> получил наблюдаемый вывод`.

## Backbone sources

- Python Docs: [Using the Python Interpreter](https://docs.python.org/3/tutorial/interpreter.html)
  - Повтори секцию `2.1 Invoking the Interpreter` только как напоминание по запуску.
- Python Docs: [Argparse Tutorial](https://docs.python.org/3.9/howto/argparse.html)
  - Пройти блоки: `Concepts`, `Introducing optional arguments`.

## Практический шаг после чтения

Сделай файл `scripts/hello_cli.py`:

- принимает аргумент `--name`;
- печатает строку `Hello, <name>!`;
- при `--help` показывает usage.

Прогони минимум 3 запуска:

- `python scripts/hello_cli.py --name Oleg`
- `python scripts/hello_cli.py --name backend`
- `python scripts/hello_cli.py --help`

## Что считаем done

- Скрипт запускается из терминала без ручных правок между запусками.
- Есть валидный вывод для двух значений `--name`.
- Есть вывод help, подтверждающий CLI-интерфейс.
