---
key: 03-files-errors-and-debugging
title: Файлы, исключения и базовый debugging
summary: Работаем с чтением и записью файлов, обрабатываем исключения и проверяем поведение на ошибочных сценариях.
objectives:
  - Читать и записывать текстовые файлы через контекстный менеджер.
  - Ловить ожидаемые исключения и формировать понятные сообщения.
  - Проверять ошибки на минимальном наборе сценариев.
checklist:
  - Протестировал отсутствие входного файла.
  - Добавил обработку хотя бы двух типов ошибок.
  - Проверил, что полезный вывод записывается в файл.
task_slug: foundation-files-and-errors
source_ids:
  - python-mooc
  - automate-boring-stuff
  - python-docs
---

## Why this matters (RU)
Практический backend почти всегда работает с I/O: файлы, логи, конфиги.  
Если не обрабатывать ошибки, даже простая утилита ломается на реальном вводе.

## Core idea (RU)
### Шаг 1: что такое файл в программе
Файл — это внешний источник/приёмник данных.  
Программа читает вход из файла и может сохранить результат в другой файл.

### Шаг 2: читаем файл (micro-example)
```python
with open("todo.txt", "r", encoding="utf-8") as file:
    text = file.read()

print(text)
```

### Шаг 3: пишем файл (micro-example)
```python
with open("report.txt", "w", encoding="utf-8") as file:
    file.write("done")
```

### Шаг 4: что если файла нет
Без обработки ошибки Python покажет traceback.
Это нормальный диагностический сигнал, а не “стыдная ошибка”.

### Шаг 5: `try/except` для контролируемого поведения
```python
try:
    with open("todo.txt", "r", encoding="utf-8") as file:
        text = file.read()
except FileNotFoundError:
    print("Ошибка: файл todo.txt не найден")
```

### Шаг 6: test case
Test case = конкретный вход + ожидаемый результат.
Пример:
- вход: `todo.txt` с двумя непустыми строками и одной пустой;
- ожидаемый результат: `total_items=2`.

## Runnable example
```python
def summarize_todo(input_path="todo.txt", output_path="todo_report.txt"):
    try:
        with open(input_path, "r", encoding="utf-8") as file:
            items = [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print("Ошибка: todo.txt не найден")
        return

    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(f"total_items={len(items)}\n")
    except OSError as exc:
        print(f"Ошибка записи файла: {exc}")
        return

    print(f"OK: report saved to {output_path}")

if __name__ == "__main__":
    summarize_todo()
```

## Run and expected output
```bash
python todo_summary.py
```

Expected output examples:
- Если `todo.txt` существует: `OK: report saved to todo_report.txt`
- Если файла нет: `Ошибка: todo.txt не найден.`

Test case (manual):
- Input file `todo.txt`:
  - `Buy milk`
  - *(empty line)*
  - `Call doctor`
- Expected report:
  - `total_items=2`

## Частые ошибки
- Открывают файл без `encoding="utf-8"` и ловят проблемы с символами.
- Не фильтруют пустые строки, получают завышенный счётчик.
- Ловят слишком широкий `except Exception` и теряют полезную диагностику.
- Не отличают ошибку чтения от ошибки записи.

## Как это связано с задачей
Task `foundation-files-and-errors` требует:
- корректную работу с `todo.txt` и `todo_report.txt`;
- обработку отсутствующего входного файла;
- проверяемый результат.

Если runnable example у тебя работает на валидном и ошибочном сценарии, ты почти готов к сдаче задачи.

## What to read (EN source)
- Sources использованы как backbone для этого урока.
- Optional deep dive:
  - Python MOOC: file handling and exceptions (вводный уровень).
  - Automate the Boring Stuff: chapters with file operations.
  - Python docs: errors and exceptions tutorial.

Дополнительная ссылка (опционально):
- https://docs.python.org/3/tutorial/errors.html

## What to skip
- Сложные уровни exception hierarchy, которые не нужны для базового CLI.
- Продвинутые инструменты профилирования и трассировки.

## Action
Сделай скрипт `todo_summary.py`, который:
1. Читает `todo.txt` (по одному пункту на строку).
2. Считает количество непустых пунктов.
3. Записывает итог в `todo_report.txt` в формате:
   `total_items=<N>`.
4. Если `todo.txt` отсутствует, печатает понятную ошибку и завершает работу без traceback.

Добавь минимум один test case (конкретный вход + ожидаемый результат) с пустыми строками внутри `todo.txt`.
Достаточно ручной проверки через запуск скрипта в терминале, без отдельного pytest-набора на этом шаге.

## Optional media
> Placeholder for embedded video:  
> topic: Python files, try/except, traceback basics  
> usage: optional explanation, not required for completion

## Definition of Done
- Используется `with open(...)` для чтения и записи.
- Ошибка отсутствующего файла обрабатывается через `except`.
- `todo_report.txt` создается и содержит ожидаемый итог.
- Скрипт не падает на пустых строках во входных данных.

## Technical English
- **file I/O** — операции чтения/записи файлов.
- **exception** — исключение: сигнал ошибки времени выполнения.
- **traceback** — стек вызовов: где и почему программа упала.
- **context manager** — контекстный менеджер: безопасная работа с ресурсом через `with`.
- **error handling** — обработка ошибок: контролируемая реакция на сбой.
- **test case** — тестовый случай: конкретный вход + ожидаемый результат.
