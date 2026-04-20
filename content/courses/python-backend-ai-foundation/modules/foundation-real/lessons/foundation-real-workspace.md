---
key: foundation-real-workspace
title: "Урок 1: Рабочее место и стартовый ритм"
summary: Подготовить воспроизводимый workspace и зафиксировать минимальный цикл «команда -> результат -> запись».
objectives:
  - Поднять рабочую папку и проверить базовые команды в терминале
  - Зафиксировать понятный стартовый ритм маленькими проверяемыми шагами
checklist:
  - Пройти указанные секции по VS Code Terminal и Python REPL
  - Выполнить стартовые команды в своём workspace
  - Зафиксировать результат выполнения в task submission
task_slug: foundation-workspace-ready
---
# Зачем этот шаг в маршруте

Это первый execution-step foundation-блока: без рабочего workspace дальше не будет стабильного прогресса ни по Python, ни по Git.

## Backbone sources

- VS Code Docs: [Getting started with the terminal](https://code.visualstudio.com/docs/terminal/getting-started)
  - Пройти только разделы: `Run your first command in the terminal`, `Navigate to previous commands`, `Run commands in another shell`.
- Python Docs: [Using the Python Interpreter](https://docs.python.org/3/tutorial/interpreter.html)
  - Пройти секции: `2.1 Invoking the Interpreter`, `2.2 The Interpreter and Its Environment`.

## Практический шаг после чтения

В папке нового учебного workspace выполни минимальный цикл:

1. Открой терминал и проверь рабочую директорию (`pwd`).
2. Проверь Python (`python --version` или `python3 --version`).
3. Запусти REPL и выполни два выражения (`2 + 2`, `print("foundation")`).
4. Выйди из REPL и создай файл `notes/foundation-log.txt` с 3 короткими строками: что запустил, что получил, что следующий шаг.

## Что считаем done

- Есть воспроизводимый workspace-путь.
- Python запускается из терминала.
- Есть короткий run-log с наблюдаемым результатом и следующим шагом.
