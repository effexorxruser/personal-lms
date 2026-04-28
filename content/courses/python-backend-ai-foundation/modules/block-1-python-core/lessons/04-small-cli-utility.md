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

## Core idea (RU)
### Что мы уже умеем после 3 уроков
- принимать и проверять input;
- выносить логику в функции и отдельные файлы;
- читать/записывать файлы;
- обрабатывать типичные ошибки без падения.

### Как собрать из этого CLI utility
Этот урок собирает знакомые детали в один сценарий:
- типы и ветвления;
- функции и модульность;
- чтение/запись файла;
- базовую обработку ошибок.

Цель — не “большой проект”, а один понятный скрипт + один helper-файл.

### Минимальный алгоритм (plain RU)
1. Получить путь к входному файлу.
2. Прочитать строки.
3. Убрать пустые строки.
4. Преобразовать значения в числа.
5. Посчитать `count`, `sum`, `average`.
6. Записать отчет в файл.
7. Если ошибка — показать понятное сообщение.

## Runnable example
`expenses_core.py`:

```python
def parse_values(lines):
    values = []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        values.append(float(text))
    return values


def build_report(values):
    if not values:
        return "count=0\nsum=0\naverage=0\n"
    total = sum(values)
    avg = total / len(values)
    return f"count={len(values)}\nsum={total}\naverage={avg}\n"
```

`expenses_cli.py`:

```python
from pathlib import Path
import sys

from expenses_core import build_report, parse_values


def main():
    if len(sys.argv) < 2:
        print("Usage: python expenses_cli.py <input_file>")
        return

    input_path = Path(sys.argv[1])
    output_path = Path("expenses_report.txt")
    try:
        lines = input_path.read_text(encoding="utf-8").splitlines()
        values = parse_values(lines)
    except FileNotFoundError:
        print("Ошибка: входной файл не найден.")
        return
    except ValueError:
        print("Ошибка: во входном файле есть нечисловое значение.")
        return

    output_path.write_text(build_report(values), encoding="utf-8")
    print(f"OK: report saved to {output_path}")


if __name__ == "__main__":
    main()
```

## Run and expected output
```bash
python expenses_cli.py sample_expenses.txt
```

Expected output:
- success: `OK: report saved to expenses_report.txt`
- missing file: `Ошибка: входной файл не найден.`
- invalid numeric line: `Ошибка: во входном файле есть нечисловое значение.`

## Частые ошибки
- Пытаются сделать всё в одном файле без выделения core-логики.
- Не проверяют отсутствие файла и получают traceback.
- Не обрабатывают нечисловую строку, из-за чего скрипт падает на `float(...)`.
- Сразу уходят в сложную архитектуру вместо маленького стабильного результата.

## Как это связано с задачей
В первом publish pass этот урок — bridge к checkpoint:
- ты собираешь один рабочий CLI-артефакт;
- подтверждаешь, что умеешь комбинировать навыки прошлых уроков;
- optional/stretch task может быть сделана отдельно, но не обязательна для прохождения модуля.

## What to read (EN source)
- Sources использованы как backbone для этого урока.
- Optional deep dive:
  - Python MOOC: recap по functions/modules/files.
  - Automate the Boring Stuff: small automation scripts.
  - Python docs tutorial: аргументы и базовые паттерны скриптов.

Дополнительная ссылка (опционально):
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

## Optional media
> Placeholder for embedded video:  
> topic: build a simple Python CLI utility from smaller functions  
> usage: optional explanation, not required for completion

## Definition of Done
- Есть минимум 2 файла: core module + CLI entrypoint.
- Утилита корректно обрабатывает валидный вход и хотя бы 1 ошибочный кейс.
- `expenses_report.txt` создается с корректными полями `count/sum/average`.
- Код читаемый: функции не слишком длинные, имена понятные.

## Technical English
- **CLI (Command Line Interface)** — интерфейс через терминал.
- **entrypoint** — точка входа скрипта, откуда начинается выполнение.
- **validation** — проверка корректности входных данных.
- **error handling** — обработка ошибок, чтобы не падать при ожидаемых сбоях.
- **report** — отчет с итоговыми метриками.
- **stretch goal** — дополнительная цель, не обязательная для базового прохождения.
