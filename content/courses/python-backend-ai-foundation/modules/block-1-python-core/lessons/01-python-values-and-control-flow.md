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
Это базовая механика для любого backend-скрипта: принять вход, проверить его, выбрать ветку логики, вернуть понятный результат.  
Если здесь есть пробелы, дальше будет сложно писать надежные CLI-инструменты и обработчики данных.

## Core idea (RU)
### Шаг 1: value и variable
- **Value** — само значение (`42`, `"привет"`, `True`).
- **Variable** — имя для этого значения.

Мини-пример:

```python
score = 75
print(score)
```

### Шаг 2: базовые типы
- `int` — целое число (`10`)
- `float` — дробное число (`10.5`)
- `str` — текст (`"10"`)
- `bool` — `True` или `False`

### Шаг 3: важное правило про input()
`input()` всегда возвращает строку.

```python
user_text = input("Введите число: ")
print(user_text)
print(type(user_text))
```

Поэтому перед сравнением с числами нужно сделать конвертацию:

```python
score = int(user_text)
```

### Шаг 4: if / elif / else
Это основной инструмент выбора ветки:

```python
if score >= 90:
    print("excellent")
elif score >= 75:
    print("good")
else:
    print("needs-work")
```

Циклы (`for`, `while`) пока вторичны. В этой задаче главное — корректные условия и обработка невалидного ввода.

## Runnable example
```python
user_text = input("Введите score (0..100): ")

try:
    score = int(user_text)
except ValueError:
    print("Ошибка: введи целое число")
else:
    if score < 0 or score > 100:
        print("Ошибка: число должно быть в диапазоне 0..100")
    elif score >= 90:
        print("excellent")
    elif score >= 75:
        print("good")
    elif score >= 60:
        print("ok")
    else:
        print("needs-work")
```

## Run and expected output
```bash
python score_label.py
```

Expected output examples:
- input: `95` -> `excellent`
- input: `78` -> `good`
- input: `61` -> `ok`
- input: `20` -> `needs-work`
- input: `abc` -> `Ошибка: введи целое число.`
- input: `101` -> `Ошибка: число должно быть в диапазоне 0..100.`

## Частые ошибки
- Забыли, что `input()` возвращает `str`, и сравнивают строку с числом.
- Делают `int(input())` без `try/except`, получают падение на `abc`.
- Проверяют диапазоны в неверном порядке и получают неправильную классификацию.
- Не обрабатывают значения меньше 0 и больше 100.

## Как это связано с задачей
Task `foundation-python-types-and-flow` просит сделать именно этот pipeline:
1) принять input;  
2) безопасно привести тип;  
3) провалидировать диапазон;  
4) вернуть понятную категорию.

Если пример выше у тебя работает на разных входах, ты уже закрыл большую часть задачи.

## What to read (EN source)
- Sources использованы как backbone для этого урока.
- Optional deep dive:
  - Python MOOC: variables, conditions, loops.
  - Automate the Boring Stuff: вводные главы про переменные и контроль потока.
  - Python docs tutorial: introduction + interpreter basics.

Дополнительные ссылки (опционально):
- https://docs.python.org/3/tutorial/introduction.html
- https://docs.python.org/3/tutorial/interpreter.html

## What to skip
- Продвинутые темы (decorators, metaclasses, async) на этом шаге.  
- Теоретические детали реализации интерпретатора, не влияющие на текущую задачу.

## Action
Сделай `score_label.py` пошагово:
1. Принимает число (0-100) через `input()`.
2. Пробует конвертировать строку в `int`.
3. Для ошибки конвертации печатает:
   - `Ошибка: введи целое число`
4. Для значения вне диапазона печатает:
   - `Ошибка: число должно быть в диапазоне 0..100`
5. Для валидного значения печатает категорию:
   - `90+ -> excellent`
   - `75-89 -> good`
   - `60-74 -> ok`
   - `<60 -> needs-work`

Запусти минимум 5 тестовых входов, включая невалидный.

## Optional media
> Placeholder for embedded video:  
> topic: Python values, types, input conversion, control flow  
> usage: optional explanation, not required for completion  
> note: deep dive only, основной материал уже есть в уроке

## Definition of Done
- Скрипт запускается локально без падения.
- Все 4 диапазона дают правильную категорию.
- Невалидный ввод обрабатывается без traceback.
- В выводе есть понятные сообщения для пользователя.

## Technical English
- **value** — значение: конкретные данные (`10`, `"hi"`, `True`).
- **variable** — переменная: имя, которое указывает на значение.
- **condition** — условие: выражение, которое даёт `True` или `False`.
- **type conversion** — преобразование типа: например `str` -> `int`.
- **branching** — ветвление: выбор одной из веток через `if/elif/else`.
- **edge case** — пограничный случай: редкий ввод, где часто прячется ошибка.
