---
key: 01-python-values-and-control-flow
title: Python значения, типы и управляющий поток
summary: Практика с переменными, типами данных, условными ветками и циклами в формате короткого CLI-скрипта.
objectives:
  - Понять, как Python обрабатывает базовые типы и выражения.
  - Использовать if/elif/else для ветвления.
  - Применять for/while для повторяющихся шагов.
checklist:
  - Запустил скрипт с разными входными значениями.
  - Проверил, что ветвления дают ожидаемый вывод.
  - Зафиксировал 2-3 edge cases.
task_slug: foundation-python-types-and-flow
source_ids:
  - python-mooc
  - automate-boring-stuff
  - python-docs
---

## Why this matters (RU)
Это базовая механика для любого backend-скрипта: чтение входа, принятие решения, вывод результата.  
Без уверенной работы с типами и control flow сложнее строить API-обработчики, CLI-утилиты и валидацию.

## What to read (EN source)
- Python MOOC: базовые разделы про variables, conditions, loops.  
- Automate the Boring Stuff: вводные главы про переменные и контроль потока.  
- Python docs tutorial: introduction + interpreter basics.

Опциональный deep dive:
- https://docs.python.org/3/tutorial/introduction.html
- https://docs.python.org/3/tutorial/interpreter.html

## What to skip
- Продвинутые темы (decorators, metaclasses, async) на этом шаге.  
- Теоретические детали реализации интерпретатора, не влияющие на текущую задачу.

## Action
Сделай мини-скрипт `score_label.py`, который:
1. Принимает число (0-100) через `input()`.
2. Проверяет корректность диапазона.
3. Печатает категорию:
   - `90+ -> excellent`
   - `75-89 -> good`
   - `60-74 -> ok`
   - `<60 -> needs-work`
4. Для нечислового ввода печатает понятную ошибку.

Запусти минимум 5 тестовых входов, включая невалидный.

## Definition of Done
- Скрипт запускается локально без падения.
- Все 4 диапазона дают правильную категорию.
- Невалидный ввод обрабатывается без traceback.
- В выводе есть понятные сообщения для пользователя.

## Technical English
- **variable** — переменная, именованное значение в памяти.
- **condition** — условие, которое возвращает `True/False`.
- **loop** — цикл, повторяющий блок кода.
- **branching** — ветвление выполнения по условиям.
- **edge case** — пограничный случай, где часто скрываются ошибки.
