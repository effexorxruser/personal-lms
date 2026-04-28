---
key: 04-small-cli-utility
title: Сборка маленькой CLI-утилиты
summary: Собираем модульный Python CLI-инструмент, который читает входные данные, валидирует их и выдает итоговый отчет.
objectives:
  - Объединить типы, функции, модули и обработку ошибок в один артефакт.
  - Сформировать минимально чистую структуру CLI-утилиты.
  - Подготовить результат, который можно показать в checkpoint.
checklist:
  - Есть отдельный модуль с бизнес-логикой.
  - CLI-скрипт запускается и обрабатывает ошибки ввода.
  - Есть демонстрационный пример запуска с ожидаемым результатом.
source_ids:
  - python-mooc
  - automate-boring-stuff
  - python-docs
---

## Why this matters (RU)
Это переход от изолированных упражнений к маленькому рабочему инструменту.  
Такой формат ближе к реальным backend-задачам: есть вход, обработка, ошибки и воспроизводимый результат.

Для first publish pass этот урок рассматривается как checkpoint-prep шаг.
Отдельная task-сущность для него может остаться optional/stretch и не входить в обязательный импорт.

## What to read (EN source)
- Python MOOC: recap по functions/modules/files.
- Automate the Boring Stuff: small automation scripts.
- Python docs tutorial: аргументы и базовые паттерны скриптов.

Опциональный deep dive:
- https://docs.python.org/3/tutorial/stdlib.html

## What to skip
- Большие framework-level решения.
- Сложные CLI-библиотеки (argparse subcommands с большим деревом) на этом этапе.

## Action
Собери утилиту `expenses_cli.py` + `expenses_core.py`:
1. Вход: текстовый файл с числами (каждое число на новой строке).
2. Логика:
   - загрузить значения;
   - отбросить пустые строки;
   - посчитать `count`, `sum`, `average`;
   - обработать нечисловые строки как ошибку с понятным сообщением.
3. Выход: файл `expenses_report.txt` с итогами.

Подготовь пример запуска и покажи результат в консоли.

## Definition of Done
- Есть минимум 2 файла: core module + CLI entrypoint.
- Утилита корректно обрабатывает валидный вход и хотя бы 1 ошибочный кейс.
- `expenses_report.txt` создается с корректными полями `count/sum/average`.
- Код читаемый: функции не слишком длинные, имена понятные.

## Technical English
- **CLI (Command Line Interface)** — интерфейс через терминал.
- **entrypoint** — точка входа скрипта.
- **validation** — проверка корректности входных данных.
- **error handling** — обработка ошибок.
- **report** — отчет с итоговыми метриками.
