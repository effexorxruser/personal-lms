---
key: 02-functions-and-modules
title: Функции и модули для переиспользуемого кода
summary: Разделяем код на функции, переносим логику в модуль и проверяем повторное использование через импорт.
objectives:
  - Выделять повторяющуюся логику в функции.
  - Понимать параметры и возвращаемые значения.
  - Использовать модульный импорт в небольшом проекте.
checklist:
  - Вынес повторяющиеся части в отдельные функции.
  - Сделал импорт из своего модуля.
  - Проверил, что результат одинаков при повторных запусках.
task_slug: foundation-functions-and-modules
source_ids:
  - python-mooc
  - automate-boring-stuff
  - python-docs
---

## Why this matters (RU)
Backend-код быстро разрастается. Если не выделять функции и модули, каждый новый шаг увеличивает хаос и риск ошибок.  
Функции и модули дают базу для чистого, проверяемого кода.

## Core idea (RU)
### Шаг 1: повторение без функции
Часто начинающие пишут одинаковые действия несколько раз:

```python
text1 = "hello world"
print(len(text1.split()))

text2 = "python backend"
print(len(text2.split()))
```

Это работает, но код дублируется.

### Шаг 2: функция без параметров
Первый шаг к упрощению:

```python
def show_fixed_word_count():
    text = "hello world from python"
    print(len(text.split()))

show_fixed_word_count()
```

### Шаг 3: функция с параметром
Теперь функция полезна для разных строк:

```python
def show_word_count(text):
    print(len(text.split()))

show_word_count("hello world")
show_word_count("python backend")
```

### Шаг 4: return
Если результат нужен дальше в коде, используй `return`:

```python
def word_count(text):
    return len(text.split())

count = word_count("hello world")
print(count)
```

### print() vs return
- `print()` — только показывает на экране.
- `return` — отдаёт значение, чтобы его можно было использовать дальше.

### Шаг 5: модуль как другой `.py` файл
`text_utils.py` хранит функции, `run_text_utils.py` их использует через импорт.

### Шаг 6: `if __name__ == "__main__"` (очень коротко)
Этот блок запускается, когда файл стартует напрямую.

## Runnable example
`text_utils.py`:

```python
def word_count(text):
    return len([part for part in text.split() if part.strip()])


def normalize_spaces(text):
    return " ".join(text.split())
```

`run_text_utils.py`:

```python
from text_utils import word_count, normalize_spaces


def main():
    raw = input("Введите строку: ")
    normalized = normalize_spaces(raw)
    print(f"normalized={normalized}")
    print(f"words={word_count(normalized)}")


if __name__ == "__main__":
    main()
```

## Run and expected output
```bash
python run_text_utils.py
```

Expected output example:
- input: `Hello   world   from   python`
- output:
  - `normalized=Hello world from python`
  - `words=4`

## Частые ошибки
- Возвращают `print(...)` вместо значения через `return`.
- Пишут всю логику в одном файле и не используют `import`.
- Забывают, что модуль должен лежать в той же папке (или в `PYTHONPATH`).
- Не обрабатывают пустую строку и получают неожиданный результат.

Примечание: type hints можно добавить позже как optional улучшение, но это не обязательная часть первого решения.

## Как это связано с задачей
Task `foundation-functions-and-modules` проверяет, умеешь ли ты:
- выделить функции в модуль;
- импортировать их в entrypoint;
- получить воспроизводимый результат на разных входах.

Этот урок даёт минимальную структуру, которую можно напрямую перенести в решение.

## What to read (EN source)
- Sources использованы как backbone для этого урока.
- Optional deep dive:
  - Python MOOC: functions, parameters, return values.
  - Automate the Boring Stuff: reusable helper functions.
  - Python docs tutorial: modules basics.

Дополнительная ссылка (опционально):
- https://docs.python.org/3/tutorial/modules.html

## What to skip
- Полная теория packaging и публикация на PyPI.
- Сложные темы про import hooks и internals.

## Action
Сделай два файла:
- `text_utils.py`
- `run_text_utils.py`

В `text_utils.py` реализуй функции:
1. `word_count(text: str) -> int`
2. `char_count(text: str) -> int`
3. `normalize_spaces(text: str) -> str`

В `run_text_utils.py`:
- импортируй функции из `text_utils.py`;
- обработай строку из `input()`;
- выведи количество слов, символов и нормализованную строку.

## Optional media
> Placeholder for embedded video:  
> topic: Python functions, return vs print, modules and import  
> usage: optional explanation, not required for completion

## Definition of Done
- Логика вынесена в функции, а не написана целиком в одном файле.
- `run_text_utils.py` корректно использует `import`.
- Функции возвращают значения, а не только печатают их.
- На пустой строке скрипт не падает.

## Technical English
- **function** — функция: переиспользуемый блок кода.
- **parameter** — параметр: вход функции.
- **return value** — возвращаемое значение: результат, который функция отдаёт наружу.
- **module** — модуль: `.py` файл с кодом, который можно импортировать.
- **import** — импорт: подключение кода из другого модуля.
- **entrypoint** — точка входа: файл/функция, с которых запускается сценарий.
